# Production & Autonomy: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 5, how you'd ship it, govern it, and widen trust over time
>
> ✅ **What this validates:** you can ship it, govern it, and widen trust deliberately, by the end you'll have proven an autonomy dial, a Trust Ladder rung with its eval gate, and a governance plan.

## Autonomy Dial by segment

_Autonomy is a product decision per user, not one global setting._

| Segment | Desired autonomy | Why |
|---|---|---|
| PM/owner (runs Cortex day-to-day) | Supervised | Built it and knows its blind spots firsthand, so stays hands-on reviewing every draft while trust is being established |
| Peer PMs/team leads (others who might adopt Cortex for their own projects) | Assisted | Lower trust since they didn't build it and haven't seen its failure modes; want full-trace visibility, not just the final draft, until they build their own track record with it |
| Leadership/exec stakeholders (readers of the output only) | Shadow | Never interact with Cortex directly, only ever see an update a human already approved, zero autonomy risk since nothing reaches them unapproved |

## Trust Ladder

- **Current rung:** Supervised. Every single run, even a clean, low-risk green update, stops at the HITL checkpoint and waits for a human decision before anything moves forward. No action gets auto-approved regardless of how routine it is.
- **Eval gate to reach the next rung (bounded-autonomous):** ≥95% pass rate across EV-1 through EV-4 (tool-call accuracy, path quality, recovery, task completion), AND zero failures on EV-5 (jailbreak/safety, `jailbreak_failure` never true), AND EV-6 always halts correctly whenever a bound is tripped, sustained over 4 consecutive weekly production runs.
- **Incident record so far:** Clean for this window means zero `jailbreak_failure: true` verdicts, zero cases where a human (not the critic) had to catch an invented metric or date the critic missed, and zero cost-cap/iteration-cap trips caused by anything other than a deliberately tested low cap (i.e., no genuine production runaway).

## Deployment plan

- **Runtime:** Serverless scheduled execution, not an always-on process. Cortex's M2 loop type is cron (Mon 7am PT); it's a short-lived script that wakes up weekly and exits in under a minute, so there's no standing state to justify an always-on managed platform.
- **Operator / on-call owner:** The PM/owner, named directly, not "the team," since this is currently a single-operator system. Escalation path: any `ESCALATE` run result triggers a direct notification (Slack DM/email) to the owner, not a shared queue.
- **Rollback:** a toolkit, not one option. Revert `prompts.py`/`agent.py` to the last known-good commit; disable a specific tool by removing it from `TOOL_SCHEMAS`/`TOOLS` without a full rollback; or drop the dial a rung (force every run back to full escalation) if the issue is behavioral rather than code-level.
- **Monitoring:** eval pass % (the 6 EV cases, tracked over time), escalation rate (ESCALATE vs. DONE ratio), cost-to-serve (per-run `Bounds.cost`, aggregated weekly), trust incidents (`jailbreak_failure` flags + human-caught misses).

## ROI metrics (beyond adoption & tokens)

| Metric | Target |
|---|---|
| Outcome | % of weekly drafts approved with zero edits, a simple yes/no tally kept at review time |
| Cost-to-serve | $ per approved update (total model cost divided by updates actually used), read directly from `Bounds.cost` |
| Trust incidents | Count per month of times a human caught something the critic missed (invented claim, scope creep, confidential leak), logged manually |

## Widen-autonomy decision rule

_What evidence lets you turn the dial up one notch, stated in advance._

Cortex's dial moves up one rung only once it clears the eval gate defined on its Trust Ladder, verified against real production run logs, never on the strength of a single good demo run.

## Governance & forward strategy

- **Compliance:** Never put customer PII into a prompt. Fixtures today are internal project/engineering metadata only; any future real connector stays scoped to project/engineering systems, never a CRM or support system with customer PII.
- **Safety:** Posting, committing a date, marking a gate, merging/closing a ticket stay above the line for everyone regardless of dial position, the dial never touches the M1 agent line. Kill switch: revoke `ANTHROPIC_API_KEY`.
- **Reliability:** Cost/iteration/revision/timeout caps already in place escalate rather than loop. If the Anthropic API itself is down/erroring, the run should fail loudly (alert the owner) rather than silently skip the week.
- **Strategy:** Next widen target is the "peer PMs/team leads" segment, gated by the same EV-1-6 suite passing against at least 2 different projects' data, not just Northstar, before onboarding a second human operator.
