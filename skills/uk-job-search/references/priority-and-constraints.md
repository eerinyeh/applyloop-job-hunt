# Role fit, gaps and hard constraints

Assess three separate dimensions: candidate eligibility, user non-negotiables and fit/preference priority. Every assessment uses the full advert's duties and requirement wording, compared with candidate evidence. Missing information is verify. A hard-constraint or eligibility failure can skip a well-matched role without describing the candidate as unqualified.

## What qualifies as priority 1–2

Reserve the very-low band for a significant mismatch in **actual seniority/responsibility** or **capabilities central to performing the job**. Examples: a junior/mid candidate versus staff/principal work involving organisation-wide technical/design strategy and mentoring; a candidate without professional coding experience versus software engineering whose main work is Python/backend development; or a regulated profession requiring a licence the candidate lacks.

Title alone is insufficient. Staff/principal labels vary, and years alone are not a reliable measure of ownership. Compare decision authority, complexity, specialist depth, accountability and essential experience. A 3–4-year preference versus two years of relevant, high-ownership delivery can be a stretch to assess, rather than an automatic priority 1–2.

## Learnable supporting tools

Do **not** assign priority 1–2 merely because a communication/coordination-led role mentions a tool such as Jira or Salesforce that the candidate has not used. Distinguish routine task/case tracking from specialist administration, configuration, automation, architecture, development or migration. If the underlying work is supported, ordinary tool familiarity is a learning/presentation gap: explain it accurately and retain realistic priority 3–5 according to fit and interest. The skill remains absent from the CV until confirmed.

Salesforce developer or administrator roles and Jira engineering/configuration roles can have core specialist requirements. They are not presumed learnable immediately because the same tool name also appears in operations roles. Similarly, Python as a principal working method differs from optional light scripting in an otherwise well-matched role. Respect an explicit mandatory certification or demonstrable specialist-experience requirement.

For each gap record: exact requirement, essential/preferred, main versus supporting work, demonstrated transferable capability, missing depth, whether it is a substantive/core gap or learnable supporting gap, and why. Never label an unfamiliar skill 'learnable' just to excuse a central gap, or claim that willingness establishes proficiency.

## Priority bands

- **1:** incompatible principal work or professional/seniority requirements.
- **2:** substantial seniority or central-capability mismatch; very weak realistic fit.
- **3:** plausible transferable fit or a manageable stretch, or lower interest with no hard-constraint violation.
- **4:** desired work with several strong supported matches; supporting tool gaps can remain.
- **5:** desired work with strong evidence across the main responsibilities and appropriate scope. A preferred supporting tool gap need not prevent this band.

No priority is an interview probability. Report important gaps plainly, and don't use missing keywords or unfamiliar tool names as the sole reason for the very-low band.

## Non-negotiables

Read the user's confirmed rules from private config. Match their intended scope: a ban on **mainly cold outreach** is not necessarily a ban on customer conversations or occasional follow-ups. A sector exclusion applies to the actual employer/product, not a speculative association.

For every rule retain rule ID, exact user wording, assessed pass/fail/verify and source/basis. Confirmed violation: skip, no packet/track row. Missing critical salary/location/payment information: verify before an eligible packet. A salary range crossing a strictly greater threshold needs clarification; a fixed base at the threshold fails. Non-negotiables are not overridden by a high fit score.

`scripts/onboarding.py check-salary` handles comparable annual base-pay numbers only. The agent identifies whether the values are base pay, the right currency/pay period and actual versus FTE before using it. It cannot interpret arbitrary adverts or prove their truth. `tracker.py prepare` checks all configured constraint IDs have pass assessments; it cannot perform the semantic assessment for the agent.
