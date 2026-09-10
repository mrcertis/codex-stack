---
name: stack-start
description: Start a new project from a plain-language idea such as «давай сделаем сайт», «хочу приложение» or «сделаем бота». Prepare local skills, interview the owner, record requirements, then use Impeccable for UI when needed and implement. Does not apply to a small fix, read-only review or maintenance of an existing project.
---

# Start from the user's idea

The user describes the desired product; they do not need skill names, commands,
framework choices or a prepared specification. Select tools yourself.

1. Identify the intended project directory from the active task. If missing,
   create a suitable directory within the authorized workspace or resolve the
   actual ambiguity. Never initialize the stack distribution, home directory or
   an unrelated existing project merely because the session opened there.
2. Before discovery, run `scripts/prepare_project.py --project /absolute/project`
   from this skill's directory, using Python 3.11+. It installs the local starting
   set: grill-with-docs, grilling, domain-modeling and Impeccable, even before UI
   requirements are known. Existing installations are preserved. Respect runtime
   network/write permissions. If setup fails, report the actual missing part;
   do not claim it installed or silently switch to a different project.
3. Read the local grilling and domain-modeling SKILL.md files and conduct their
   combined interview. This is the grill-with-docs workflow. The upstream wrapper
   is explicit-only; this automatic entry point composes its two constituent
   skills, without changing upstream policy or asking the user to type a command.
   Ask about product decisions, research discoverable facts yourself, reuse known
   answers. Record domain terms and significant decisions using domain-modeling.
4. Confirm your understanding and record requirements in the existing canonical
   brief or docs/brief.md. Do not ask the user to choose a skill or repeat the idea.
5. If UI is needed, read the already installed local Impeccable SKILL.md and its
   matching playbook. Its init reuses interview answers for PRODUCT.md; its design
   workflow chooses the visual direction with the user. Do not preselect the UI
   or require an existing design as a condition for installing Impeccable.
   For a backend-only project, leave it installed but skip the design workflow.
6. Implement from the agreed requirements and direction, verify the result and
   finish the required documentation. Use GSD only when the work warrants it.
   DESIGN.md reflects the implemented design according to Impeccable's playbook.

New local skills may not appear in the current session's cached skill menu.
Read their files directly during this turn; do not claim that the catalog or
project hooks reloaded. Check hook support and trust separately. Existing-project
changes use relevant skills directly, without repeating this startup interview.
