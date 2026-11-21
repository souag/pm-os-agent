# Build Insights: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 4, what you learned building it
>
> ✅ **What this validates:** you can reflect on what building it taught you, by the end you'll have proven the friction, the learning, and the aha that changes how you'd design your next agent.

## Friction

_Where did the build fight you? (Loop stop conditions? Context budget? The validator? Bounds?)_

Getting the critic to actually produce a rejection was harder than expected, the live model resisted every attempt to weaken it into inventing a claim, even under an adversarial system prompt across multiple escalating tries. Had to fall back to a direct validator test (hand-crafted bad draft) to prove the catch worked.

## Learning

_The two or three things you now understand about shipping agents that you didn't before the course._

1. A bound only counts if it's enforced outside the model, a sentence in a prompt is not a bound.
2. The agent line and the loop spec can quietly drift apart across modules if you don't cross-check them, M1 and M3 actually disagreed until M5 caught it.
3. "Naive RAG" is a real, specific failure mode, not a vague warning, each retrieved source needed a named reason it wasn't naive.

## Aha moment

_The single insight that changed how you'd design your next agent._

The model's own robustness against producing unsafe/invented output, even when I deliberately tried to break it, mattered as much as any bound I wrote in code. Containment is layered: the model itself, the critic, and the infrastructure bounds all have to fail simultaneously for something bad to actually happen.

## What you'd do differently

_If you rebuilt Cortex from scratch, what changes?_

Write the M1 agent line and M5 bounds table in the same sitting, since the gap between what M1 says should require a human and what the build actually enforces only surfaced because M5 explicitly forced a cross-check.
