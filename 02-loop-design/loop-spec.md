# Loop Spec: Cortex PM Chief-of-Staff Agent

> Module 2 · Loop Engineering, ★ Deliverable 2
>
> ✅ **What this validates:** the agent knows when to run and when to stop, by the end you'll have proven a one-page Loop Spec with a trigger, a definition of "done," and explicit stop conditions.
>
> Your one-page blueprint for how the work you handed to the agent (M1) actually *runs*.
> An agent is just a prompt that fires itself, this spec says when it fires, what "done" means, and what it needs to do the job. Living document; refine as the course progresses.

## 1. Trigger & loop type

**Chosen type:** Cron

**Why this type?** The work is calendar-driven (a weekly leadership update), not event-driven — heartbeat, hook, and goal loops are overkill for an activity that only needs to fire once a week.

Run this at the beginning of every work week, typically a Monday at 7 AM PT. If Monday is a holiday or I am on PTO, run this on the next work day or when I am back to work. Read my PTO from enterprise timekeeping tool.

**Idempotency:** Each run is keyed by date. Before drafting, Cortex checks whether that date's key has already been processed and skips if so, preventing a duplicate draft from a retry or re-trigger.

## 2. Goal / definition of done

_What outcome is this loop responsible for? For a goal loop, what validation says "done"? (e.g. a status update grounded in real activity, queued for review, nothing posted.)_

Cortex drafts the weekly leadership status update and proposes next-sprint stories from the backlog (within the story cap), using live project state and activity data. It queues both for human review and stops. Nothing is posted to Slack or any channel; no Jira ticket, milestone, or launch gate is touched, those stay above the agent line (per `agent-line-map.md`).

## 3. Stop conditions

| Condition | What it looks like | What happens |
|---|---|---|
| **Success** | The critic validator passes the drafted update/stories as grounded, in-scope, and norm-compliant | Draft saved to `run-output/`, surfaced at the HITL checkpoint, nothing posted |
| **Stuck / give up** | A required lookup (project, activity, roadmap) returns not-found or no data, or the critic rejects past the revision cap | Stop, do not invent data, escalate to a human with what was tried |
| **Escalate to human** | Embargoed/confidential content requested, a request to commit a ship/GA date, a prompt-injection attempt, or the cost cap is hit | Stop, flag the specific reason, queue nothing that violates the agent line, notify the human |

## 4. State

_What persists across iterations, and what's the scope? (e.g. per-project context and last week's update; no cross-project confidential leakage.)_

Updates per-project context and last week's update; no cross-project confidential leakage. Tracked via the date-keyed idempotency marker from §1, which records that a given week's run has already been processed.

## 5. The five things a loop can lean on

_`state` is always-on. `connectors` only if you already have one wired (e.g. a Jira key or Google MCP), otherwise just note it as a plan. `skills`, `subagents`, `work tree` scale with autonomy; "not needed yet, because…" is a valid answer._

| Component | For Cortex |
|---|---|
| **Work tree** (isolated workspace per run, a git worktree) | Not needed yet, because a single draft-and-queue run needs no isolated workspace, it reads and writes one output file. |
| **Skills** (reusable capabilities) | Not needed yet, because the loop is a single fixed flow, not a library of reusable sub-tasks. |
| **Plugins / connectors** (tools & access, optional if you don't have one yet) | Planned, not yet wired. Current build (`00-build/tools.py`) uses mocked fixture data; live GitHub/Jira read access is the near-term connector to add. |
| **Subagents** (independent check when the loop can't grade itself) | _placeholder → M3 orchestration-map.md_ |
| **State tracking** | The date-keyed idempotency marker from §1 (see §4). |

> Context plan (M4) and the hand-off to bounds & evals (M5) come in later modules, you'll add them to their own deliverables then, not here.

## Link to live loop

_[path to your agent in `00-build/`]_
