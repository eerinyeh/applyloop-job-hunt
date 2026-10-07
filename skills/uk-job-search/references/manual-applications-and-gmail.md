# Manual applications and Gmail tracking

## Application preparation

The candidate finds and selects openings and supplies the complete JD or a specific advert link. Keep duplicate, eligibility and non-negotiable checks, then prepare the chosen level of CV/cover-letter work and a Draft record. The candidate handles accounts, verification, uploads, attestations and final submission.

Only questions actually supplied or visible in an explicitly shared form are known. A JD alone cannot reveal a portal's hidden questions. Accept pasted questions with company/role or Application ID and word/character limits; also accept screenshots or an explicitly shared browser page through available tools. Inspect only the identified application when requested. A request to inspect/draft form answers is not permission to submit it. Do not promise every question is visible before an account is created or a file uploaded.

Save the actual question and answer in that role's packet. Read its JD and relevant evidence; do not repeat full CV optimisation for a short question. Research the specific company from primary sources for company-specific answers when useful, keeping candidate evidence separate. Label guessed practice questions as optional preparation, not mandatory form fields. Check answer limits. If a CV batch is occupying the chat, a separate chat in the same project can read the saved packet; the user starts it, and only one writer updates Excel at a time.

Completion of a CV is Ready, not Applied. A user confirmation such as 'Submitted APP-… today' or an unambiguous employer receipt proves submission. Use the user-stated date or a date explicitly established by the receipt; do not silently substitute the email receipt date for an unknown submission date. Hold the update for clarification when the required Applied date is unknown. Never count prepared documents as submitted applications.

## Connected Gmail checks

The skill's local Python tools do not authenticate to Gmail. Scheduled Codex runs use the available Gmail connector and spreadsheet runtime. This depends on the user's connections, local file access and scheduling environment. A local XLSX needs the computer on and desktop app running. Verify a live run before describing email synchronisation as tested.

Store the target mailbox, cadence and sync state under private, never in public examples. Before every mailbox read, call the connector's profile tool and compare its email with the exact configured target. On mismatch, read no mail and report the connection needed once, then remain quiet until the connection state changes. Do not change another account's connection or permissions implicitly.

Use read operations only: do not send/draft replies in Gmail, archive, label, delete, accept invitations or submit assessments. An assessment invitation creates an action/deadline; it does not complete the assessment. A scheduling request creates an action; it does not book an interview.

### Incremental processing

1. Read the current workbook and private sync state. If there are no tracked applications, do not scan an unrelated inbox. For an initial run with applications, use a bounded recent window (seven days by default); older reconciliation is an explicit separate request.
2. Search new messages relevant to tracked employers, roles, requisitions or saved threads. Include reasonable recruitment/platform senders; sender alone never establishes the employer or role. Overlap the previous successful check by one day and deduplicate by immutable message ID. Paginate the whole selected search window before advancing its watermark; partial failures retain the earlier watermark for retry.
3. Read only plausible messages and the bounded thread context needed to interpret them. Match exact requisitions, specific role titles and established application threads. Same employer with multiple roles or generic wording requires review. Unmatched updates belong in private pending review and do not create speculative rows.
4. Extract event type, message timestamp, any explicit event/deadline date and timezone, exact role, source message ID and supporting text. Save a concise event record; retain relevant evidence without copying unrelated inbox contents. Distinguish invitations from scheduled/completed events.
5. Prepare source-backed patches by stable Application ID. Read latest status and event history first. Do not regress Interview to Applied because a delayed receipt arrives, erase a deadline due to a receipt, overwrite a user correction, or reopen a terminal status without explicit evidence. Conflicts remain pending. Keep first progression after rejection and preserve existing manual edits.
6. Use the workbook updater with its backup, validation and concurrency checks. Re-read the saved row before marking the message processed. If a write fails, leave it unprocessed. If the workbook succeeded but the ledger write failed, reconcile the recorded message ID against the update log before retrying, rather than duplicating the event. Defer locked/open/conflicting files and report the required action.

Keep private `email-sync-state.json` with the verified mailbox, last successful search watermark, processed message IDs with Application ID/event reference, pending-review message IDs/reasons and the last reported connection/error state. Keep timestamped source-backed event records under `private/email-events/`; the workbook is the concise current view, the events retain history. Pending messages are not repeatedly re-read until new context or a user correction can resolve them.

### Status mapping

| Employer message | Current tracker status/action |
| --- | --- |
| Specific application receipt | Applied after submission date is established; no progression |
| Assessment/test invitation | Assessment; record task and explicit deadline |
| HR screening invitation or booking | Interview; Notes identify HR screening and invitation/booking; Next action follows the message |
| Hiring-manager or later-round invitation/booking | Interview; Notes identify exact stage; preserve earlier stage history |
| Offer | Offer; record stated response deadline |
| Explicit rejection for the matched role | Rejected; preserve first progression and record rejection event date |
| Generic talent-pool newsletter or receipt acknowledgment | No stage change |
| Silence or stated no-reply cutoff | Reminder/review, never a confirmed rejection |

The existing workbook uses one Interview status. HR screening, hiring-manager calls and later rounds are detailed in Notes/Next action and private event history; they are not separate dropdown statuses. An email referring to a call does not prove its date, acceptance or completion. Do not infer rejection causes from timing.

### Employer-stated silence deadlines

When a specific confirmation says that no reply within X days/weeks means unsuccessful, save the exact wording, source message ID, matched Application ID, start-date basis, calendar/business-day basis and computed cutoff in a private event's `silence_rule`. Also show the review date and basis in the workbook's Due date/Next action/Notes when it does not replace a more important current action. If the rule's starting date, timezone or business-day calendar cannot be resolved, hold it for clarification; never invent them. For date-only cutoffs wait until that local day has finished.

Every scheduled run checks saved due silence rules even when no new email was found. Before changing a status, refresh the relevant thread and search for subsequent role-specific responses through the current check. If retrieval is incomplete, fails or leaves an ambiguous possible response, defer the change. Apply only to applications still awaiting an initial response (normally Applied); do not expire an assessment, interview, offer or user-confirmed withdrawal/rejection with an earlier receipt's rule. Later invitations or responses supersede the silence rule.

When the full cutoff has passed and no relevant reply is found after a successful check, change to No response (inferred), record the check time and source-backed basis, and preserve the employer's wording. It is not a confirmed rejection and is excluded from confirmed rejection rates. Notify once for that transition. If a later employer message arrives, replace the inferred status with the supported new status and retain the history. Do not send a follow-up automatically.

### Notifications and usage

When setting up monitoring, collect the candidate's timezone, frequency, local times and days of week. These are user settings, not fixed properties of the skill. A suggested starting schedule is weekdays at 10:30 and 17:30 in the user's timezone, only if they accept it. Users can change the schedule later through a chat request or the app's scheduling controls; update the existing automation and private preferences together rather than creating a duplicate. Changing an example/config file alone does not change the running app schedule.

With weekends excluded, Monday's search continues from the last successful Friday check, including Saturday/Sunday and any longer missed-run gap. Never substitute a fixed last-24-hours query for the watermark. Handle overdue silence rules on the next scheduled check. Holidays remain scheduled unless the user requests a holiday calendar.

Use a scheduled check in the existing chat when requested; twice daily is a reasonable starting cadence, not instant delivery. Notify on meaningful stage changes, actionable tasks/deadlines, newly unresolved matches or failures requiring the user. Stay quiet when nothing relevant changes. Track processed messages and keep retrieval bounded rather than re-reading the inbox or entire CV bank. Company research and full CV review are unnecessary for routine status updates. Actual usage must be measured; no fixed token-cost promise is warranted.
