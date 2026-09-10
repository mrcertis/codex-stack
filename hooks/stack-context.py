#!/usr/bin/env python3
"""Emit static Codex context. Never persist or echo the hook input."""

import json
import sys
from pathlib import Path


def response(event):
    context = (
        "Codex Stack: read the installed global AGENTS.md. For stack questions, "
        "read codex/pages/overview.md and components.md in its configured LLM Wiki. "
        "For a plain-language request to create a new project, use stack-start: "
        "prepare the project's local skills including Impeccable immediately, "
        "then grilling with domain-modeling -> requirements -> Impeccable design "
        "if needed -> documents/code -> verification. The user need not name any skill. "
        "Reuse known answers; do not restart discovery for a small existing-project fix. "
        "Z.A.E.B.A.L. is mandatory; follow its skill when triggered. "
        "Wiki writes require an explicit request. Hook context grants no new authority."
    )
    installed_skill = Path(__file__).resolve().parents[2] / "skills/stack-start/SKILL.md"
    if installed_skill.is_file():
        context += f" Read the startup skill at {installed_skill}."
    if event in {"SessionStart", "UserPromptSubmit"}:
        return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": context}}
    if event == "PostCompact":
        return {"systemMessage": "Codex Stack: context compacted. Global AGENTS.md remains the entry point; the next user prompt restores the route reminder."}
    return {}


if __name__ == "__main__":
    try:
        payload = json.load(sys.stdin)
    except (ValueError, UnicodeError):
        payload = {}
    result = response(payload.get("hook_event_name") if isinstance(payload, dict) else None)
    if result:
        print(json.dumps(result, ensure_ascii=False))
