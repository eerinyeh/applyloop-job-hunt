# ApplyLoop

For fewer “Which job was this again?” moments.

Turn a pasted job description into tailored CVs, cover letters and application answers grounded in your actual experience. Keep each role's context and application history together in an editable Excel tracker.

A Codex job-search skill for any candidate, with local Python helpers and an editable Excel tracker. It starts from an uploaded CV, detailed typed experience, or both; confirms search directions and non-negotiables; creates category base CVs; then assesses vacancies and prepares applications. Each vacancy has separate saved context so form questions can be answered during a CV batch.

The first version focuses on application preparation and records. You find and select openings, paste the JD, and submit through the employer portal yourself. Pasting a JD starts preparation, not submission. Share actual form questions and their limits as they appear, or explicitly share a form for inspection. Gmail tracking is a separately authorised connected-tool workflow; it does not require permission to submit applications or send emails.

## Start using it

Open this folder as a Codex project. New users can start with this prompt, then upload a base CV or type their background:

Use the extracted folder containing `README.md`, `skills/`, `tools/` and `examples/` as the project directory. Creating a new empty project does not copy these files. Start the onboarding chat in **Local** mode, working directly in that folder. An empty Git repository has no committed starting branch and cannot create a worktree (`fatal: invalid reference: main`). Local mode does not require a Git commit. It also keeps the private profile and tracker in one persistent project directory.

> Use the skill at skills/uk-job-search/SKILL.md to set up my job search. Gather my experience, desired categories/titles and non-negotiables. Suggest additional directions supported by my experience. Wait for me to confirm the directions and constraints, then create a consulting/banking-style base CV for each confirmed category and set up my tracker.

You can supply education, employment, projects, skills, volunteering, training, languages, name/location/contact details and optional LinkedIn, portfolio, GitHub or other links. Details already in a CV do not need to be retyped. The agent organises your evidence privately and asks only useful follow-up questions. You do not need to write JSON yourself.

Onboarding also offers an empty tracker or an existing XLSX/CSV import. Import is an agent-assisted migration: inspect the source, review column/category/status/date mappings and duplicate conflicts, then create/merge the new tracker while preserving the original. Unknown history stays unresolved rather than being invented. See [tracker import](skills/uk-job-search/references/tracker-import.md); a generic file-import CLI and real-file migration tests are not implemented.

Once setup is complete, use this prompt followed by your job descriptions:

> Use the skill at skills/uk-job-search/SKILL.md. Read my private config and evidence bank, check duplicates, classify these vacancies and prepare the appropriate applications. Follow my private workspace formatting instructions.

The skill source is provided in this folder; it is not installed into your global Codex skills directory. For current Codex local discovery, copy `skills/uk-job-search` into the project's `.agents/skills/` directory or use the skill installer with this repository and skill path. The private data stays in this project. Installed copies need this project's directory when invoked. Reading a skill file by its explicit path works without installing it.

## Distribution and platform support

Publish the contents of the public ZIP, not the entire working folder with private files. Downloading or cloning starts no process and grants no account access. A new user opens the extracted folder as a local Codex project, invokes the setup prompt above, supplies their profile/preferences and confirms directions. The agent then creates their private bases and tracker. Gmail connections and recurring schedules are set up separately for each user; your own connection and schedule are not distributed by GitHub.

Codex desktop is the initial supported environment because workbook helpers depend on its bundled artifact-tool runtime. The Python helpers use the standard library and can run in other local environments. Claude Code supports SKILL.md skills under `.claude/skills/`, so the drafting instructions are candidates for reuse, but this package has not been tested there. Excel authoring, document rendering, Gmail and schedules need platform-specific tooling or adapters. Regular ChatGPT/Claude chats can use supplied instructions and files for drafting, but uploading this repository alone does not establish a persistent local-file workflow, a mailbox monitor or a installed plugin. Do not advertise unchanged full compatibility. A packaged plugin and tested adapters are separate work.

For a form question while another chat drafts CVs, open a separate chat in the same project and give it the role's `private/jobs/APP-…/context.json`, `jd.txt`, the question and its limit. The `questions` helper produces this prompt. The chats share role context but must not write the workbook simultaneously. This version doesn't launch background agents or new chats automatically.

Open `private/Applications.xlsx` in Excel. Add/edit rows on Applications, filter Category, Priority or Status, and use Search for company, role, category, notes or requisition. Search displays the first match and a count; filter Search match to 1 for all matches. Overview shows conversion and rejection by role category and priority, plus monthly and twice-weekly volumes. Data and formulas support 1,000 application rows. Conversion means reaching an assessment, interview or offer, even if later rejected.

## What is implemented

- Universal CV-or-narrative intake, evidence-linked direction proposals and a separate user-confirmation step before category bases are created.
- Candidate-specific categories and title aliases, rather than a fixed career taxonomy. The tracker builder/updater use the private config.
- Hard constraints separate from soft preferences: sector, main duties, base pay, paid employment, location and custom rules. Missing information is held for verification; confirmed violations skip.
- A three-way eligibility check: pass, fail, verify. Unknown visa/clearance facts are held for verification.
- Priority 1–2 skips, priority 3 standard adaptation, priority 4–5 full five-pass CV optimisation. Stronger private CV requirements still apply to priority 3.
- Priority 1–2 is reserved for major seniority or central-capability mismatch. Missing routine Jira/Salesforce familiarity in a coordination-led role is a supporting learning gap; specialist engineering/configuration can be a core gap.
- Evidence-linked drafting rules, preserved chronology/project attribution and a private claim map. The reference checker detects missing IDs; the agent must still verify meaning.
- Duplicate checks using advert URL, employer requisition and company/title. Inspected, genuinely distinct possible matches can proceed with a saved evidence-based review; exact duplicates remain blocked.
- Private per-role packets containing the full JD and decision, so expired adverts and interrupted batches retain context.
- Separate application-question files and word/character-limit checks.
- An XLSX tracker with filters, validations, date-cohort formulas and search.
- Read-only Python workbook search, duplicate checks, statistics and candidate matching for exported email text.
- A Codex spreadsheet update helper with validation, backups and protection against overwriting a workbook changed during an edit.

## Local tools

Python 3.10+ is sufficient for the Python helpers. They use only the standard library and perform no network calls. From this project folder:

The agent translates your input into private intake/direction files, then runs these helpers as needed:

```sh
python3 skills/uk-job-search/scripts/onboarding.py init --input private/intake-input.json
python3 skills/uk-job-search/scripts/onboarding.py propose --input private/direction-input.json
python3 skills/uk-job-search/scripts/onboarding.py confirm --input private/user-confirmation.json
python3 skills/uk-job-search/scripts/onboarding.py check-salary --threshold 30000 --minimum 28000 --maximum 35000
```

`confirm` records an actual user reply and the selected direction IDs. It does not generate Word files itself: Codex creates, renders and verifies the bases after confirmation. `init` refuses to overwrite an existing candidate workspace. The empty intake schema and sample non-negotiables are examples, not defaults imposed on users.

```sh
python3 skills/uk-job-search/scripts/tracker.py search "operations" --category Operations
python3 skills/uk-job-search/scripts/tracker.py duplicates --company "Example" --title "Operations Associate" --url "https://example.com/jobs/123"
python3 skills/uk-job-search/scripts/tracker.py stats --start 2026-10-01 --end 2026-11-01
python3 skills/uk-job-search/scripts/tracker.py check-answer private/answer.txt --words 150 --chars 1000
python3 skills/uk-job-search/scripts/tracker.py check-claims private/jobs/APP-XXXXXXXXXX/claims.json
python3 -m unittest discover -s tests -v
```

`--project PATH` and `--workbook PATH` go before the command. By default the project is the current directory and the workbook is `private/Applications.xlsx`.

After the agent has verified eligibility and prioritised the vacancy, it can create a packet:

```sh
python3 skills/uk-job-search/scripts/tracker.py prepare --company "Example" --title "Operations Associate" --category Operations --url "https://example.com/jobs/123" --jd private/jd.txt --decision private/decision.json
python3 skills/uk-job-search/scripts/tracker.py questions --id APP-XXXXXXXXXX --input examples/questions.json
python3 skills/uk-job-search/scripts/tracker.py email-match private/email.txt
```

The example decision is a schema illustration, not evidence of an actual eligibility pass. Fill it with real requirements and verified facts. When non-negotiables are configured, `constraint_assessments` must include every rule's ID, pass/fail/verify status and source/basis. `prepare` refuses unconfirmed directions, failed/unknown eligibility or hard constraints, and priority 1–2. It creates a draft packet; the agent then adds its Draft tracker row. Submission must be confirmed before Applied date is filled.

For an inspected possible duplicate that is genuinely a different vacancy, use `prepare --duplicate-review private/duplicate-review.json` with the private, source-backed review format in [tracker rules](skills/uk-job-search/references/tracker-rules.md). This cannot override an exact duplicate.

## Workbook creation and updates

The JavaScript helpers require `@oai/artifact-tool` from Codex's bundled spreadsheet runtime; they are not standalone npm tools. Ask Codex to use its spreadsheet skill and dependency loader. Keep a `node_modules` link to the bundled dependencies locally, never in a published archive. Do not copy the bundled runtime into the repository.

`tools/build_tracker.mjs OUTPUT.xlsx [QA_DIRECTORY] [CONFIG.json]` creates a new **empty** template using confirmed config categories and refuses an existing output path. `tools/update_tracker.mjs WORKBOOK PATCHES.json [QA_DIRECTORY] [CONFIG.json]` reads the same categories and refuses a mismatch with the workbook. Both default to `config.json` beside the workbook. Changing directions later requires a reviewed category migration, not rebuilding or silently recategorising applications. The update helper uses patches such as:

```json
[
  {
    "application_id": "APP-XXXXXXXXXX",
    "source": "User confirmed submitting this application on the stated date",
    "fields": {"Status": "Applied", "Applied date": "2026-10-07", "Updated date": "2026-10-07"}
  }
]
```

Run updates through the spreadsheet skill so its operation marker, recalculation and visual checks are performed. Close the workbook in Excel before an agent update. Backups and update source logs are saved under private. The update helper targets this template, not arbitrary existing workbooks. Don't use it after changing column positions without adapting and verifying it.

## Private setup and publishing

The working copy has a private evidence bank and config. Those files, the populated tracker, CVs, emails and job packets are excluded by `.gitignore`. The public ZIP uses an explicit allowlist and excludes the entire private directory and runtime links.

For another user, start the onboarding prompt above. The agent can use `examples/intake.example.json` as a private working schema, extract a supplied CV or record typed experience, and save an evidence bank (`records` with stable `id`, `facts`, `source`, plus profile and claim boundaries). It then proposes directions, waits for user confirmation, and creates the category bases/tracker. `examples/config.example.json` documents the unconfigured state. No applicant data belongs in public examples. An existing user can keep their library and update only changed preferences/evidence.

Review the public file list before publishing updates; keep the private directory excluded from any manual upload. `.gitignore` does not remove files already committed to a repository.

## Current boundaries

This is an agent-assisted local workflow. Local scripts do not authenticate to Gmail, send emails, submit applications or scrape job boards. A connected Codex session can perform authorised read-only Gmail checks and source-backed tracker updates using [the mailbox workflow](skills/uk-job-search/references/manual-applications-and-gmail.md). Scheduling uses the desktop app, not a Python background service. A matching mailbox connection and a successful live run are required before claiming the sync works; synthetic/local checks do not verify it. The computer and desktop app must remain available for local XLSX updates. Job sourcing and autonomous submission are outside the default scope.

No-response deadlines are reminders/inferences rather than confirmed rejection. Early rejection timing doesn't establish an ATS decision or its cause. Editorial fit estimates are a writing/relevance rubric, not an ATS score or interview probability.

The spreadsheet was checked with its calculation engine and rendered previews. Native Excel interaction must be confirmed in the user's Excel version; a successful export alone doesn't verify its UI behavior. Word creation/rendering uses the document tools available in the Codex session.

See [validation results](tests/VALIDATION.md) for the checks actually executed and the integrations still awaiting a live test. New tracker reporting starts in the creation month; the twice-weekly periods include that month's opening days. Existing workbooks are preserved and are not rebuilt by these changes.
