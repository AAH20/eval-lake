import unittest
from evallake.etl.schema import EvaluationRecord, BatchEvaluationReceipt
from evallake.grc.mapper import ComplianceMapper
from evallake.grc.dossier import ComplianceDossierGenerator


class TestGRC(unittest.TestCase):

    def test_compliance_mapping(self):
        evals = [
            EvaluationRecord(test_id="DET-TOOL-001", category="deterministic", metric_name="syntax", passed=True, score=1.0, threshold=1.0),
            EvaluationRecord(test_id="DET-LOOP-002", category="deterministic", metric_name="loops", passed=True, score=1.0, threshold=0.98),
            EvaluationRecord(test_id="DET-ERR-003", category="deterministic", metric_name="errors", passed=True, score=1.0, threshold=0.95),
            EvaluationRecord(test_id="SAF-PII-001", category="safety", metric_name="pii", passed=True, score=1.0, threshold=1.0),
            EvaluationRecord(test_id="SAF-INJ-002", category="safety", metric_name="injection", passed=True, score=1.0, threshold=1.0),
            EvaluationRecord(test_id="OPS-LAT-001", category="semantic", metric_name="latency", passed=True, score=1.0, threshold=3000.0),
            EvaluationRecord(test_id="OPS-CST-002", category="semantic", metric_name="cost", passed=True, score=1.0, threshold=0.05),
            EvaluationRecord(test_id="DFT-EVO-001", category="drift", metric_name="drift", passed=True, score=1.0, threshold=25.0),
        ]

        scorecard = ComplianceMapper.map_evaluations_to_frameworks(evals)
        self.assertEqual(scorecard["overall_status"], "CONFORMANT")
        self.assertEqual(scorecard["overall_grade"], "A+")
        self.assertIn("eu_ai_act", scorecard["frameworks"])
        self.assertIn("nist_ai_rmf", scorecard["frameworks"])
        self.assertIn("iso_42001", scorecard["frameworks"])
        self.assertEqual(scorecard["frameworks"]["eu_ai_act"]["status"], "CONFORMANT")

    def test_dossier_generation(self):
        receipt = BatchEvaluationReceipt(
            batch_id="batch_test_001",
            timestamp="2026-09-19T06:00:00Z",
            dataset_source="test.jsonl",
            total_traces=10,
            total_evaluations=1,
            passed_evaluations=1,
            failed_evaluations=0,
            pass_rate=1.0,
            p50_latency_ms=100.0,
            p95_latency_ms=150.0,
            p99_latency_ms=200.0,
            total_tokens=1000,
            total_cost_usd=0.01,
            evaluations=[
                EvaluationRecord(test_id="DET-TOOL-001", category="deterministic", metric_name="syntax", passed=True, score=1.0, threshold=1.0, message="OK")
            ],
            compliance_scorecards={"overall_status": "CONFORMANT", "overall_grade": "A+", "aggregate_compliance_score": 1.0, "frameworks": {}}
        )

        md = ComplianceDossierGenerator.generate_markdown(receipt)
        html = ComplianceDossierGenerator.generate_html(receipt)

        self.assertIn("AI System Compliance & Evaluation Dossier", md)
        self.assertIn("batch_test_001", md)
        self.assertIn("<!DOCTYPE html>", html)


if __name__ == "__main__":
    unittest.main()
