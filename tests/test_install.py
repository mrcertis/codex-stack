import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("installer", ROOT / "scripts/install_config.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)
start_spec = importlib.util.spec_from_file_location("prepare", ROOT / "skills/stack-start/scripts/prepare_project.py")
prepare = importlib.util.module_from_spec(start_spec)
start_spec.loader.exec_module(prepare)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="stack test ")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name).resolve() / "codex home"
        self.home.mkdir()
        self.tools = Path(self.temp.name) / "Tools"
        self.wiki = Path(self.temp.name) / "LLM Wiki"

    def install(self, apply=True):
        installer.install(self.home, self.tools, self.wiki, apply=apply)

    def test_replace_preserve_backup_and_idempotency(self):
        (self.home / "AGENTS.md").write_text("Old unique instruction")
        (self.home / "config.toml").write_text('model = "test"')
        (self.home / "PROJECTS.md").write_text("private registry")
        other = {"hooks": [{"type": "command", "command": "echo other"}]}
        (self.home / "hooks.json").write_text(json.dumps({"extra": True, "hooks": {"UserPromptSubmit": [other]}}))
        self.install(apply=False)
        self.assertEqual((self.home / "AGENTS.md").read_text(), "Old unique instruction")
        self.assertFalse((self.home / "stack-backups").exists())
        self.install()
        agents = (self.home / "AGENTS.md").read_text()
        self.assertNotIn("Old unique instruction", agents)
        self.assertNotIn("<WIKI_ROOT>", agents)
        self.assertIn(str(self.wiki), agents)
        self.assertEqual((self.home / "config.toml").read_text(), 'model = "test"')
        self.assertEqual((self.home / "PROJECTS.md").read_text(), "private registry")
        hooks = json.loads((self.home / "hooks.json").read_text())
        self.assertTrue(hooks["extra"])
        self.assertEqual(hooks["hooks"]["UserPromptSubmit"][0], other)
        self.assertEqual(len(hooks["hooks"]["UserPromptSubmit"]), 2)
        command = hooks["hooks"]["SessionStart"][0]["hooks"][0]["command"]
        output = subprocess.run(command, shell=True, input='{"hook_event_name":"SessionStart"}',
                                text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(output.stdout)["hookSpecificOutput"]["hookEventName"], "SessionStart")
        self.assertIn(str(self.home / "skills/stack-start/SKILL.md"), output.stdout)
        self.assertTrue((self.home / "skills/stack-start/scripts/prepare_project.py").is_file())
        self.install()
        self.assertEqual(hooks, json.loads((self.home / "hooks.json").read_text()))
        backups = list((self.home / "stack-backups").iterdir())
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "0-AGENTS.md").read_text(), "Old unique instruction")

    def test_invalid_manifest_leaves_agents_untouched(self):
        (self.home / "AGENTS.md").write_text("old")
        for text in ("invalid", "[]", '{"hooks": []}', '{"hooks":{"Stop":[{}]}}'):
            (self.home / "hooks.json").write_text(text)
            with self.assertRaises(ValueError):
                self.install()
            self.assertEqual((self.home / "AGENTS.md").read_text(), "old")
            self.assertFalse((self.home / "stack-backups").exists())

    def test_override_and_symlink_refused(self):
        override = self.home / "AGENTS.override.md"
        override.write_text("override")
        with self.assertRaises(ValueError):
            self.install()
        override.unlink()
        target = Path(self.temp.name) / "original"
        target.write_text("preserve")
        (self.home / "AGENTS.md").symlink_to(target)
        with self.assertRaises(ValueError):
            self.install()
        self.assertEqual(target.read_text(), "preserve")

    def test_hook_events_and_no_input_echo(self):
        for event in ("SessionStart", "UserPromptSubmit", "PostCompact", "Stop"):
            output = subprocess.run([sys.executable, str(ROOT / "hooks/stack-context.py")],
                                    input=json.dumps({"hook_event_name": event, "prompt": "PRIVATE_SENTINEL"}),
                                    capture_output=True, text=True, check=True).stdout
            self.assertNotIn("PRIVATE_SENTINEL", output)
            data = json.loads(output) if output else {}
            if event == "PostCompact":
                self.assertEqual(set(data), {"systemMessage"})
            elif event == "Stop":
                self.assertFalse(data)
            else:
                self.assertEqual(data["hookSpecificOutput"]["hookEventName"], event)

    def test_project_preparation_preserves_installed_set(self):
        for name in (*prepare.INTERVIEW, "impeccable"):
            skill = self.home / ".agents/skills" / name / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("existing content")
        with patch.object(prepare.subprocess, "run") as run:
            prepare.prepare(self.home)
            run.assert_not_called()
        self.assertEqual((self.home / ".agents/skills/impeccable/SKILL.md").read_text(), "existing content")

    def test_project_preparation_refuses_distribution_and_partial_skill(self):
        with patch.object(prepare.subprocess, "run") as run:
            with self.assertRaises(ValueError):
                prepare.prepare(ROOT)
            (self.home / ".agents/skills/impeccable").mkdir(parents=True)
            with self.assertRaises(ValueError):
                prepare.prepare(self.home)
            run.assert_not_called()

    def test_claude_block_settings_and_idempotency(self):
        home = Path(self.temp.name).resolve() / "claude home"
        home.mkdir()
        (home / "CLAUDE.md").write_text("# Mine\nKeep this instruction\n")
        other = {"matcher": "Bash", "hooks": [{"type": "command", "command": "echo other"}]}
        settings = {"model": "keep", "permissions": {"allow": ["Bash(ls)"]}, "hooks": {"PreToolUse": [other]}}
        (home / "settings.json").write_text(json.dumps(settings))
        installer.install(home, self.tools, self.wiki, apply=False, host="claude")
        self.assertFalse((home / "stack-backups").exists())
        installer.install(home, self.tools, self.wiki, apply=True, host="claude")
        rules = (home / "CLAUDE.md").read_text()
        self.assertTrue(rules.startswith("# Mine\nKeep this instruction\n\n" + installer.BEGIN))
        self.assertIn("Ты — Claude Code", rules)
        self.assertIn(str(home / "skills/stack-start/SKILL.md"), rules)
        self.assertNotIn("<WIKI_ROOT>", rules)
        self.assertNotIn("~/.claude", rules)
        data = json.loads((home / "settings.json").read_text())
        self.assertEqual(data["model"], "keep")
        self.assertEqual(data["permissions"], settings["permissions"])
        self.assertEqual(data["hooks"]["PreToolUse"], [other])
        self.assertEqual(set(data["hooks"]), {"PreToolUse", "SessionStart", "UserPromptSubmit"})
        command = data["hooks"]["SessionStart"][0]["hooks"][0]["command"]
        self.assertTrue(command.endswith("--host claude"))
        output = subprocess.run(command, shell=True, input='{"hook_event_name":"SessionStart","source":"compact"}',
                                text=True, capture_output=True, check=True)
        self.assertIn("global CLAUDE.md", json.loads(output.stdout)["hookSpecificOutput"]["additionalContext"])
        # A rerun after a template change rewrites only the marked block.
        (home / "CLAUDE.md").write_text(rules.replace("Ты — Claude Code", "stale") + "After block\n")
        installer.install(home, self.tools, self.wiki, apply=True, host="claude")
        rerun = (home / "CLAUDE.md").read_text()
        self.assertEqual(rerun, rules + "After block\n")
        self.assertEqual(data, json.loads((home / "settings.json").read_text()))
        self.assertFalse((home / "AGENTS.md").exists())

    def test_claude_broken_markers_refused(self):
        home = Path(self.temp.name).resolve() / "claude home"
        home.mkdir()
        for text in (installer.BEGIN + "\nno end\n", (installer.BEGIN + installer.END) * 2,
                     installer.END + installer.BEGIN):
            (home / "CLAUDE.md").write_text(text)
            with self.assertRaises(ValueError):
                installer.install(home, self.tools, self.wiki, apply=True, host="claude")
            self.assertEqual((home / "CLAUDE.md").read_text(), text)

    def test_claude_hook_has_no_post_compact(self):
        output = subprocess.run([sys.executable, str(ROOT / "hooks/stack-context.py"), "--host", "claude"],
                                input='{"hook_event_name":"PostCompact"}', capture_output=True, text=True, check=True)
        self.assertEqual(output.stdout, "")

    def test_claude_project_preparation_uses_claude_paths(self):
        def fake_run(args, cwd, check):
            names = args[args.index("--skill") + 1:args.index("--copy")] if "--skill" in args else ["impeccable"]
            for name in names:
                skill = Path(cwd) / ".claude/skills" / name / "SKILL.md"
                skill.parent.mkdir(parents=True)
                skill.write_text("installed")
        with patch.object(prepare.subprocess, "run", side_effect=fake_run) as run:
            prepare.prepare(self.home, "claude")
        self.assertIn("claude-code", run.call_args_list[0].args[0])
        self.assertIn("--providers=claude", run.call_args_list[1].args[0])
        self.assertFalse((self.home / ".agents").exists())


if __name__ == "__main__":
    unittest.main()
