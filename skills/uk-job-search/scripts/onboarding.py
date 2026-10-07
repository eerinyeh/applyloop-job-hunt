#!/usr/bin/env python3
"""Persist agent-assisted intake and confirmed directions. Python stdlib only."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

SECTIONS = ['education', 'work_experience', 'side_projects', 'skills', 'volunteer', 'training', 'languages', 'other']


def write_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def validate_constraints(rules):
    if not isinstance(rules, list):
        raise ValueError('non_negotiables must be a list')
    ids = []
    for rule in rules:
        if not isinstance(rule, dict) or not rule.get('id') or not rule.get('user_wording'):
            raise ValueError('Every hard constraint needs an ID and exact user wording')
        ids.append(rule['id'])
    if len(ids) != len(set(ids)):
        raise ValueError('Hard constraint IDs must be unique')


def initialise(project, intake):
    private = project / 'private'
    if any((private / f).exists() for f in ('intake.json', 'config.json', 'evidence_bank.json')):
        raise ValueError('An existing candidate workspace must be reviewed/merged, not reinitialised')
    profile = intake.get('profile', {})
    if not isinstance(profile, dict):
        raise ValueError('profile must be an object')
    search = intake.get('search', {})
    if not isinstance(search, dict):
        raise ValueError('search must be an object')
    rules = search.get('non_negotiables', [])
    validate_constraints(rules)
    records = []
    for section in SECTIONS:
        entries = intake.get(section, [])
        if not isinstance(entries, list):
            raise ValueError(section + ' must be a list; the agent maps narrative into it')
        for i, item in enumerate(entries, 1):
            if not isinstance(item, (str, dict)) or not item:
                raise ValueError('Each experience/skill entry must contain supplied facts')
            records.append({'id': f'{section}.{i}', 'facts': item, 'source': f'User intake: {section} entry {i}',
                            'verification_status': 'candidate_supplied'})
    raw = intake.get('raw_experience', '')
    if raw:
        records.append({'id': 'user.raw', 'facts': raw, 'source': 'Detailed user narrative',
                        'verification_status': 'candidate_supplied; agent must separate contexts before drafting'})
    for record in intake.get('extracted_cv_records', []):
        if not all(record.get(k) for k in ('id', 'facts', 'source')):
            raise ValueError('Extracted CV records require ID, facts and source')
        records.append(dict(record, verification_status=record.get('verification_status', 'candidate_supplied_cv')))
    if not records and not intake.get('base_cv_sources'):
        raise ValueError('Supply a base CV source or detailed experience before starting')
    ids = [r['id'] for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError('Evidence IDs must be unique')
    config = {'onboarding_status': 'intake_saved', 'tracker': 'private/Applications.xlsx',
              'evidence': 'private/evidence_bank.json', 'categories': [], 'directions': [],
              'requested_categories': search.get('requested_categories', []),
              'requested_titles': search.get('requested_titles', []),
              'preferred_responsibilities': search.get('preferred_responsibilities', []),
              'lower_preference': search.get('lower_preference', []), 'non_negotiables': rules,
              'search_notes': search.get('notes', ''), 'base_index': 'private/base_cvs/index.json',
              'cv_style': {'style': 'consulting_banking', 'body_font_pt': 11, 'early_career_pages': 1},
              'current_work_permission': {'status': 'unknown', 'expiry': None},
              'future_route': {'status': 'unknown', 'expiry': None}}
    bank = {'profile': profile, 'records': records, 'sources': intake.get('base_cv_sources', []),
            'claim_boundaries': ['Do not invent claims, measurements, qualifications or proficiency',
                                 'Keep dates, roles, individual/team attribution and project contexts separate'],
            'created_at': timestamp()}
    write_new(private / 'intake.json', intake)
    write_new(private / 'evidence_bank.json', bank)
    write_new(private / 'config.json', config)
    return {'status': 'intake_saved', 'records': len(records),
            'next': 'Extract any uploaded CV and review facts/preferences; propose evidence-linked directions for user confirmation'}


def propose(project, directions):
    private = project / 'private'
    config = json.loads((private / 'config.json').read_text())
    if config.get('onboarding_status') == 'directions_confirmed':
        raise ValueError('Existing confirmed directions need a reviewed change, not replacement by proposals')
    bank = json.loads((private / 'evidence_bank.json').read_text())
    evidence_ids = {r['id'] for r in bank['records']}
    if not isinstance(directions, list) or not directions:
        raise ValueError('Supply proposed directions')
    ids, names = [], []
    for d in directions:
        if not all(d.get(k) for k in ('id', 'category', 'example_titles', 'basis')):
            raise ValueError('Each proposed direction needs ID, category, title examples and evidence-linked basis')
        if d.get('origin') not in ('requested', 'recommended'):
            raise ValueError('Identify requested versus recommended directions')
        for b in d['basis']:
            if b.get('evidence_id') not in evidence_ids or not b.get('capability') or not b.get('role_link'):
                raise ValueError('Every recommendation basis needs a known evidence ID, capability and role link')
        ids.append(d['id']); names.append(d['category'].casefold())
    if len(ids) != len(set(ids)) or len(names) != len(set(names)):
        raise ValueError('Direction IDs and categories must be unique')
    dest = private / 'directions.proposed.json'
    dest.write_text(json.dumps({'proposed_at': timestamp(), 'directions': directions,
                                'non_negotiables': config.get('non_negotiables', [])}, indent=2))
    return {'status': 'awaiting_user_confirmation', 'proposal': str(dest),
            'categories_activated': False, 'base_cvs_created': False}


def confirm(project, reply):
    private = project / 'private'
    config = json.loads((private / 'config.json').read_text())
    if config.get('onboarding_status') == 'directions_confirmed':
        raise ValueError('Directions already confirmed; review later changes explicitly')
    if not reply.get('user_confirmation') or not reply.get('direction_ids'):
        raise ValueError('Record the actual user confirmation and selected direction IDs')
    proposed = json.loads((private / 'directions.proposed.json').read_text())
    lookup = {d['id']: d for d in proposed['directions']}
    selected = reply['direction_ids']
    if len(selected) != len(set(selected)) or any(i not in lookup for i in selected):
        raise ValueError('Select unique IDs from the proposals; revise proposals for new directions')
    if (private / 'Applications.xlsx').exists():
        raise ValueError('Review tracker category migration before changing directions in a workbook workspace')
    config['directions'] = [lookup[i] for i in selected]
    config['categories'] = [lookup[i]['category'] for i in selected]
    config['preferred_categories'] = list(config['categories'])
    config['onboarding_status'] = 'directions_confirmed'
    config['confirmation'] = {'user_reply': reply['user_confirmation'], 'confirmed_at': timestamp()}
    config_path = private / 'config.json'
    write_new(private / ('config-before-confirmation-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f') + '.json'),
              json.loads(config_path.read_text()))
    config_path.write_text(json.dumps(config, indent=2))
    return {'status': 'directions_confirmed', 'categories': config['categories'],
            'next': 'Agent creates and verifies one base CV per confirmed category, then builds the tracker from this config'}


def check_salary(threshold, minimum=None, maximum=None, operator='>', comparable=True):
    if not comparable or minimum is None and maximum is None:
        return 'verify'
    if minimum is not None and maximum is not None and maximum < minimum:
        raise ValueError('Salary range maximum cannot be below minimum')
    if operator not in ('>', '>='):
        raise ValueError('Choose > or >=')
    if minimum is not None and (minimum > threshold if operator == '>' else minimum >= threshold):
        return 'pass'
    if maximum is not None and (maximum <= threshold if operator == '>' else maximum < threshold):
        return 'fail'
    return 'verify'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path, default=Path.cwd())
    sub = p.add_subparsers(dest='command', required=True)
    for cmd in ('init', 'propose', 'confirm'):
        s = sub.add_parser(cmd); s.add_argument('--input', type=Path, required=True)
    s = sub.add_parser('check-salary')
    s.add_argument('--threshold', type=float, required=True)
    s.add_argument('--minimum', type=float); s.add_argument('--maximum', type=float)
    s.add_argument('--operator', choices=['>', '>='], default='>')
    s.add_argument('--not-comparable', action='store_true')
    a = p.parse_args()
    if a.command == 'check-salary':
        result = {'assessment': check_salary(a.threshold, a.minimum, a.maximum, a.operator, not a.not_comparable),
                  'scope': 'Comparable annual guaranteed base pay only; source interpretation required'}
    else:
        data = json.loads(a.input.read_text())
        result = {'init': initialise, 'propose': propose, 'confirm': confirm}[a.command](a.project.resolve(), data)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(str(exc), file=sys.stderr); sys.exit(2)
