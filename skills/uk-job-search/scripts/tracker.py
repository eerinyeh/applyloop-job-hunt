#!/usr/bin/env python3
"""Read-only XLSX utilities and private per-role packets. Python 3.10+, stdlib only."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import sys
import uuid
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import xml.etree.ElementTree as ET
import zipfile

NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
COLS = ['Application ID', 'Company', 'Job title', 'Category', 'Priority', 'Status',
        'Applied date', 'Advert URL', 'Location', 'Next action', 'Due date',
        'First progressed date', 'Updated date', 'Notes', 'Requisition ID', 'Search match']


def norm(value):
    return ' '.join(re.findall(r'\w+', str(value).casefold()))


def canonical_url(value):
    if not value:
        return ''
    u = urlsplit(value)
    query = [(k, v) for k, v in parse_qsl(u.query, keep_blank_values=True)
             if not k.lower().startswith('utm_') and k.lower() not in
             {'trk', 'trackingid', 'ref', 'source', 'refid', 'lipi'}]
    return urlunsplit((u.scheme.lower(), u.netloc.lower(), u.path.rstrip('/'),
                      urlencode(sorted(query)), ''))


def _date(value):
    if value in ('', None):
        return None
    if isinstance(value, (int, float)):
        return (dt.datetime(1899, 12, 30) + dt.timedelta(days=value)).date()
    return dt.date.fromisoformat(str(value)[:10])


def read_xlsx(path):
    """Read data cells only. Formula caches are never used for decision fields."""
    with zipfile.ZipFile(path) as z:
        workbook = ET.fromstring(z.read('xl/workbook.xml'))
        props = workbook.find('s:workbookPr', NS)
        if props is not None and props.get('date1904') in ('1', 'true'):
            raise ValueError('1904 date-system workbooks require conversion before import')
        rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        targets = {r.get('Id'): r.get('Target') for r in rels}
        sheet = next((s for s in workbook.findall('s:sheets/s:sheet', NS)
                      if s.get('name') == 'Applications'), None)
        if sheet is None:
            raise ValueError('Applications sheet not found; use the supplied workbook')
        target = targets[sheet.get('{'+NS['r']+'}id')]
        target = target.lstrip('/') if target.startswith('/') else 'xl/' + target
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si', NS):
                strings.append(''.join(t.text or '' for t in si.iter('{'+NS['s']+'}t')))
        data = []
        headers = None
        for row in ET.fromstring(z.read(target)).findall('s:sheetData/s:row', NS):
            cells = {}
            for c in row.findall('s:c', NS):
                col = re.match('[A-Z]+', c.get('r')).group()
                t = c.get('t')
                v = c.find('s:v', NS)
                value = v.text if v is not None else ''
                if t == 's':
                    value = strings[int(value)]
                elif t == 'inlineStr':
                    value = ''.join(t.text or '' for t in c.iter('{'+NS['s']+'}t'))
                elif t not in ('str', 'd', 'e') and value:
                    value = float(value)
                    if value.is_integer():
                        value = int(value)
                # Do not trust formulas as editable source data (except the search helper).
                if c.find('s:f', NS) is not None and col != 'P':
                    value = ''
                cells[col] = value
            if cells.get('A') == 'Application ID':
                headers = {k: v for k, v in cells.items()}
                if any(name not in headers.values() for name in COLS[:-1]):
                    raise ValueError('Required tracker columns are missing')
                continue
            if headers and cells.get('A'):
                item = {name: cells.get(col, '') for col, name in headers.items()}
                for name in ['Applied date', 'Due date', 'First progressed date', 'Updated date']:
                    d = _date(item.get(name))
                    item[name] = d.isoformat() if d else ''
                data.append(item)
        if headers is None:
            raise ValueError('Application header row not found')
        ids = [x['Application ID'] for x in data]
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate Application IDs; resolve before automated updates')
        return data


def duplicates(rows, company, title, url='', requisition=''):
    out = []
    for r in rows:
        reasons = []
        if url and canonical_url(url) == canonical_url(r.get('Advert URL', '')):
            conflicting_req = requisition and r.get('Requisition ID') and str(requisition).casefold() != str(r['Requisition ID']).casefold()
            if norm(company) == norm(r.get('Company', '')) and norm(title) == norm(r.get('Job title', '')) and not conflicting_req:
                reasons.append('same advert URL and company/title')
            else:
                reasons.append('possible duplicate: shared URL; inspect actual advert/requisition')
        if requisition and norm(company) == norm(r.get('Company', '')) and \
                str(requisition).strip().casefold() == str(r.get('Requisition ID', '')).strip().casefold():
            reasons.append('same company and requisition')
        same_title = norm(company) == norm(r.get('Company', '')) and norm(title) == norm(r.get('Job title', ''))
        if same_title and not reasons:
            reasons.append('possible duplicate: company and title; inspect requisitions')
        if reasons:
            out.append({'id': r['Application ID'], 'reasons': reasons,
                        'status': r.get('Status', ''), 'exact': any(not x.startswith('possible') for x in reasons)})
    return out


def packet_rows(project):
    rows = []
    for p in (project / 'private/jobs').glob('*/context.json'):
        c = json.loads(p.read_text())
        rows.append({'Application ID': c['application_id'], 'Company': c['company'],
                     'Job title': c['title'], 'Advert URL': c['url'],
                     'Requisition ID': c.get('requisition', ''), 'Status': 'Packet created'})
    return rows


def review_duplicates(matches, review):
    """Permit inspected possible matches, preserving the distinction and its basis."""
    if any(m['exact'] for m in matches):
        raise ValueError('Exact duplicate cannot be overridden: ' + json.dumps(matches))
    if not isinstance(review, list) or not review:
        raise ValueError('Possible duplicates require an evidenced review for each matched ID')
    ids = [r.get('id') for r in review if isinstance(r, dict)]
    if len(ids) != len(review) or len(ids) != len(set(ids)) or set(ids) != {m['id'] for m in matches}:
        raise ValueError('Duplicate review must cover exactly the possible matched IDs once each')
    if any(r.get('outcome') != 'distinct' or not isinstance(r.get('basis'), str) or not r['basis'].strip()
           for r in review):
        raise ValueError('Each duplicate review requires outcome distinct and a verified basis')
    return review


def statistics(rows, start, end):
    chosen = [r for r in rows if r.get('Applied date') and start <= _date(r['Applied date']) < end]
    def measure(group):
        n = len(group)
        advanced = sum(bool(r.get('First progressed date')) for r in group)
        rejected = sum(r.get('Status') == 'Rejected' for r in group)
        return {'applications': n, 'progressed': advanced, 'rejected': rejected,
                'conversion_rate': advanced / n if n else None,
                'rejection_rate': rejected / n if n else None,
                'no_response_inferred': sum(r.get('Status') == 'No response (inferred)' for r in group)}
    result = {'start_inclusive': start.isoformat(), 'end_exclusive': end.isoformat(),
              'overall': measure(chosen), 'categories': {}, 'priorities': {}}
    for field, key in [('Category', 'categories'), ('Priority', 'priorities')]:
        for name in sorted(set(str(r[field]) for r in chosen)):
            result[key][name] = measure([r for r in chosen if str(r[field]) == name])
    return result


def answer_check(text, words=None, chars=None):
    result = {'words': len(text.split()), 'characters': len(text),
              'utf16_characters': len(text.encode('utf-16-le')) // 2}
    result['within_limit'] = (words is None or result['words'] <= words) and \
        (chars is None or max(result['characters'], result['utf16_characters']) <= chars)
    return result


def claim_check(bank, mapping):
    allowed = {r['id'] for r in bank['records']}
    errors = []
    claims = mapping.get('claims', [])
    if not claims:
        errors.append('No claims supplied')
    for i, claim in enumerate(claims, 1):
        if not claim.get('text') or not claim.get('evidence_ids'):
            errors.append(f'Claim {i}: text and evidence_ids required')
        for ref in claim.get('evidence_ids', []):
            if ref not in allowed:
                errors.append(f'Claim {i}: unknown evidence ID {ref}')
    return {'references_valid': not errors, 'errors': errors,
            'semantic_review_required': True, 'claims': len(claims)}


def check_constraints(config, decision):
    rules = config.get('non_negotiables', [])
    assessments = decision.get('constraint_assessments', [])
    ids = [a.get('id') for a in assessments]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate hard-constraint assessments')
    lookup = {a.get('id'): a for a in assessments}
    for rule in rules:
        a = lookup.get(rule['id'], {})
        if a.get('status') != 'pass' or not a.get('basis'):
            raise ValueError('Non-negotiable not verified as passed: ' + rule['id'])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path.cwd())
    parser.add_argument('--workbook', type=Path)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('rows')
    p = sub.add_parser('search'); p.add_argument('query'); p.add_argument('--category')
    p = sub.add_parser('duplicates')
    p.add_argument('--company', required=True); p.add_argument('--title', required=True)
    p.add_argument('--url', default=''); p.add_argument('--requisition', default='')
    p = sub.add_parser('stats'); p.add_argument('--start', required=True); p.add_argument('--end', required=True)
    p = sub.add_parser('prepare')
    for field in ('company', 'title', 'category', 'jd', 'decision'):
        p.add_argument('--'+field, required=True)
    p.add_argument('--url', default=''); p.add_argument('--requisition', default='')
    p.add_argument('--duplicate-review', type=Path)
    p = sub.add_parser('questions'); p.add_argument('--id', required=True); p.add_argument('--input', type=Path, required=True)
    p = sub.add_parser('check-answer'); p.add_argument('file', type=Path)
    p.add_argument('--words', type=int); p.add_argument('--chars', type=int)
    p = sub.add_parser('check-claims'); p.add_argument('file', type=Path)
    p = sub.add_parser('email-match'); p.add_argument('file', type=Path)
    args = parser.parse_args(argv)
    project = args.project.resolve()
    path = args.workbook or project / 'private/Applications.xlsx'
    if args.command in ('rows', 'search', 'duplicates', 'stats', 'prepare', 'email-match'):
        if not path.exists():
            raise ValueError(f'Tracker missing: {path}; create it before checking duplicates')
        rows = read_xlsx(path)
    if args.command == 'rows':
        result = rows
    elif args.command == 'search':
        terms = norm(args.query).split()
        result = [r for r in rows if all(t in norm(' '.join(str(v) for v in r.values())) for t in terms)
                  and (not args.category or norm(r['Category']) == norm(args.category))]
    elif args.command == 'duplicates':
        result = duplicates(rows + packet_rows(project), args.company, args.title, args.url, args.requisition)
    elif args.command == 'stats':
        start, end = dt.date.fromisoformat(args.start), dt.date.fromisoformat(args.end)
        if end <= start:
            raise ValueError('End must be after start (end is exclusive)')
        result = statistics(rows, start, end)
    elif args.command == 'prepare':
        matches = duplicates(rows + packet_rows(project), args.company, args.title, args.url, args.requisition)
        # A tracker row and its packet share an ID; review that application once.
        unique_matches = {}
        for match in matches:
            if match['id'] not in unique_matches or match['exact']:
                unique_matches[match['id']] = match
        matches = list(unique_matches.values())
        duplicate_review = []
        if matches:
            if not args.duplicate_review:
                raise ValueError('Duplicate or possible duplicate: inspect before drafting: ' + json.dumps(matches))
            duplicate_review = review_duplicates(matches, json.loads(args.duplicate_review.read_text()))
        elif args.duplicate_review:
            raise ValueError('No duplicate candidates to review; omit --duplicate-review')
        decision = json.loads(Path(args.decision).read_text())
        priority = decision.get('priority')
        if decision.get('eligibility') != 'pass' or type(priority) is not int or priority not in (3, 4, 5):
            raise ValueError('Only eligibility pass and integer priority 3–5 create a packet')
        gates = decision.get('gates', [])
        if not gates or not all(g.get('status') == 'pass' and g.get('requirement') and g.get('basis') for g in gates):
            raise ValueError('Every eligibility gate requires pass, requirement and basis')
        if not decision.get('rationale'):
            raise ValueError('Decision rationale required')
        config = json.loads((project / 'private/config.json').read_text())
        if config.get('onboarding_status') and config['onboarding_status'] != 'directions_confirmed':
            raise ValueError('Complete user confirmation of search directions before creating application packets')
        check_constraints(config, decision)
        categories = config['categories']
        if args.category not in categories:
            raise ValueError('Use one configured category')
        jd = Path(args.jd).read_text()
        if not jd.strip():
            raise ValueError('Full job description is required')
        key = 'APP-' + uuid.uuid4().hex[:10].upper()
        dest = project / 'private/jobs' / key
        dest.mkdir(parents=True, exist_ok=False)
        (dest / 'jd.txt').write_text(jd)
        context = {'application_id': key, 'company': args.company, 'title': args.title,
                   'category': args.category, 'url': args.url, 'requisition': args.requisition,
                   'decision': decision, 'initial_status': 'Draft',
                   'captured_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                   'duplicate_review': duplicate_review,
                   'jd_sha256': hashlib.sha256(jd.encode()).hexdigest()}
        (dest / 'context.json').write_text(json.dumps(context, indent=2))
        result = {'id': key, 'packet': str(dest), 'next': 'Create Draft tracker row with this ID; do not mark applied'}
    elif args.command == 'questions':
        if not re.fullmatch(r'APP-[A-Z0-9]{10}', args.id):
            raise ValueError('Invalid application ID')
        dest = project / 'private/jobs' / args.id
        if not (dest / 'context.json').exists():
            raise ValueError('Role context not found')
        qs = json.loads(args.input.read_text())
        if not isinstance(qs, list) or not qs:
            raise ValueError('Supply a nonempty question list')
        for q in qs:
            if not isinstance(q, dict) or not q.get('question'):
                raise ValueError('Each question needs exact question text')
            for k in ('max_words', 'max_characters'):
                if k in q and (type(q[k]) is not int or q[k] <= 0):
                    raise ValueError('Limits must be positive integers')
        qpath = dest / ('questions-' + uuid.uuid4().hex[:8] + '.json')
        qpath.write_text(json.dumps(qs, indent=2))
        skill_path = Path(__file__).resolve().parents[1] / 'SKILL.md'
        result = {'questions_file': str(qpath), 'prompt':
                  f'Use the skill at {skill_path}. Answer the questions in {qpath} using {dest}/context.json, '
                  f'{dest}/jd.txt and {project}/private/evidence_bank.json. Apply the exact limits and map claims to evidence. '
                  'Do this now without waiting for the CV batch.'}
    elif args.command == 'check-answer':
        result = answer_check(args.file.read_text(), args.words, args.chars)
        if not result['within_limit']:
            print(json.dumps(result, indent=2)); return 2
    elif args.command == 'check-claims':
        result = claim_check(json.loads((project / 'private/evidence_bank.json').read_text()),
                             json.loads(args.file.read_text()))
        if not result['references_valid']:
            print(json.dumps(result, indent=2)); return 2
    else:
        email = norm(args.file.read_text())
        result = []
        for r in rows:
            req = norm(r.get('Requisition ID', ''))
            company, title = norm(r['Company']), norm(r['Job title'])
            if (req and req in email and company in email) or (company and company in email and title and title in email):
                result.append({'id': r['Application ID'], 'company': r['Company'], 'title': r['Job title']})
        result = {'candidates': result, 'verified': False, 'action': 'Verify role and message before updating; no status changed'}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
