#!/usr/bin/env python3
"""Install only the public rules template and own hooks; dry-run by default."""

import argparse
import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shlex
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HOSTS = {
    # Codex: AGENTS.md is replaced entirely; hooks live in hooks.json.
    "codex": {"rules": "AGENTS.md", "template": "global-config/AGENTS.md",
              "hooks": "hooks.json", "home": "~/.codex",
              "events": ("SessionStart", "UserPromptSubmit", "PostCompact")},
    # Claude Code: a marked block in CLAUDE.md; hooks are a key of settings.json.
    # SessionStart also fires after compact, so no PostCompact handler is needed.
    "claude": {"rules": "CLAUDE.md", "template": "global-config/CLAUDE.md",
               "hooks": "settings.json", "home": "~/.claude",
               "events": ("SessionStart", "UserPromptSubmit")},
}
BEGIN = "<!-- codex-stack:begin -->"
END = "<!-- codex-stack:end -->"


def check_path(path):
    for candidate in (path, *path.parents):
        if candidate.is_symlink():
            raise ValueError(f"Symlink requires manual review: {candidate}")
    if path.exists() and not path.is_file():
        raise ValueError(f"Expected a regular file: {path}")


def merge_hooks(data, command, events_to_add=HOSTS["codex"]["events"]):
    if not isinstance(data, dict) or not isinstance(data.get("hooks", {}), dict):
        raise ValueError("Hook configuration must contain an object of events")
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
    for event in events_to_add:
        groups = events.setdefault(event, [])
        # Only our exact command belongs to this installer; preserve all others.
        groups[:] = [group for group in groups if group != {
            "hooks": [{"type": "command", "command": command, "timeout": 10}]
        }]
        groups.append({"hooks": [{"type": "command", "command": command, "timeout": 10}]})
    return result


def merge_block(existing, block):
    """Replace or append only the stack's marked block, keeping other CLAUDE.md content."""
    wrapped = f"{BEGIN}\n{block.rstrip()}\n{END}\n"
    if not existing.strip():
        return wrapped
    if existing.count(BEGIN) != existing.count(END) or existing.count(BEGIN) > 1:
        raise ValueError("CLAUDE.md has broken or duplicate Codex Stack markers; review it manually")
    if BEGIN not in existing:
        return existing.rstrip("\n") + "\n\n" + wrapped
    start, end = existing.index(BEGIN), existing.index(END) + len(END)
    if end - len(END) < start:
        raise ValueError("CLAUDE.md has broken or duplicate Codex Stack markers; review it manually")
    tail = existing[end:]
    return existing[:start] + wrapped + (tail[1:] if tail.startswith("\n") else tail)


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


def install(home, tools_root, wiki_root, apply=False, host="codex"):
    spec = HOSTS[host]
    targets = [home / spec["rules"], home / spec["hooks"],
               home / "hooks/codex-stack/stack-context.py",
               home / "skills/stack-start/SKILL.md",
               home / "skills/stack-start/scripts/prepare_project.py"]
    if host == "codex" and (home / "AGENTS.override.md").exists():
        raise ValueError("AGENTS.override.md shadows AGENTS.md; review and archive it explicitly first")
    for path in targets:
        check_path(path)
    data = json.loads(targets[1].read_text()) if targets[1].exists() else {}
    command = f"{shlex.quote(sys.executable)} {shlex.quote(str(targets[2]))}"
    if host != "codex":
        command += f" --host {host}"
    merged = merge_hooks(data, command, spec["events"])
    template = (ROOT / spec["template"]).read_text()
    template = template.replace("<TOOLS_ROOT>", str(tools_root)).replace("<WIKI_ROOT>", str(wiki_root))
    template = template.replace(spec["home"], str(home))
    if host == "claude":
        template = merge_block(targets[0].read_text() if targets[0].exists() else "", template)
    contents = [template, json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
                (ROOT / "hooks/stack-context.py").read_text(),
                (ROOT / "skills/stack-start/SKILL.md").read_text(),
                (ROOT / "skills/stack-start/scripts/prepare_project.py").read_text()]
    changes = [(path, content) for path, content in zip(targets, contents)
               if not path.exists() or path.read_text() != content]
    for path, _ in changes:
        print(f"{'INSTALL' if apply else 'DRY RUN'}: {path}")
    if not apply or not changes:
        return
    # Backup is private, outside the source checkout, and created before any replacement.
    if home == ROOT or ROOT in home.parents:
        raise ValueError("The agent home must be outside the public checkout")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup = home / "stack-backups" / stamp
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
    if host == "claude":
        print("Installed files only. Review hooks with /hooks in Claude Code, then test a new session.")
    else:
        print("Installed files only. Review and trust hooks in Codex, then test a new session.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=sorted(HOSTS), default="claude")
    parser.add_argument("--claude-home", type=Path, default=Path(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude")))
    parser.add_argument("--codex-home", type=Path, default=Path(os.environ.get("CODEX_HOME", "~/.codex")))
    parser.add_argument("--tools-root", type=Path, default=Path("~/Documents/Codex/Tools"))
    parser.add_argument("--wiki-root", type=Path, default=Path("~/Documents/Codex/Knowledge/LLM Wiki"))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    home = args.claude_home if args.host == "claude" else args.codex_home
    paths = [path.expanduser().absolute() for path in (home, args.tools_root, args.wiki_root)]
    try:
        install(*paths, apply=args.apply, host=args.host)
    except (ValueError, OSError) as exc:
        # JSON parsing errors include locations, not configuration contents.
        print(f"Installation stopped: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
