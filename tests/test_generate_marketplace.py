from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.generate_marketplace import generate_marketplace


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "source" / "skills"


class GenerateMarketplaceTest(unittest.TestCase):
    def test_end_to_end_generation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="marketplace-test-") as temp_dir:
            output_root = Path(temp_dir) / "output"
            report = generate_marketplace(
                source_root=FIXTURE_ROOT,
                output_root=output_root,
                marketplace_name="fixture-marketplace",
                owner_name="Fixture Owner",
            )

            self.assertEqual(report["total_source_skills"], 4)
            self.assertEqual(report["generated_count"], 3)
            self.assertEqual(report["skipped_count"], 1)
            self.assertGreaterEqual(report["normalized_skill_files"], 2)

            marketplace = json.loads(
                (output_root / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
            )
            self.assertEqual(marketplace["name"], "fixture-marketplace")
            plugin_names = [plugin["name"] for plugin in marketplace["plugins"]]
            self.assertEqual(
                plugin_names,
                [
                    "owner-one--simple-skill",
                    "owner-three--complex-suite",
                    "owner-two--lowercase-skill",
                ],
            )

            simple_plugin = output_root / "plugins" / "owner-one--simple-skill"
            self.assertTrue((simple_plugin / ".claude-plugin" / "plugin.json").is_file())
            self.assertTrue((simple_plugin / "agents" / "openai.yaml").is_file())
            self.assertTrue((simple_plugin / "hooks" / "hooks.json").is_file())
            self.assertTrue(
                (simple_plugin / "skills" / "simple-skill" / "references" / "guide.md").is_file()
            )
            self.assertTrue((simple_plugin / "skills" / "simple-skill" / "SKILL.md").is_file())

            lowercase_skill = (
                output_root
                / "plugins"
                / "owner-two--lowercase-skill"
                / "skills"
                / "lowercase-skill"
                / "SKILL.md"
            )
            self.assertTrue(lowercase_skill.is_file())
            self.assertNotIn(
                "skill.md",
                {path.name for path in lowercase_skill.parent.iterdir()},
            )

            complex_plugin = output_root / "plugins" / "owner-three--complex-suite"
            self.assertTrue((complex_plugin / "templates" / "base.md").is_file())
            self.assertTrue((complex_plugin / "hooks" / "hooks.json").is_file())
            self.assertTrue((complex_plugin / "skills" / "complex-suite" / "SKILL.md").is_file())
            self.assertTrue((complex_plugin / "skills" / "helper" / "SKILL.md").is_file())

            complex_text = (
                complex_plugin / "skills" / "complex-suite" / "SKILL.md"
            ).read_text(encoding="utf-8")
            self.assertIn("../../templates/base.md", complex_text)
            self.assertIn("../../hooks/hooks.json", complex_text)
            self.assertIn("Generated note: shared plugin assets", complex_text)

            report_json = json.loads(
                (output_root / "reports" / "generate-marketplace.json").read_text(encoding="utf-8")
            )
            self.assertEqual(len(report_json["skipped"]), 1)
            self.assertEqual(report_json["skipped"][0]["source"], "owner-four/missing-skill")


if __name__ == "__main__":
    unittest.main()

