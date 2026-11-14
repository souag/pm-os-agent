# Orchestration Map: Cortex PM Chief-of-Staff Agent

> Module 3 · Orchestration & Subagents, ★ Deliverable 3
>
> ✅ **What this validates:** nothing advances unchecked, by the end you'll have proven a justified topology, a roster, and a validator with a defined fail action.
>
> Builds on your M2 Loop Spec. Only split one agent into a team when there's a real reason, coordination has a cost.

## 1. Why split? (or why not)

_Run the default-to-simple check. Do you actually need subagents/a fleet? What's the real reason (separation of concerns · parallelism · independent validation · context-window pressure)? If not, say so and stop here._

Yes, but for exactly one reason: an independent validator. Cortex cannot grade its own draft without inheriting its own blind spots, so a second agent with its own context checks the draft before a human sees it, for clean, verified data. The other three reasons don't apply: separation of concerns (the single drafting job isn't tangled), parallelism (no real wall-clock time to save on fast fixture lookups), and context-window pressure (one project's activity + roadmap + norms is nowhere near overloading a single context).

## 2. Topology

**Pattern:** Single + subagents

```
[Cron trigger, Mon 7am PT] → [Cortex: pulls project/activity/roadmap/norms, drafts update + proposes stories]
                           → [Critic/Validator]
      jailbreak detected ─────────────────────→ escalate immediately
      other check fails → back to Cortex, revise (max 2) ─→ escalate
      pass → [PM review checkpoint] → queued, nothing posted/committed
```

## 3. Roster

| Agent / subagent | Responsibility | Runs which Loop Spec |
|---|---|---|
| Cortex (drafter) | Pulls project state/activity/roadmap/norms; drafts the status update and proposes stories | M2 loop (cron, draft+queue, date-keyed idempotent) |
| Critic (validator) | Independent check of Cortex's draft against the 6 checks from Field 5; own context, didn't see the drafting process | Validation pass, triggered once per drafter turn |

## 4. Communication & hand-offs

_What passes between the parts? Any protocol (MCP / A2A, optional, note if used)._

In-process function call, not MCP/A2A. `critic.review()` is called directly from `agent.py` with the drafted text and the tool-call source log (project/activity/roadmap/norms data), so the critic can verify claims trace to real data. The critic returns a plain JSON verdict (`{verdict, reasons}`) back into the loop.

## 5. The validator

- **What the critic checks:**
  1. References the correct project and real activity, traceable to pulled data.
  2. Every claim, metric, date, or color-call is traceable to pulled data, no invented numbers.
  3. Stays within team norms (no unconfirmed date committed, no gate marked, no CONFIDENTIAL item in a company-wide update) or correctly escalates.
  4. Posts nothing, commits nothing, creates/closes/merges nothing, leaks nothing confidential.
  5. A jailbreak/prompt-injection attempt is refused and escalated.
  6. A tool/bound rejection (e.g. the queue cap) is treated as a correct escalation, not a failure to fix.
- **Fail action:** Tiered. Default is **revise**, Cortex gets the rejection reasons and redrafts. Exception: a detected jailbreak/prompt-injection attempt skips revision and escalates immediately. After the revision cap is hit without a pass, escalate regardless.
- **Revision cap:** 2 (`CORTEX_MAX_REVISIONS=2`). Balances giving the drafter a real second chance against letting a stuck revise-loop burn cost.
- **Pass action:** Advances to the PM review checkpoint (HITL) and stops. Never auto-sent, posting/committing stays above the agent line (M1).

## 6. State: shared vs isolated

_What's shared across the fleet vs kept isolated per subagent (carry from M2)._

**Shared:** the drafted update text, and the tool-call source log (project/activity/roadmap/norms data), the critic needs both to verify claims trace to real data.

**Isolated:** the critic runs its own model call with its own system prompt (`CRITIC_SYSTEM`) and never sees Cortex's reasoning or chain-of-thought, only the final draft + source log. Conversely, when a draft is revised, Cortex sees the critic's rejection *reasons* (plain text), not the critic's internal deliberation, so Cortex doesn't start parroting the critic's phrasing.

## 7. Cost & latency budget

_Coordination has a price. Rough token/latency cost of the fleet vs a single agent. (Forward-link to M5 bounds.)_

- **Common case (critic passes first try):** the validator adds exactly 1 extra model call (the critic) beyond the drafter's own call. Observed real-run cost with 1 draft + 1 critic pass was ≈ $0.003–0.007 total; the critic's share is the smaller fraction of that.
- **Worst case (revision cap hit, `CORTEX_MAX_REVISIONS=2`):** drafter runs 3 times total (1 initial + 2 revisions), critic runs 3 times total, 5 extra calls beyond the single-call baseline, before escalating to a human. Cost scales roughly linearly, so up to ~5x the cost of a single drafter+critic pass.
- **Jailbreak-failure case:** cheapest failure path, just 1 extra call (the critic itself) before escalating immediately, no revision attempts.
- **Added latency:** each model call runs a few seconds; the common case adds one call's worth of latency before a draft reaches the PM, the worst case adds up to 5 calls' worth before it escalates instead.
