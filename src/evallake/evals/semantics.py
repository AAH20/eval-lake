"""
Semantic and Operational Performance Evaluation Suite.
Verifies latency SLAs, cost ceilings, and response groundedness.
"""

from typing import List, Dict, Any
from evallake.etl.schema import TraceEvent, EvaluationRecord


class SemanticEvaluator:
    """Evaluates latency SLAs, token budgets, and groundedness."""

    @staticmethod
    def evaluate_latency_sla(traces: List[TraceEvent], max_p95_ms: float = 3000.0) -> EvaluationRecord:
        """Verifies that P95 latency satisfies SLA threshold."""
        if not traces:
            return EvaluationRecord(
                test_id="OPS-LAT-001",
                category="semantic",
                metric_name="p95_latency_sla_compliance",
                passed=True,
                score=1.0,
                threshold=max_p95_ms,
                message="No traces evaluated"
            )

        lats = sorted([t.latency_ms for t in traces])
        idx = max(0, int(len(lats) * 0.95) - 1)
        p95 = lats[idx]
        passed = p95 <= max_p95_ms
        score = max(0.0, min(1.0, (max_p95_ms / p95) if p95 > 0 else 1.0))

        return EvaluationRecord(
            test_id="OPS-LAT-001",
            category="semantic",
            metric_name="p95_latency_sla_compliance",
            passed=passed,
            score=round(score, 4),
            threshold=max_p95_ms,
            details={"p95_latency_ms": round(p95, 2), "sla_target_ms": max_p95_ms},
            message=f"P95 latency {round(p95, 2)}ms within SLA ({max_p95_ms}ms)" if passed else f"P95 latency {round(p95, 2)}ms violated SLA ({max_p95_ms}ms)"
        )

    @staticmethod
    def evaluate_cost_budget(traces: List[TraceEvent], max_cost_per_trace_usd: float = 0.05) -> EvaluationRecord:
        """Verifies that average cost per trace is within operational budget."""
        if not traces:
            return EvaluationRecord(
                test_id="OPS-CST-002",
                category="semantic",
                metric_name="unit_economics_cost_governance",
                passed=True,
                score=1.0,
                threshold=max_cost_per_trace_usd,
                message="No traces evaluated"
            )

        tot_cost = sum(t.token_usage.estimated_cost_usd for t in traces)
        avg_cost = tot_cost / len(traces)
        passed = avg_cost <= max_cost_per_trace_usd
        score = max(0.0, min(1.0, (max_cost_per_trace_usd / avg_cost) if avg_cost > 0 else 1.0))

        return EvaluationRecord(
            test_id="OPS-CST-002",
            category="semantic",
            metric_name="unit_economics_cost_governance",
            passed=passed,
            score=round(score, 4),
            threshold=max_cost_per_trace_usd,
            details={"average_cost_usd": round(avg_cost, 6), "budget_cap_usd": max_cost_per_trace_usd},
            message=f"Average cost ${round(avg_cost, 5)} satisfies budget cap (${max_cost_per_trace_usd})" if passed else f"Average cost ${round(avg_cost, 5)} exceeded budget cap"
        )
