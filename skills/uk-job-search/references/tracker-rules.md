# Tracker rules

The workbook has three useful views: `Overview` for period/cohort metrics, `Search` for quick retrieval, `Applications` for the editable filterable table. Data validations and calculations are prepared through row 1005 (1,000 records). Extend the formulas/validation and named table ranges together before exceeding that limit. Search uses a match column; enter a query on Search, then filter `Search match` to 1 on Applications. Blank query includes all populated records. Excel Find is also available. The CLI search has no workbook formula limit.

## Data contract

Columns: Application ID, Company, Job title, Category, Priority, Status, Applied date, Advert URL, Location, Next action, Due date, First progressed date, Updated date, Notes, Requisition ID, Search match.

Use one stable `APP-` ID per application/packet. A repost/duplicate URL does not create another application. Store the full advert locally in the packet because online adverts expire. Same company/title can represent a genuinely new requisition; inspect it. Save the employer requisition ID when available. Keep priority 1–2 and held eligibility checks out of the main tracker. Draft rows are not applications until Applied date is entered.

`prepare` stops on possible matches until inspected. If all matches are genuinely distinct, the agent saves a private review list, one entry per matched Application ID: `{"id":"APP-XXXXXXXXXX","outcome":"distinct","basis":"Verified distinction with advert/requisition sources"}`. Pass its path as `--duplicate-review private/duplicate-review.json`. It must cover every possible matched ID exactly once; its basis is retained in the new packet. Exact duplicate matches cannot be overridden. A review is evidence of inspection, not permission to invent different requisitions or apply twice.

Primary categories come from the candidate's confirmed private config/direction index. Use one primary category per record so totals reconcile; map title aliases by actual duties. Secondary possibilities belong in notes or the role packet. The builder creates category summary rows and dropdowns from that config. Later category changes require a reviewed workbook/config migration that preserves historical records; no universal default list is imposed.

Statuses: Draft, Ready, Applied, Assessment, Interview, Offer, Rejected, Withdrawn, No response (inferred), On hold. Confirmed application dates are required for all submitted applications. Store dates as Excel dates. `First progressed date` is the first employer-requested assessment, interview or offer; automated receipt alone does not count. Keep it after later rejection. This prevents conversion rates falling merely because a progressed candidate was rejected.

## Metrics

The editable start date and exclusive end date on Overview select applications by **Applied date**. An end date of 1 November includes all October applications. Statuses reflect the latest known outcome as of now, so old cohorts evolve. Current window defaults to October 2026; edit the yellow start/end dates for any week, semiweek or month. The displayed monthly and semiweekly tables are application volumes. Semiweekly means Monday–Wednesday and Thursday–Sunday (chosen default, configurable in a future revision).

- Applications: count of rows with an Applied date within the selected cohort.
- Progressed: those rows with a First progressed date.
- Conversion: progressed applications / submitted applications.
- Confirmed rejection: submitted rows currently marked Rejected / submitted applications.
- Offer: submitted rows currently marked Offer / submitted applications.
- No response (inferred) is counted separately and excluded from confirmed rejection.
- Empty denominators show `n.a.`. Small or recent cohorts are incomplete, not evidence that a category is ineffective.

Category and priority summaries use the same cohort and definitions. Don't infer rejection reasons from quick timing; record an employer-stated reason separately from hypotheses.

## Writes and email updates

The Python tool reads only. For an agent write, back up the current workbook to a private timestamped path, re-read it, and update the row identified by stable ID using available spreadsheet tools. The optional `tools/update_tracker.mjs` applies JSON patches, preserves source fields and backs up the file. It requires the bundled Codex artifact-tool runtime and a source reference for each patch. Preserve all unrelated manual edits, and render changed areas after broad formatting changes. Check saved dates/status and relevant formulas. Don't open/save the workbook with a tool that loses unsupported features.

`email-match` produces candidate matches from exported email text using requisition/company/title. It performs no login, no inbox scanning and no autonomous status update. Confirm against the message, exact role and sender context. Multiple matches or generic company emails require manual resolution. Store a concise message reference/update, not an entire inbox in the workbook.

For an explicit 'if no reply in X weeks' message, save its date and review deadline. At the deadline check for later messages. Mark No response (inferred) when appropriate, retain the basis, and permit correction when the employer later responds. It is never a confirmed rejection without a rejection message.
