#!/usr/bin/env python3
"""Install Impeccable locally into the explicitly selected new project."""

import argparse
from pathlib import Path
import subprocess

SKILL_DIRS = {"codex": ".agents/skills", "claude": ".claude/skills"}


def prepare(project, host="codex"):
    project = project.expanduser().resolve(strict=True)
    if not project.is_dir() or project == Path.home() or project == Path(project.anchor):
        raise ValueError("Choose the actual project directory")
    if (project / "scripts/install_config.py").exists() and (project / "global-config/AGENTS.md").exists():
        raise ValueError("Choose the new project, not the Codex Stack distribution")
    skills = project / SKILL_DIRS[host]
    for path in (skills.parent, skills, project / ".codex"):
        if path.is_symlink():
            raise ValueError(f"Project configuration symlink needs review: {path}")
    skill = skills / "impeccable"
    if skill.is_symlink() or (skill.exists() and not (skill / "SKILL.md").is_file()):
        raise ValueError(f"Existing skill needs review before installation: {skill}")
    if not (skill / "SKILL.md").is_file():
        subprocess.run(["npx", "--yes", "impeccable@latest", "install",
                        f"--providers={host}", "--scope=project", "--yes"], cwd=project, check=True)
    if not (skill / "SKILL.md").is_file():
        raise ValueError(f"Installer did not create {skill}/SKILL.md")
    print(f"Impeccable ready: {skill}")
    print("Next: gsd-new-project. Skill discovery and hook trust require separate verification.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--host", choices=sorted(SKILL_DIRS), default="codex")
    args = parser.parse_args()
    try:
        prepare(args.project, args.host)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"Project preparation stopped: {exc}\n")
