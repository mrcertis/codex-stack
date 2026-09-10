import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("installer", ROOT / "scripts/install_config.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


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


if __name__ == "__main__":
    unittest.main()
