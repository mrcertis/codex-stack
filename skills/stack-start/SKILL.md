---
name: stack-start
description: Start a new project from a plain-language idea such as «давай сделаем сайт», «хочу приложение» or «сделаем бота». Install Impeccable into the project, then hand over to GSD (gsd-new-project) for the interview, requirements, roadmap and phases. Does not apply to a small fix, read-only review or an existing project that already has .planning/.
---

# Start from the user's idea

The user describes the desired product; they do not need skill names, commands,
framework choices or a prepared specification. Select tools yourself.

1. Identify the intended project directory from the active task. If missing,
   create a suitable directory within the authorized workspace or resolve the
   actual ambiguity. Never initialize the stack distribution, home directory or
   an unrelated existing project merely because the session opened there.
2. Run `scripts/prepare_project.py --project /absolute/project` from this skill's
   directory with Python 3.11+; add `--host claude` in Claude Code. It installs
   Impeccable locally even before UI requirements are known and preserves an
   existing installation. Respect runtime network/write permissions. If setup
   fails, report the actual missing part; do not claim it installed.
3. Explain in one line that the project will be run through GSD and start
   `gsd-new-project` ($gsd-new-project in Codex, /gsd-new-project in Claude Code)
   after the user agrees. GSD conducts the interview and writes the requirements;
   do not run a separate interview before it.
4. Follow the global rules for GSD: ask GSD's questions and wait for answers,
   stop at the four confirmation points, never pick options for the user.
5. When the project needs UI, use Refero for references if it is connected,
   and the local Impeccable skill for the design workflow. For a backend-only
   project leave Impeccable installed and skip the design workflow.

For existing code without `.planning/`, do not use this skill: propose
`gsd-onboard`. New local skills may not appear in the current session's skill
menu; read their files directly and verify hook trust separately.
