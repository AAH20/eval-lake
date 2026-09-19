import unittest
import tempfile
import os
import shutil
from evallake.cli import run_eval_pipeline


class TestCLI(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.traces_file = os.path.join(self.test_dir, "test_traces.jsonl")
        with open(self.traces_file, "w", encoding="utf-8") as f:
            f.write('{"trace_id": "c1", "timestamp": "2026-09-19T00:00:00Z", "model": "test-model", "prompt": "Hello", "response": "Hi", "latency_ms": 120.0, "usage": {"prompt_tokens": 10, "completion_tokens": 5}, "tool_calls": []}\n')

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_run_eval_pipeline_end_to_end(self):
        out_dir = os.path.join(self.test_dir, "artifacts")
        receipt = run_eval_pipeline(self.traces_file, output_dir=out_dir, sign_receipt=True)

        self.assertEqual(receipt.total_traces, 1)
        self.assertTrue(receipt.pass_rate > 0.0)

        # Check generated artifacts
        self.assertTrue(os.path.exists(os.path.join(out_dir, "evaluation_receipt.json")))
        self.assertTrue(os.path.exists(os.path.join(out_dir, "compliance_dossier.md")))
        self.assertTrue(os.path.exists(os.path.join(out_dir, "compliance_dossier.html")))
        self.assertTrue(os.path.exists(os.path.join(out_dir, "oax_signed_envelope.json")))
        self.assertTrue(os.path.exists(os.path.join(out_dir, "public_key.pub")))


if __name__ == "__main__":
    unittest.main()
