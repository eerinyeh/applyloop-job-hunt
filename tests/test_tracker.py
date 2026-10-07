import datetime as dt
import importlib.util
from pathlib import Path
import tempfile
import unittest

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
            # Use the actual empty template when available; failure must precede any packet creation.
            workbook=ROOT/'private/Applications.xlsx'
            if not workbook.exists(): self.skipTest('Template not built')
            with self.assertRaises(ValueError):
                tracker.main(['--project',d,'--workbook',str(workbook),'prepare','--company','Fictional',
                              '--title','Example','--category','Operations','--jd',str(p),'--decision',str(p)])
            self.assertFalse((Path(d)/'private/jobs').exists())

    def test_empty_delivered_workbook_has_no_fictional_records(self):
        workbook=ROOT/'private/Applications.xlsx'
        if not workbook.exists(): self.skipTest('Template not built')
        self.assertEqual(tracker.read_xlsx(workbook),[])


if __name__=='__main__': unittest.main()
