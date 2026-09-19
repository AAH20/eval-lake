import unittest
from evallake.crypto.ed25519 import CryptoSigner
from evallake.crypto.oax import sign_evaluation_receipt, verify_evaluation_receipt
from evallake.etl.schema import BatchEvaluationReceipt, EvaluationRecord


class TestCrypto(unittest.TestCase):

    def setUp(self):
        self.priv_key, self.pub_key = CryptoSigner.generate_keypair()
        self.receipt = BatchEvaluationReceipt(
            batch_id="batch_crypto_test",
            timestamp="2026-09-19T06:00:00Z",
            dataset_source="sample.jsonl",
            total_traces=5,
            total_evaluations=1,
            passed_evaluations=1,
            failed_evaluations=0,
            pass_rate=1.0,
            p50_latency_ms=80.0,
            p95_latency_ms=120.0,
            p99_latency_ms=150.0,
            total_tokens=500,
            total_cost_usd=0.005,
            evaluations=[
                EvaluationRecord(test_id="DET-TOOL-001", category="deterministic", metric_name="syntax", passed=True, score=1.0, threshold=1.0)
            ],
            compliance_scorecards={"overall_status": "CONFORMANT"}
        )

    def test_sign_and_verify_valid_receipt(self):
        envelope = sign_evaluation_receipt(self.receipt, self.priv_key, self.pub_key)
        env_dict = {
            "version": envelope.version,
            "envelope_id": envelope.envelope_id,
            "issued_at": envelope.issued_at,
            "payload_digest": envelope.payload_digest,
            "payload": envelope.payload,
            "signer": envelope.signer
        }

        valid, msg = verify_evaluation_receipt(env_dict, self.pub_key)
        self.assertTrue(valid)
        self.assertIn("zero tampering detected", msg)

    def test_tamper_detection_on_payload_alteration(self):
        envelope = sign_evaluation_receipt(self.receipt, self.priv_key, self.pub_key)
        env_dict = {
            "version": envelope.version,
            "envelope_id": envelope.envelope_id,
            "issued_at": envelope.issued_at,
            "payload_digest": envelope.payload_digest,
            "payload": envelope.payload,
            "signer": envelope.signer
        }

        # Maliciously tamper with evaluation results
        env_dict["payload"]["pass_rate"] = 0.50
        valid, msg = verify_evaluation_receipt(env_dict, self.pub_key)
        self.assertFalse(valid)
        self.assertIn("Tamper detected", msg)

    def test_tamper_detection_on_corrupt_signature(self):
        envelope = sign_evaluation_receipt(self.receipt, self.priv_key, self.pub_key)
        env_dict = {
            "version": envelope.version,
            "envelope_id": envelope.envelope_id,
            "issued_at": envelope.issued_at,
            "payload_digest": envelope.payload_digest,
            "payload": envelope.payload,
            "signer": envelope.signer
        }

        # Corrupt signature string
        env_dict["signer"]["signature"] = "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoxMjM0NTY="
        valid, msg = verify_evaluation_receipt(env_dict, self.pub_key)
        self.assertFalse(valid)


if __name__ == "__main__":
    unittest.main()
