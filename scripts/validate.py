#!/usr/bin/env python3
"""Check the public distribution without reading any user configuration."""

from pathlib import Path
import re
import sys
import tomllib
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "README.md", "AGENTS.md", "plugins.md", "NOTICE.md", "LICENSE", ".gitignore",
    "global-config/AGENTS.md", "global-config/PROJECTS.example.md",
    "global-config/mcp.example.toml", "docs/AGENT-SETUP.md", "docs/INSTALL.md",
    "docs/USAGE.md", "docs/VERIFY.md", "scripts/validate.py",
}
errors = []
for name in sorted(EXPECTED):
    path = ROOT / name
    if not path.is_file():
        errors.append(f"Missing: {name}")
        continue
    content = path.read_text(encoding="utf-8")
    if name.endswith(".md"):
        for target in re.findall(r"\]\(([^)]+)\)", content):
            if target.startswith(("https://", "http://", "#", "mailto:")):
                continue
            relative = unquote(target.split("#", 1)[0])
            if relative and not (path.parent / relative).is_file():
                errors.append(f"Broken local link in {name}: {target}")
    if name.endswith(".toml"):
        try:
            tomllib.loads(content)
        except tomllib.TOMLDecodeError as exc:
            errors.append(f"Invalid TOML in {name}: {exc}")
    # Focused accidental-disclosure checks, not a complete secrets audit.
    if name != "scripts/validate.py":
        for pattern in (r"/Users/[^/\s]+/", r"gh[pousr]_[A-Za-z0-9]{20,}",
                        r"ctx7sk-[A-Za-z0-9_-]{12,}", r"sk-[A-Za-z0-9_-]{24,}",
                        r"-----BEGIN .*PRIVATE KEY-----"):
            if re.search(pattern, content):
                errors.append(f"Possible private data in {name}")

for path in ROOT.rglob("*"):
    if ".git" in path.relative_to(ROOT).parts:
        continue
    if path.is_symlink():
        errors.append(f"Unexpected symlink: {path.relative_to(ROOT)}")
    elif path.is_file() and path.relative_to(ROOT).as_posix() not in EXPECTED:
        errors.append(f"Unreviewed publication file: {path.relative_to(ROOT)}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
print(f"PASS: {len(EXPECTED)} public files; local links, TOML and disclosure checks")
