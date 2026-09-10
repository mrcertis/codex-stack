#!/usr/bin/env python3
"""Prepare the explicitly selected new project's local skill set."""

import argparse
from pathlib import Path
import subprocess

INTERVIEW = ("grill-with-docs", "grilling", "domain-modeling")


def prepare(project):
    project = project.expanduser().resolve(strict=True)
    if not project.is_dir() or project == Path.home() or project == Path(project.anchor):
        raise ValueError("Choose the actual project directory")
    if (project / "scripts/install_config.py").exists() and (project / "global-config/AGENTS.md").exists():
        raise ValueError("Choose the new project, not the Codex Stack distribution")
    skills = project / ".agents/skills"
    for path in (project / ".agents", skills, project / ".codex"):
        if path.is_symlink():
            raise ValueError(f"Project configuration symlink needs review: {path}")
    for name in (*INTERVIEW, "impeccable"):
        path = skills / name
        if path.is_symlink() or (path.exists() and not (path / "SKILL.md").is_file()):
            raise ValueError(f"Existing skill needs review before installation: {path}")
    missing = [name for name in INTERVIEW if not (skills / name / "SKILL.md").is_file()]
    if missing:
        subprocess.run(["npx", "--yes", "skills@latest", "add", "mattpocock/skills",
                        "--agent", "codex", "--skill", *missing, "--copy", "--yes"],
                       cwd=project, check=True)
    if not (skills / "impeccable/SKILL.md").is_file():
        subprocess.run(["npx", "--yes", "impeccable@latest", "install",
                        "--providers=codex", "--scope=project", "--yes"], cwd=project, check=True)
    absent = [name for name in (*INTERVIEW, "impeccable") if not (skills / name / "SKILL.md").is_file()]
    if absent:
        raise ValueError("Installer did not create expected local skills: " + ", ".join(absent))
    print("Local starting set ready: " + ", ".join((*INTERVIEW, "impeccable")))
    print("Read local skills now. Codex discovery and hook trust require separate verification.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    args = parser.parse_args()
    try:
        prepare(args.project)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"Project preparation stopped: {exc}\n")
