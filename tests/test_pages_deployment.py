#!/usr/bin/env python3
"""Contracts for the GitHub Pages artifact assembled for AdMob verification."""

from pathlib import Path
import os
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = ROOT / "scripts" / "build-pages-artifact.sh"
WORKFLOW = ROOT / ".github" / "workflows" / "deploy-pages.yml"
FIXTURE_PUBLISHER_ID = "pub-1234567890"


class PagesDeploymentTest(unittest.TestCase):
    def build_artifact(self, publisher_id: str):
        self.assertTrue(BUILD_SCRIPT.is_file(), "Pages artifact builder is missing")
        temporary_directory = tempfile.TemporaryDirectory()
        artifact_directory = Path(temporary_directory.name) / "artifact"
        environment = os.environ | {"ADMOB_PUBLISHER_ID": publisher_id}
        result = subprocess.run(
            [str(BUILD_SCRIPT), str(artifact_directory)],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        return temporary_directory, artifact_directory, result

    def test_builds_a_root_app_ads_file_without_changing_static_routes(self):
        """Catches a build that omits app-ads.txt or changes the existing site layout."""
        temporary_directory, artifact_directory, result = self.build_artifact(
            FIXTURE_PUBLISHER_ID
        )
        self.addCleanup(temporary_directory.cleanup)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertNotIn(FIXTURE_PUBLISHER_ID, result.stderr)
        self.assertEqual(
            (artifact_directory / "app-ads.txt").read_text(encoding="utf-8"),
            "google.com, pub-1234567890, DIRECT, f08c47fec0942fa0\n",
        )
        self.assertEqual(
            list(artifact_directory.rglob("app-ads.txt")),
            [artifact_directory / "app-ads.txt"],
        )
        self.assertFalse((artifact_directory / "index.html").exists())
        for source_path in ("CNAME", "kr", "jp", "docs"):
            self.assertTrue((artifact_directory / source_path).exists(), source_path)

    def test_rejects_an_invalid_publisher_id_without_echoing_it(self):
        """Catches validation that accepts malformed IDs or leaks supplied values."""
        invalid_publisher_id = "not-a-publisher-id"
        temporary_directory, artifact_directory, result = self.build_artifact(
            invalid_publisher_id
        )
        self.addCleanup(temporary_directory.cleanup)

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("ADMOB_PUBLISHER_ID is missing or invalid.", result.stderr)
        self.assertNotIn(invalid_publisher_id, result.stderr)
        self.assertFalse(artifact_directory.exists())

    def test_workflow_uses_the_pages_actions_with_minimum_permissions(self):
        """Catches a deployment workflow that widens permissions or skips Pages deployment."""
        self.assertTrue(WORKFLOW.is_file(), "Pages deployment workflow is missing")
        workflow = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("contents: read", workflow)
        self.assertIn("pages: write", workflow)
        self.assertIn("id-token: write", workflow)
        self.assertIn('group: "pages"', workflow)
        self.assertIn("cancel-in-progress: false", workflow)
        self.assertIn("actions/checkout@v6", workflow)
        self.assertIn("actions/configure-pages@v5", workflow)
        self.assertIn("actions/upload-pages-artifact@v5", workflow)
        self.assertIn("actions/deploy-pages@v5", workflow)
        self.assertIn("ADMOB_PUBLISHER_ID: ${{ secrets.ADMOB_PUBLISHER_ID }}", workflow)
        self.assertIn("github-pages", workflow)


if __name__ == "__main__":
    unittest.main()
