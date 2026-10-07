# Validation results

Checked on 7 October 2026, starting from a fresh clone of published commit `2b79c30579ff3c65193699ead4f64cfae0080e89`.

The core application-preparation and tracking route worked with fictional candidate data in Codex desktop. This is a tested prototype, with live integrations and additional entry routes still requiring validation. No real application was submitted and no mailbox messages were read.

## Checks actually executed

| Area | Observed result |
| --- | --- |
| Typed-experience onboarding | Saved only the fictional candidate; directions stayed provisional until the supplied user confirmation; activated two chosen categories. |
| Hard constraints and priority | Routine Jira familiarity remained a supporting gap at priority 4. A staff backend role was priority 1 and refused preparation. Missing salary/location held the other role. Strict base-pay comparison, unknown eligibility and hard-constraint refusal passed helper tests. |
| Documents | Two category bases and one tailored editable DOCX were generated, rendered and visually inspected: one page each, 11pt body, native paragraphs/bullets. No invented Jira use, metrics or employer facts. |
| Form questions | Saved role context produced a separate-chat prompt; the answer was 72 of 100 allowed words, with valid evidence IDs. This did not execute a real handoff between two user chats. |
| Empty tracker | Builder exported an empty XLSX using the fictional candidate's categories. All three sheets were rendered. In-memory input-change checks exercised cohort rates and matching/no-match search. |
| Saved tracker updates | Draft, Ready, Applied, Interview, Rejected and Assessment updates were written, exported and re-read. Drafts had no application date; confirmation alone did not create progression; first progression survived rejection. |
| Synthetic deadline scenario | An explicit calendar-day cutoff was recorded; a simulated complete no-later-reply check allowed a labelled no-response inference after the cutoff; a synthetic late assessment reply restored the active status. These were source-backed fixture patches, not an automated email-classifier or live inbox test. |
| Workbook consistency | Invalid submission dates, calendar dates and progression erasure were refused without changing the workbook bytes. Five valid update batches created five backups and source logs. Saved OOXML retained native validation, table and formulas; formula-like notes stayed text. |
| Calculations after saved updates | Reimport/recalculation showed two submitted applications, two ever progressed, one confirmed rejection, one draft and no remaining inferred silence. Saved search found the expected application ID. Rendered results were visually inspected. |
| Python suite | Published snapshot: 11 tests, nine passed and two skipped due to a private-workbook dependency. Revised suite: 14 passed, zero skipped, using synthetic reader fixtures. |

## Defects found and corrected

1. Possible company/title duplicates could be inspected as genuinely different vacancies but `prepare` still refused them. An explicit private, evidence-based `--duplicate-review` now permits only reviewed possible matches. Exact duplicates remain blocked, and the review is retained in the new packet. Successful distinct-role preparation and failed exact-duplicate override were tested.
2. The twice-weekly periods began on 5 October, omitting 1–4 October. New tracker periods start on the Monday on/before the opening month, with an input-change check that opening-month applications are counted. Reporting now starts in the creation month instead of being permanently anchored to October 2026. The revised builder ran successfully and its exported empty workbook was re-read/rendered.
3. Two tests silently skipped on a clean download because private files were excluded. They now use a synthetic OOXML reader fixture. This fixture does not substitute for the separately executed real workbook builder/updater checks.

These source changes do not rebuild or migrate an existing populated tracker. Existing reporting ranges require a reviewed edit if they need the corrected dates.

## Still requiring a live or additional test

- **Gmail and recurring runs:** the connected account differed from the configured target. No message search or read was attempted. A matching account, a verified tracked application and a successful scheduled run are needed before claiming automatic sync. No live pagination, watermark recovery, message deduplication, ambiguity resolution or no-response inference has been verified.
- **Existing-tracker import:** the documented route is an agent-assisted migration, not a generic import command. A real legacy XLSX/CSV migration, unresolved history and category changes have not been tested.
- **Uploaded CV intake:** helper tests verify that a CV-only intake needs extraction before recommendations; an end-to-end PDF/DOCX upload and extraction session was not exercised in this pass. The full practical onboarding pass used typed experience.
- **Native Excel interaction:** exported formulas, validations and renders were inspected through Codex tooling. Dropdown/filter behaviour and manual edits were not exercised in the user's Microsoft Excel version. Simultaneous writers and interrupted export recovery were not stress-tested; follow the single-writer rule.
- **Other platforms:** unchanged full compatibility with ChatGPT, Claude or Claude Code has not been established. The workbook authoring helpers require Codex's bundled spreadsheet runtime. Capacity above 1,000 rows is not implemented without extending ranges.
- **Human judgement:** evidence IDs validate references, not the truth of prose. CV claims, role eligibility, duplicate-review evidence and email interpretation still require the agent's source review. Test adverts and confirmations were fictional.

## Reproduce the deterministic helper checks

From a fresh extracted project folder, with Python 3.10 or newer:

```sh
python3 -m unittest discover -s tests -v
```

For real workbook/document checks, use Codex's spreadsheet/document skills and bundled dependencies. Create an isolated fictional candidate workspace, confirm directions, build an empty tracker, prepare a qualifying advert, add a Draft row, then apply source-backed status patches and re-read the saved rows. Render the workbook and documents. Keep all generated candidate files private and out of public commits.
