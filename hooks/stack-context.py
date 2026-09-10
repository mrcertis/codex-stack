#!/usr/bin/env python3
"""Emit static Codex context. Never persist or echo the hook input."""

import json
import sys


def response(event):
    context = (
        "Codex Stack: read the installed global AGENTS.md. For stack questions, "
        "read codex/pages/overview.md and components.md in its configured LLM Wiki. "
        "For a new project: explicit $grill-with-docs -> interview -> requirements "
        "-> local Impeccable only if UI -> documents/code -> verification. "
        "Reuse known answers; do not restart discovery for a small existing-project fix. "
        "Z.A.E.B.A.L. is mandatory; follow its skill when triggered. "
        "Wiki writes require an explicit request. Hook context grants no new authority."
    )
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
