import unittest
import tempfile
import json
import os
from evallake.etl.parser import TraceParser
from evallake.etl.engine import AnalyticsEngine
from evallake.etl.schema import TraceEvent, ToolInvocation, TokenUsage


class TestETL(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl")
        sample_records = [
            {
                "trace_id": "t1",
                "timestamp": "2026-09-19T00:00:00Z",
                "model": "gpt-4o",
                "prompt": "Hello",
                "response": "World",
                "latency_ms": 100.0,
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                "tool_calls": [{"name": "calculator", "arguments": {"x": 1, "y": 2}}]
            },
            {
                "trace_id": "t2",
                "timestamp": "2026-09-19T00:00:05Z",
                "model": "gpt-4o",
                "prompt": "Test 2",
                "response": "Res 2",
                "latency_ms": 200.0,
                "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
                "tool_calls": []
            }
        ]
        for r in sample_records:
            self.temp_file.write(json.dumps(r) + "\n")
        self.temp_file.close()

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_parse_jsonl(self):
        traces = TraceParser.parse_jsonl(self.temp_file.name)
        self.assertEqual(len(traces), 2)
        self.assertEqual(traces[0].trace_id, "t1")
        self.assertEqual(traces[0].model_name, "gpt-4o")
        self.assertEqual(len(traces[0].tool_calls), 1)
        self.assertEqual(traces[0].tool_calls[0].tool_name, "calculator")
        self.assertEqual(traces[0].token_usage.total_tokens, 15)

    def test_analytics_engine_summary(self):
        traces = TraceParser.parse_jsonl(self.temp_file.name)
        engine = AnalyticsEngine(traces)
        summary = engine.compute_summary()
        self.assertEqual(summary["total_traces"], 2)
        self.assertEqual(summary["total_tokens"], 45)
        self.assertEqual(summary["error_count"], 0)
        self.assertAlmostEqual(summary["p50_latency_ms"], 100.0, places=1)
        self.assertAlmostEqual(summary["p95_latency_ms"], 200.0, places=1)
        self.assertEqual(summary["total_tool_calls"], 1)

    def test_sql_query(self):
        traces = TraceParser.parse_jsonl(self.temp_file.name)
        engine = AnalyticsEngine(traces)
        res = engine.query_sql("SELECT trace_id, latency_ms FROM traces ORDER BY latency_ms DESC")
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]["trace_id"], "t2")


if __name__ == "__main__":
    unittest.main()
