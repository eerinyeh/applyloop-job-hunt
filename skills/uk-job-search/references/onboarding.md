# Universal candidate onboarding

Start here for a new user, a missing private profile or a request to change search directions. Existing users can review only the changed information. Never require an existing CV library, a portfolio, GitHub or a particular profession.

## 1. Collect CV and/or experience

Offer two equally valid entry paths, which can be combined:

- Upload an existing base CV. Extract the complete text with available document/PDF tools, inspect reading order and keep the original private and unchanged. Use the CV as candidate-supplied evidence, not independent proof of every claim. Ask about unclear dates, attribution, metrics and recent changes only when they matter.
- Type detailed background. Collect name, location, email, phone, LinkedIn and optional portfolio/GitHub/other links; education, work experience, side projects, skills, volunteering, training, languages and any other relevant experience. For each experience collect organisation/project, title, dates, context, responsibilities, individual contribution, tools, scope, outcomes and which outcomes were measured. Optional or unavailable details remain blank. Do not demand an address, nationality or visa details unless needed for an eligibility question.

Accept a long narrative; do not force users to complete JSON or repeat details already extracted from a CV. The agent translates the input into the private intake schema, preserves raw text/source references and creates separate evidence records by experience/project. An uploaded CV and new narrative can supplement one another. Where they conflict, show the specific difference and prioritise the newest direct clarification. Keep unresolved claims marked uncertain and out of base CVs.

`scripts/onboarding.py init --input ...` saves a new profile/evidence/preferences workspace without overwriting an existing one. It is a persistence/validation helper, not a CV parser or recommendation model. Document extraction and source-grounded recommendations are performed by the agent. For existing profiles edit/merge the relevant private files after reviewing the changes; do not reinitialise or discard their evidence.

## 2. Collect goals and non-negotiables

Also ask whether to start with an empty tracker or import an existing XLSX/CSV. If supplied, preserve it privately and read [tracker import](tracker-import.md). Inspect/mapping work can start during onboarding; consolidate into a new tracker after categories are confirmed. Do not overwrite the user's source or treat their historical applications as newly triaged vacancies.

Ask for desired job categories and/or titles in the user's own words. Map different titles to actual duties and retain aliases rather than demanding one taxonomy. Ask about preferred responsibilities, seniority, industries and working pattern when helpful.

Separate **preferences** from **non-negotiables**. Examples of hard constraints, only if selected by that user: exclude gambling; no roles where cold outreach is a main duty; annual guaranteed base salary strictly greater than GBP 30,000; paid employment only; work based in London. Record the exact wording, scope and any exceptions. A soft interest in avoiding sales is different from a hard ban on cold outreach as a central responsibility.

For salary record currency, annual/hourly basis, full-time equivalent versus actual contracted pay and strict `>` versus `>=`. OTE, commission and benefits cannot satisfy a base-pay threshold. A range crossing the threshold needs verification; an unspecified salary is unknown, not a violation. Do not assume a salary conversion, exchange rate or part-time basis. 'London' may mean an office location, commutable work, or remote work from London: clarify once rather than inventing a radius.

Save hard constraints separately from eligibility and fit. Every vacancy gets a pass/fail/verify assessment for each applicable hard constraint with the supporting advert/portal text. A confirmed violation skips independently of fit priority. Unknown critical facts create a hold to verify. An empty constraint list is valid and means none supplied, not permission to invent defaults.

## 3. Recommend and confirm directions

Use verified experience and stated interests to propose the requested directions and a few adjacent possibilities when evidence supports them. For each: show category, example titles, the concrete transferable capabilities/evidence, why the work fits, substantive gaps and alignment with preferences. Do not invent capabilities or assume domain/job demand from a title. Research actual role requirements when making current market recommendations, using primary employer sources. No fixed seven-category list or employer-specific eligibility promise.

Keep recommendations provisional. Ask which directions to keep, remove or add and show the interpreted hard constraints in the same concise confirmation. Wait for the user's answer before adopting directions or creating their category base CVs. This is the user's requested decision point; time passing is not confirmation. Continue organizing/extracting supplied evidence while waiting.

Use `propose` to save source-linked draft directions and `confirm` only after an actual user reply. Confirmation can include their original directions, some recommended ones, or new directions supported by the evidence. Record their reply and stable direction IDs. The helper verifies references and the confirmation record; the agent must check that the user actually authorized it.

## 4. Create the category base CVs

If the user requests Gmail tracking, separately collect the target mailbox, timezone, check times/frequency and days of week. Suggest weekdays at 10:30 and 17:30 if useful, but use their actual preference. Verify the connector account before reading mail and set up the schedule through the app after authorisation. See [manual applications and Gmail tracking](manual-applications-and-gmail.md). A schedule is not activated merely by onboarding or downloading the repository.

After direction confirmation create one editable base DOCX per confirmed category under `private/base_cvs/`, plus matching extracted TXT, claim map and a private base index mapping direction ID, category and title aliases to files. Use each direction's actual work requirements to select and order supported evidence. These are reusable category bases, not applications for an imaginary vacancy. Do not run vacancy-specific recruiter scores or pretend to speak for a company at this stage.

Use a restrained consulting/banking-style layout with parser-friendly structure: one column, native paragraphs/bullets, conventional section headings, reverse chronology, consistent dates, and contact information in the body. Use a readable 11pt body font, a larger name, clear section hierarchy, concise action/scope/outcome bullets and sensible whitespace. No photos, skill bars, decorative icons, text boxes or layout tables. Keep links readable. Aim for one page for early-career candidates without shrinking text; ask about a longer version if the experience genuinely needs it. Education may lead for students/recent graduates and relevant recruiting routes; experience may lead where it is stronger. A three-sentence summary may be used when it adds direction-specific value and fits the user's preference, not as mandatory filler for every banking/consulting base. Follow supplied formatting templates and direct user preferences.

Consulting/banking style describes the appearance; it does not imply consulting, banking, investment or modelling experience. Never manufacture finance credentials to suit the style. For an existing user with exact formatting preferences, those control the base CVs.

Render every final Word base, inspect every page, and verify extracted reading order, dates, hyperlinks and evidence support. There is no universal ATS format standard or guaranteed parser result. Describe these as parser-friendly conventions, not proof of passage. Only mark bases ready after the required QA. Update the config with confirmed categories and base-index path, then create the tracker with those categories. Do not silently recategorise historical applications when directions later change.
