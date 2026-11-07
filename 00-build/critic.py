"""Independent validator (M3). A separate model call that never saw the drafting
context, so it can't inherit the draft's blind spots. Returns a pass/fail verdict.
The revision cap that stops a critic<->drafter loop lives in `agent.py`.
"""

from __future__ import annotations

from prompts import CRITIC_SYSTEM

# Claude has no response_format=json_object mode; force structured output by
# requiring a single tool call instead.
VERDICT_TOOL = {
    "name": "submit_verdict",
    "description": "Submit the validation verdict for the proposed output.",
    "input_schema": {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": ["pass", "fail"]},
            "reasons": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["verdict", "reasons"],
    },
}


def review(client, model: str, proposed_output: str, source_data: str) -> dict:
    """Return {"verdict": "pass"|"fail", "reasons": [...]} for a proposed output."""
    resp = client.messages.create(
        model=model,
        max_tokens=1024,
        system=CRITIC_SYSTEM,
        messages=[
            {"role": "user", "content":
                f"SOURCE DATA Cortex used:\n{source_data}\n\n"
                f"CORTEX PROPOSED OUTPUT:\n{proposed_output}"},
        ],
        tools=[VERDICT_TOOL],
        tool_choice={"type": "tool", "name": "submit_verdict"},
    )
    verdict = {"verdict": "fail", "reasons": ["critic returned unparseable output"]}
    for block in resp.content:
        if block.type == "tool_use" and block.name == "submit_verdict":
            verdict = dict(block.input)
            break
    verdict["_usage"] = {"prompt": resp.usage.input_tokens, "completion": resp.usage.output_tokens}
    return verdict
