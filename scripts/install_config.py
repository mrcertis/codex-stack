#!/usr/bin/env python3
"""Install the public AGENTS template, own hooks and stack-start; dry-run by default."""

import argparse
import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ("SessionStart", "UserPromptSubmit", "PostCompact")
MTGA_BLOCK = re.compile(r"^<!-- MTGA:BEGIN[^\n]*-->$.*?^<!-- MTGA:END -->$", re.M | re.S)


def check_path(path):
    for candidate in (path, *path.parents):
        if candidate.is_symlink():
            raise ValueError(f"Symlink requires manual review: {candidate}")
    if path.exists() and not path.is_file():
        raise ValueError(f"Expected a regular file: {path}")


def merge_hooks(data, command):
    if not isinstance(data, dict) or not isinstance(data.get("hooks", {}), dict):
        raise ValueError("hooks.json must contain an object of events")
    result = copy.deepcopy(data)
    events = result.setdefault("hooks", {})
    for event, groups in events.items():
        if not isinstance(groups, list):
            raise ValueError(f"Invalid event list: {event}")
        for group in groups:
            if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
                raise ValueError(f"Invalid hook group: {event}")
            if any(not isinstance(hook, dict) for hook in group["hooks"]):
                raise ValueError(f"Invalid handler: {event}")
    for event in EVENTS:
        groups = events.setdefault(event, [])
        # Only our exact command belongs to this installer; preserve all others.
        groups[:] = [group for group in groups if group != {
            "hooks": [{"type": "command", "command": command, "timeout": 10}]
        }]
        groups.append({"hooks": [{"type": "command", "command": command, "timeout": 10}]})
    return result


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".codex-stack-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def claude_include(codex_home):
    default = Path.home() / ".codex"
    return "@~/.codex/AGENTS.md" if codex_home == default else f"@{codex_home}/AGENTS.md"


def install(codex_home, tools_root, wiki_root, apply=False, claude_home=None):
    targets = [codex_home / "AGENTS.md", codex_home / "hooks.json",
               codex_home / "hooks/codex-stack/stack-context.py",
               codex_home / "skills/stack-start/SKILL.md",
               codex_home / "skills/stack-start/scripts/prepare_project.py"]
    if claude_home:
        targets += [claude_home / "CLAUDE.md", claude_home / "skills/stack-start/SKILL.md",
                    claude_home / "skills/stack-start/scripts/prepare_project.py"]
    if (codex_home / "AGENTS.override.md").exists():
        raise ValueError("AGENTS.override.md shadows AGENTS.md; review and archive it explicitly first")
    for path in targets:
        check_path(path)
    data = json.loads(targets[1].read_text()) if targets[1].exists() else {}
    command = f"{shlex.quote(sys.executable)} {shlex.quote(str(targets[2]))}"
    merged = merge_hooks(data, command)
    template = (ROOT / "global-config/AGENTS.md").read_text()
    template = template.replace("<TOOLS_ROOT>", str(tools_root)).replace("<WIKI_ROOT>", str(wiki_root))
    template = template.replace("~/.codex", str(codex_home))
    old_agents = targets[0].read_text() if targets[0].exists() else ""
    # MTGA keeps its style block inside AGENTS.md; a full replacement must not drop it.
    mtga = MTGA_BLOCK.search(old_agents)
    if mtga:
        template += "\n" + mtga.group(0) + "\n"
    skill = [(ROOT / "skills/stack-start/SKILL.md").read_text(),
             (ROOT / "skills/stack-start/scripts/prepare_project.py").read_text()]
    contents = [template, json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
                (ROOT / "hooks/stack-context.py").read_text(), *skill]
    if claude_home:
        claude_md = targets[5].read_text() if targets[5].exists() else ""
        line = claude_include(codex_home)
        if line not in claude_md.splitlines():
            claude_md = (claude_md.rstrip("\n") + "\n\n" if claude_md.strip() else "") + line + "\n"
        contents += [claude_md, *skill]
    changes = [(path, content) for path, content in zip(targets, contents)
               if not path.exists() or path.read_text() != content]
    for path, _ in changes:
        print(f"{'INSTALL' if apply else 'DRY RUN'}: {path}")
    if not apply or not changes:
        return
    # Backup is private, outside the source checkout, and created before any replacement.
    if codex_home == ROOT or ROOT in codex_home.parents:
        raise ValueError("CODEX_HOME must be outside the public checkout")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup = codex_home / "stack-backups" / stamp
    check_path(backup / "manifest.json")
    backup.mkdir(parents=True, mode=0o700)
    manifest = []
    for index, (path, _) in enumerate(changes):
        prior = path.exists()
        name = f"{index}-{path.name}"
        if prior:
            shutil.copyfile(path, backup / name)
            (backup / name).chmod(0o600)
        manifest.append({"target": str(path), "existed": prior, "backup": name if prior else None})
    atomic_write(backup / "manifest.json", json.dumps(manifest, indent=2) + "\n")
    for path, content in changes:
        atomic_write(path, content)
    print(f"Backup: {backup}")
    print("Installed files only. Review and trust hooks in Codex, then test a new session.")
    if mtga is None:
        print("MTGA block not found: turn MTGA on after installation (see docs/INSTALL.md#mtga).")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", type=Path, default=Path(os.environ.get("CODEX_HOME", "~/.codex")))
    parser.add_argument("--tools-root", type=Path, default=Path("~/tools"))
    parser.add_argument("--wiki-root", type=Path, default=Path("~/Knowledge/LLM Wiki"))
    parser.add_argument("--claude-home", type=Path,
                        help="also add the AGENTS.md include to CLAUDE.md and stack-start for Claude Code")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    paths = [path.expanduser().absolute() for path in (args.codex_home, args.tools_root, args.wiki_root)]
    claude_home = args.claude_home.expanduser().absolute() if args.claude_home else None
    try:
        install(*paths, apply=args.apply, claude_home=claude_home)
    except (ValueError, OSError) as exc:
        # JSON parsing errors include locations, not configuration contents.
        print(f"Installation stopped: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
