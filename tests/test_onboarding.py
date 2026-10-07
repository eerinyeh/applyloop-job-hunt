import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/f'skills/uk-job-search/scripts/{name}.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
onboarding=load('onboarding');tracker=load('tracker')


class UniversalWorkflowTests(unittest.TestCase):
    def intake(self):
        return {'profile':{'name':'Example Candidate'},
                'work_experience':[{'organisation':'Example School','contribution':'Coordinated timetables and communicated with families'}],
                'search':{'requested_titles':['Programme Coordinator'],
                          'non_negotiables':[{'id':'paid','user_wording':'Paid roles only'}]}}

    def test_directions_stay_provisional_until_real_confirmation_record(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);onboarding.initialise(p,self.intake())
            directions=[{'id':'coordination','category':'Programme Coordination','example_titles':['Programme Coordinator'],
                         'origin':'requested','basis':[{'evidence_id':'work_experience.1','capability':'Timetable coordination',
                                                       'role_link':'Scheduling and stakeholder communication'}]}]
            onboarding.propose(p,directions)
            config=json.loads((p/'private/config.json').read_text())
            self.assertEqual(config['categories'],[])
            self.assertFalse((p/'private/base_cvs').exists())
            with self.assertRaises(ValueError):onboarding.confirm(p,{'direction_ids':['coordination']})
            onboarding.confirm(p,{'direction_ids':['coordination'],'user_confirmation':'Keep Programme Coordination; paid only is correct.'})
            config=json.loads((p/'private/config.json').read_text())
            self.assertEqual(config['categories'],['Programme Coordination'])
            self.assertEqual(config['non_negotiables'][0]['id'],'paid')

    def test_cv_only_intake_requires_extraction_before_recommendation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);onboarding.initialise(p,{'base_cv_sources':['private/uploaded_cv.docx']})
            self.assertEqual(json.loads((p/'private/evidence_bank.json').read_text())['records'],[])
            with self.assertRaises(ValueError):
                onboarding.propose(p,[{'id':'sales','category':'Sales','example_titles':['Sales Associate'],
                                      'origin':'recommended','basis':[{'evidence_id':'invented','capability':'Closing', 'role_link':'Sales'}]}])

    def test_existing_profile_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);onboarding.initialise(p,self.intake())
            before=(p/'private/evidence_bank.json').read_bytes()
            with self.assertRaises(ValueError):onboarding.initialise(p,{'raw_experience':'Different person'})
            self.assertEqual(before,(p/'private/evidence_bank.json').read_bytes())

    def test_strict_base_salary_threshold_and_unknowns(self):
        self.assertEqual(onboarding.check_salary(30000,30000,30000),'fail')
        self.assertEqual(onboarding.check_salary(30000,30000,30000,'>='),'pass')
        self.assertEqual(onboarding.check_salary(30000,28000,35000),'verify')
        self.assertEqual(onboarding.check_salary(30000,31000,35000),'pass')
        self.assertEqual(onboarding.check_salary(30000,None,None),'verify')
        self.assertEqual(onboarding.check_salary(30000,35000,35000,comparable=False),'verify')

    def test_hard_constraints_block_packets_independent_of_fit(self):
        cfg={'non_negotiables':[{'id':'paid','user_wording':'Paid roles only'}]}
        for decision in [{'priority':5}, {'priority':5,'constraint_assessments':[{'id':'paid','status':'verify','basis':'No pay information'}]},
                         {'priority':5,'constraint_assessments':[{'id':'paid','status':'fail','basis':'Advert says unpaid'}]}]:
            with self.assertRaises(ValueError):tracker.check_constraints(cfg,decision)
        tracker.check_constraints(cfg,{'priority':5,'constraint_assessments':[{'id':'paid','status':'pass','basis':'Advert confirms paid employment'}]})


if __name__=='__main__':unittest.main()
