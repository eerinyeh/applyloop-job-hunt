# Application writing

## Base and claim controls

Choose the closest verified base from the candidate's confirmed categories/index by actual duties and title aliases. If no category bases exist, complete onboarding and user direction confirmation before generating them. Refer to the private config for paths and formatting. Do not populate a new user's profile with another candidate's facts or a fixed default career taxonomy.

Create a claim map alongside drafts: `{"claims":[{"text":"A substantive sentence or bullet", "evidence_ids":["experience.startxlabs"]}]}`. Use the narrowest supporting ID available. Read the whole supporting record including limits. IDs are provenance aids; referencing a source does not make an embellished sentence supported. Do not put the map in the CV itself.

Keep work-permission facts as dated evidence records too, with an ID such as `eligibility.current`, source and verification status. Distinguish self-reported current status, documented conditions and a planned route. A config preference or agent decision is not evidence of permission. Do not treat a clarification answer as resolving eligibility.

Preserve dates, original titles, individual/team attribution, overlapping roles, expected grades and product stage. Apply XYZ using a measured outcome when supplied; otherwise use supported scope or a specific decision. Scope is not business uplift. No fabricated result is required just to fit a formula. Avoid em dashes in CVs.

## Priority 3

Select the relevant evidence, adjust wording to supported terminology, remove irrelevant detail, check factual support, parser order and the one-page render. Produce a brief cover letter. Where the private workspace requires five review passes for every CV, complete those checks even on priority 3, using a compact review record. Honour any new direct user exception. The public workflow defaults to lighter review for priority 3.

## Priority 4–5: sequential five-pass revision

1. **Scanner:** assess the draft against published requirements. Give five material first-scan concerns (or fewer if five would be invented), missing relevant terminology, section ratings 1–10 with reasons and the highest-impact change. An optional score is an editorial fit estimate, never a claimed ATS score: core responsibilities 40, required capabilities 25, scope/seniority 20, evidence clarity 15. Report eligibility separately. List up to ten missing terms, flag unsupported ones and do not insert them.
2. **Surgeon:** revise the summary into three concise sentences covering identity, evidenced strengths and role relevance. Rewrite experience around concrete actions, supported scope/outcomes and judgement. Update only evidenced skills. Keep body text 11pt and one page when required by the private profile, shortening lower-value content first.
3. **Stress test:** inspect extracted reading order, native paragraphs/bullets, contact info in the body, dates and hyperlinks. Check seven-second visibility, repetition and supported terminology. Front-load meaningful actions where natural. An editorial score improvement is not proof of ATS passage.
4. **HR:** review actual eligibility, unclear chronology, must-have gaps and shortlist reasons. Repair presentation of existing evidence; retain genuine gaps.
5. **Hiring manager:** test ownership, judgement and ability to perform the main work. Distinguish missing professional experience from presentation/learning gaps without assuming a complex technical skill can be acquired immediately. Amplify two or three concrete reasons to interview. Revise, check facts again, render and inspect the final Word file.

Record findings, actual revisions and remaining gaps in the role's `review.md`. Keep the user-facing explanation short unless they ask for the review.

## Cover letters

Aim for about 180–250 words unless the form specifies otherwise. Ground the opening in the actual employer/role, using current employer sources if needed. Explain the candidate's relevant combination, then use one compact STAR example and an optional second short example. State the action and supported result; no invented commercial impact. Finish with the contribution the examples support. Do not merely repeat CV bullets or invent personal enthusiasm.

## Interruptible form answers

Use `questions` to store exact questions and limits separately from draft files. A new chat reads `context.json`, `jd.txt`, the private evidence bank and the question file. It can answer even if the CV is unfinished. Read only that role's context to prevent cross-company contamination.

If the role is held and has no packet, draft from the exact supplied question/advert and private evidence without running the packet-dependent helper. Save the clarification under private and preserve the unresolved eligibility decision.

For each answer: address the exact question, choose the relevant evidence, draft naturally, validate with `check-answer` and create/update `claims.json`. STAR is appropriate for behavioural examples, not mechanically for every motivation question. Respect character limits including spaces and newlines; the CLI reports Unicode and UTF-16 counts because portal counters vary. Verify the final pasted answer in the portal. Work-rights answers require current confirmed facts and the exact question wording; refer to eligibility guidance.
