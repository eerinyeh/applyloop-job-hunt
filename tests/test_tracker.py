import datetime as dt
import importlib.util
from pathlib import Path
import tempfile
import unittest
import json
from xlsx_fixture import write_fixture

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('tracker', ROOT/'skills/uk-job-search/scripts/tracker.py')
tracker = importlib.util.module_from_spec(spec); spec.loader.exec_module(tracker)


class WorkflowTests(unittest.TestCase):
    def test_duplicate_url_preserves_requisition_query(self):
        rows = [{'Application ID':'A','Company':'Acme','Job title':'Designer','Advert URL':'https://jobs.example/job?id=1&utm_source=linkedin','Requisition ID':'R1'}]
        self.assertTrue(tracker.duplicates(rows,'ACME','designer','https://jobs.example/job?id=1&trk=feed')[0]['exact'])
        self.assertFalse(tracker.duplicates(rows,'Acme','Designer','https://jobs.example/job?id=2', 'R2')[0]['exact'])
        self.assertEqual(tracker.duplicates(rows,'Acme','Other role','','R2'),[])
        self.assertFalse(tracker.duplicates(rows,'Acme','Different vacancy','https://jobs.example/job?id=1')[0]['exact'])

    def test_progression_survives_rejection_and_drafts_excluded(self):
        rows = [
            {'Applied date':'2026-10-02','First progressed date':'2026-10-05','Status':'Rejected','Category':'Operations','Priority':4},
            {'Applied date':'2026-10-31','First progressed date':'','Status':'No response (inferred)','Category':'Operations','Priority':3},
            {'Applied date':'2026-11-01','First progressed date':'','Status':'Applied','Category':'Product','Priority':4},
            {'Applied date':'','First progressed date':'','Status':'Draft','Category':'Operations','Priority':5}]
        result=tracker.statistics(rows,dt.date(2026,10,1),dt.date(2026,11,1))['overall']
        self.assertEqual(result['applications'],2)
        self.assertEqual(result['conversion_rate'],0.5)
        self.assertEqual(result['rejection_rate'],0.5)
        self.assertEqual(result['no_response_inferred'],1)
        self.assertIsNone(tracker.statistics([],dt.date(2026,10,1),dt.date(2026,11,1))['overall']['conversion_rate'])

    def test_character_limits_include_unicode_and_newlines(self):
        self.assertEqual(tracker.answer_check('one\ntwo')['characters'],7)
        self.assertFalse(tracker.answer_check('😀',chars=1)['within_limit'])
        self.assertTrue(tracker.answer_check('one two',words=2,chars=7)['within_limit'])

    def test_unknown_evidence_blocked_but_semantic_review_required(self):
        bank={'records':[{'id':'project.one'}]}
        self.assertFalse(tracker.claim_check(bank,{'claims':[{'text':'Claim','evidence_ids':['project.two']} ]})['references_valid'])
        r=tracker.claim_check(bank,{'claims':[{'text':'Claim','evidence_ids':['project.one']} ]})
        self.assertTrue(r['references_valid']); self.assertTrue(r['semantic_review_required'])

    def test_failed_or_unknown_gate_cannot_create_packet(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'decision.json';p.write_text('{"priority":4,"eligibility":"verify"}')
            workbook=Path(d)/'Applications.xlsx'
            write_fixture(workbook)
            with self.assertRaises(ValueError):
                tracker.main(['--project',d,'--workbook',str(workbook),'prepare','--company','Fictional',
                              '--title','Example','--category','Operations','--jd',str(p),'--decision',str(p)])
            self.assertFalse((Path(d)/'private/jobs').exists())

    def test_reader_accepts_empty_workbook(self):
        with tempfile.TemporaryDirectory() as d:
            workbook=Path(d)/'Applications.xlsx'
            write_fixture(workbook)
            self.assertEqual(tracker.read_xlsx(workbook),[])

    def test_reader_roundtrips_dates_and_rejects_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as d:
            workbook=Path(d)/'Applications.xlsx'
            row={'Application ID':'APP-EXAMPLE001','Company':'Example & Company',
                 'Job title':'Coordinator','Applied date':46300,'Status':'Applied'}
            write_fixture(workbook,[row])
            saved=tracker.read_xlsx(workbook)[0]
            self.assertEqual(saved['Applied date'],'2026-10-05')
            self.assertEqual(saved['Company'],'Example & Company')
            write_fixture(workbook,[row,row])
            with self.assertRaisesRegex(ValueError,'Duplicate Application IDs'):
                tracker.read_xlsx(workbook)

    def test_distinct_possible_duplicate_needs_saved_review(self):
        with tempfile.TemporaryDirectory() as d:
            project=Path(d); (project/'private').mkdir()
            workbook=project/'private/Applications.xlsx'
            write_fixture(workbook,[{'Application ID':'APP-EXAMPLE001','Company':'Example',
                'Job title':'Coordinator','Requisition ID':'OLD-1','Status':'Applied'}])
            (project/'private/config.json').write_text(json.dumps({'categories':['Operations'],
                'onboarding_status':'directions_confirmed','non_negotiables':[]}))
            decision=project/'decision.json'
            decision.write_text(json.dumps({'priority':4,'eligibility':'pass',
                'gates':[{'status':'pass','requirement':'Paid role','basis':'Synthetic full advert'}],
                'rationale':'Synthetic eligible coordination role'}))
            jd=project/'jd.txt';jd.write_text('Synthetic distinct vacancy NEW-2, paid coordination role.')
            args=['--project',d,'prepare','--company','Example','--title','Coordinator',
                '--category','Operations','--requisition','NEW-2','--jd',str(jd),'--decision',str(decision)]
            with self.assertRaisesRegex(ValueError,'possible duplicate'):
                tracker.main(args)
            review=project/'review.json'
            review.write_text(json.dumps([{'id':'APP-EXAMPLE001','outcome':'distinct',
                'basis':'Compared saved OLD-1 advert with supplied NEW-2 advert; different employer requisitions.'}]))
            tracker.main(args+['--duplicate-review',str(review)])
            contexts=list((project/'private/jobs').glob('*/context.json'))
            self.assertEqual(len(contexts),1)
            self.assertEqual(json.loads(contexts[0].read_text())['duplicate_review'],json.loads(review.read_text()))
            with self.assertRaisesRegex(ValueError,'Exact duplicate'):
                tracker.main(args+['--duplicate-review',str(review)])

    def test_exact_duplicate_and_incomplete_reviews_remain_blocked(self):
        with self.assertRaisesRegex(ValueError,'Exact duplicate'):
            tracker.review_duplicates([{'id':'APP-EXAMPLE001','exact':True}],
                [{'id':'APP-EXAMPLE001','outcome':'distinct','basis':'Attempted override'}])
        for review in ([],[{'id':'wrong','outcome':'distinct','basis':'No match'}],
                       [{'id':'APP-EXAMPLE001','outcome':'distinct','basis':' '}],
                       [{'id':'APP-EXAMPLE001','outcome':'duplicate','basis':'Same role'}]):
            with self.subTest(review=review), self.assertRaises(ValueError):
                tracker.review_duplicates([{'id':'APP-EXAMPLE001','exact':False}],review)


if __name__=='__main__': unittest.main()
