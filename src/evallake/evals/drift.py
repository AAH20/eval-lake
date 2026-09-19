"""
Model Evolution and Distribution Drift Evaluation Suite.
Detects performance regression, prompt drift, token inflation, and error shifts.
"""

from typing import List, Dict, Any
from evallake.etl.schema import TraceEvent, EvaluationRecord


class DriftEvaluator:
    """Calculates statistical drift between baseline and candidate trace batches."""

    @staticmethod
    def calculate_drift(baseline: List[TraceEvent], candidate: List[TraceEvent], max_allowed_drift_pct: float = 25.0) -> EvaluationRecord:
        """Compares operational metrics between baseline and candidate trace sets."""
        if not baseline or not candidate:
            return EvaluationRecord(
                test_id="DFT-EVO-001",
                category="drift",
                metric_name="cross_revision_stability",
                passed=True,
                score=1.0,
                threshold=max_allowed_drift_pct,
                message="Insufficient baseline or candidate traces to compute drift"
            )

        # Baseline metrics
        b_n = len(baseline)
        b_latencies = sorted([t.latency_ms for t in baseline])
        b_p95 = b_latencies[int(b_n * 0.95) - 1] if b_n > 0 else 1.0
        b_tokens = sum(t.token_usage.total_tokens for t in baseline) / b_n
        b_err_rate = sum(1 for t in baseline if t.error is not None) / b_n

        # Candidate metrics
        c_n = len(candidate)
        c_latencies = sorted([t.latency_ms for t in candidate])
        c_p95 = c_latencies[int(c_n * 0.95) - 1] if c_n > 0 else 1.0
        c_tokens = sum(t.token_usage.total_tokens for t in candidate) / c_n
        c_err_rate = sum(1 for t in candidate if t.error is not None) / c_n

        # Percentage drifts
        lat_drift_pct = ((c_p95 - b_p95) / b_p95) * 100 if b_p95 > 0 else 0.0
        tok_drift_pct = ((c_tokens - b_tokens) / b_tokens) * 100 if b_tokens > 0 else 0.0
        err_shift_pct = (c_err_rate - b_err_rate) * 100

        # Maximum negative drift observed
        max_observed_drift = max(abs(lat_drift_pct), abs(tok_drift_pct), max(0.0, err_shift_pct * 10))
        passed = (lat_drift_pct <= max_allowed_drift_pct) and (tok_drift_pct <= max_allowed_drift_pct) and (err_shift_pct <= 5.0)
        score = max(0.0, 1.0 - (max_observed_drift / 100.0))

        details = {
            "baseline_p95_ms": round(b_p95, 2),
            "candidate_p95_ms": round(c_p95, 2),
            "latency_drift_pct": round(lat_drift_pct, 2),
            "baseline_avg_tokens": round(b_tokens, 1),
            "candidate_avg_tokens": round(c_tokens, 1),
            "token_drift_pct": round(tok_drift_pct, 2),
            "baseline_error_rate": round(b_err_rate, 4),
            "candidate_error_rate": round(c_err_rate, 4)
        }

        return EvaluationRecord(
            test_id="DFT-EVO-001",
            category="drift",
            metric_name="cross_revision_stability",
            passed=passed,
            score=round(score, 4),
            threshold=max_allowed_drift_pct,
            details=details,
            message=f"Candidate revision within stability envelope (max drift {round(max_observed_drift, 1)}%)" if passed else f"Candidate revision exhibited unacceptable drift ({round(max_observed_drift, 1)}%)"
        )
