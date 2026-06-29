import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "skills" / "product-core" / "scripts" / "product_memory.py"


class ProductMemoryTests(unittest.TestCase):
    project = "automated-test-project"

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_root = Path(self.temp_dir.name)
        for directory in ("config", "templates", "knowledge"):
            shutil.copytree(ROOT / directory, self.test_root / directory)

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_cli(self, *args, input_text=None):
        environment = os.environ.copy()
        environment["PRODUCT_COPILOT_ROOT"] = str(self.test_root)
        return subprocess.run(
            ["python3", str(CLI), *args],
            cwd=ROOT,
            input=input_text,
            text=True,
            capture_output=True,
            env=environment,
        )

    def test_project_ingest_recall_and_deduplicate(self):
        self.assertEqual(self.run_cli("init-project", "--project", self.project).returncode, 0)
        content = "Refund Service applies a deterministic idempotency key for every refund request."
        first = self.run_cli(
            "ingest-text", "--project", self.project, "--source", "confluence://refunds", input_text=content
        )
        second = self.run_cli(
            "ingest-text", "--project", self.project, "--source", "confluence://refunds", input_text=content
        )
        self.assertEqual(json.loads(first.stdout)["chunks_added"], 1)
        self.assertEqual(json.loads(second.stdout)["duplicates_skipped"], 1)
        recalled = self.run_cli(
            "recall", "--project", self.project, "--query", "refund idempotency", "--budget", "1000"
        )
        self.assertIn("idempotency key", recalled.stdout)
        self.assertIn("Context characters used:", recalled.stdout)
        self.assertIn("Estimated context tokens:", recalled.stdout)

    def test_governed_fact_requires_proposal(self):
        result = self.run_cli(
            "learn",
            "--project",
            self.project,
            "--kind",
            "business-rule",
            "--statement",
            "Refunds expire.",
            "--source",
            "ticket-1",
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("requires `propose`", result.stderr)

    def test_template_gate(self):
        result = self.run_cli("template-status", "--type", "ticket")
        manifest = json.loads(result.stdout)
        self.assertTrue(manifest["installed"])
        self.assertTrue(manifest["exactly_one_requirement_variant"])

    def test_ticket_requires_exactly_one_requirement_variant(self):
        metadata = """project: demo
sources: [source-1]
assumptions: []
generated_at: 2026-06-29
trace_id: trace-1
"""
        valid_ticket = metadata + """
# Context
Need a change.
# Requirement
## Product
User sees the updated state.
# Acceptance Criteria
Given a user, when they act, then the state is updated.
"""
        invalid_ticket = valid_ticket.replace(
            "# Acceptance Criteria",
            "## Configuration\nUpdate a flag.\n# Acceptance Criteria",
        )
        with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8") as handle:
            handle.write(valid_ticket)
            handle.flush()
            valid = self.run_cli("validate-artifact", "--type", "ticket", "--file", handle.name)
        with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8") as handle:
            handle.write(invalid_ticket)
            handle.flush()
            invalid = self.run_cli("validate-artifact", "--type", "ticket", "--file", handle.name)
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
        self.assertEqual(invalid.returncode, 2)
        self.assertIn("exactly one Requirement variant", invalid.stdout)

    def test_sequence_validation(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8") as handle:
            handle.write(
                """project: demo
sources: [REQ-001]
assumptions: []
generated_at: 2026-01-01
trace_id: trace-1
```mermaid
sequenceDiagram
autonumber
participant U as User
participant A as API
U->>A: Submit REQ-001
A-->>U: Accepted
```
"""
            )
            handle.flush()
            result = self.run_cli("validate-artifact", "--type", "sequence", "--file", handle.name)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(json.loads(result.stdout)["valid"])

    def test_all_artifact_skills_apply_clarification_policy(self):
        for skill in ("write-ticket", "write-prd", "draw-sequence", "analyze-requirement"):
            content = (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("clarification-policy.md", content, skill)
            self.assertIn("Vietnamese", content, skill)


if __name__ == "__main__":
    unittest.main()
