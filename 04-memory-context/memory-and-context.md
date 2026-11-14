# Context Engineering & Memory: Cortex PM Chief-of-Staff Agent

> Module 4 · Context Engineering & Memory
>
> ✅ **What this validates:** the agent reasons on the right, safe inputs, by the end you'll have proven a context budget, per-source retrieve-vs-long-context decisions, and a memory map with risk mitigations.
>
> 🗂️ **How the lab maps to this file:** In **Part A** (before the lecture) you don't edit this file, you rough-draft on scratch, focused on the per-source calls in **section 2** plus a quick remember/forget + "how it rots" sketch. In **Part B** (after the lecture) you complete **all five sections**; the Lab Guide's guided builder writes this file for you to copy in and commit.

## 1. Context budget

_What does each loop iteration actually receive, and why? (You can't fit everything, what's the priority order?)_

Priority order when the budget is tight: (1) the task brief and team norms go in first, small, non-negotiable constraints that define what's being asked and what's off-limits; (2) the project's own activity next, the core evidence a status update is graded on; (3) the roadmap slice after that, needed to check confidentiality before anything is written; (4) past-updates precedent last, useful for tone and continuity but the first thing to drop if something has to give.

## 2. Retrieve vs. long-context: per source

For each data source, decide: **retrieve** (narrow a large/changing corpus to the relevant slice) or **long-context** (just include a bounded set you can reason over).

| Source | Size / volatility | Decision | Why |
|---|---|---|---|
| `get_activity` | Large, grows every sprint | Retrieve | Data changes often and must be current |
| `search_past_updates` | Unbounded, grows every week | Retrieve | Data changes often and must be current |
| `get_roadmap` | Medium, slow-changing, mixes confidential/shareable items | Retrieve | Need to make sure roadmap data is not stale when it changes |
| `get_norms` | Medium, bounded | Long-context | Size is small enough to include in full |
| `get_task` (task brief) | One static, bounded doc | Long-context | Size is small enough to include in full |

## 3. Retrieval quality plan

_Which of these apply, and how? (This is what separates modern agentic retrieval from naive "embed → top-k → stuff".)_

| Source | Move(s) | Why |
|---|---|---|
| `get_activity` | Self-verification | It's a deterministic lookup, not a ranked search, so the risk isn't a wrong item being retrieved, it's a drafted claim not matching what was retrieved. The critic cross-checks every claim against the pulled activity. |
| `search_past_updates` | Document grading | The tool does naive keyword-overlap matching (by design, per its own docstring), so it can surface another project's precedent as if it were relevant tone/precedent. Cortex must check a returned match is actually about the queried project before using it for tone. |
| `get_roadmap` | Document grading + self-verification | Returns one file mixing shareable and confidential/embargoed sections. Cortex must filter to the shareable section before drafting (grading), and the critic independently checks no confidential item leaked (self-verification). |

Routing, reranking, and caching don't apply here: there's exactly one tool per data need (no ambiguity on which source to query), no ranked list to reorder (each tool returns a single deterministic payload), and runs are infrequent and cheap enough that caching isn't worth the staleness risk.

## 4. Memory map (your PM brain)

| Memory type | What Cortex stores | Scope / TTL |
|---|---|---|
| **Working** (in-loop) | This run's pulled data (project, activity, roadmap slice, norms) + the draft + critic verdict + source log | This run only, discarded when the process exits |
| **Episodic** (past runs) | Read: past status updates & decisions (`past-updates.json`, `decision-log.json`) used as precedent. Write: each finished draft saved to `run-output/`, plus a date-keyed idempotency marker recording that week's run completed | Read side is whatever the fixture holds (static here; would grow weekly in production). Write side persists indefinitely in `run-output/`; the marker persists indefinitely but is only checked against its own ISO week |
| **Semantic** (durable facts/prefs) | Team norms + roadmap facts (project status, confidentiality flags) | Re-fetched fresh every run, not cached by Cortex, durable at the source, not in Cortex's own memory |
| **Shared** (across agents) | The draft text + tool-call source log, handed from Cortex to the Critic | Scoped to this run's drafter↔critic exchange only, not persisted beyond it |

## 5. Memory risks & mitigations

| Risk | Mitigation |
|---|---|
| _Drift_ | Revision cap (`CORTEX_MAX_REVISIONS=2`) bounds how many rounds drift can accumulate over; the critic's internal reasoning is never shared verbatim with Cortex, only the rejection reasons, so Cortex doesn't start parroting the critic's phrasing |
| _Poisoning_ | Task brief content is treated as data, not instructions (prompt-injection defense); a detected jailbreak skips revision and escalates immediately rather than giving a compromised context more attempts |
| _Staleness_ | No caching, data is always re-fetched fresh from source each run; the idempotency marker is itself a staleness risk if data is corrected after a run completes, since it would block a legitimate re-run until a human manually clears it |
| _Confidential / retention_ | Read access stays scoped to project/engineering metadata, never customer data; `run-output/` drafts need a retention TTL (forward-link to M5 bounds) rather than accumulating forever. The read-only nature of every source tool (no write-back to systems of record) caps the blast radius on all four risks above |
