"""
Deterministic Evaluation Suite.
Tests schema adherence, tool invocation syntax, and agent execution loop detection.
"""

from typing import List, Dict, Any
import json
from evallake.etl.schema import TraceEvent, EvaluationRecord


class DeterministicEvaluator:
    """Evaluates non-probabilistic invariants across agent traces."""

    @staticmethod
    def evaluate_tool_syntax(traces: List[TraceEvent]) -> EvaluationRecord:
        """Verifies that all tool calls contain valid arguments and no unhandled syntax errors."""
        total_calls = 0
        failed_calls = 0
        failures = []

        for trace in traces:
            for tc in trace.tool_calls:
                total_calls += 1
                if tc.error:
                    failed_calls += 1
                    failures.append({"trace_id": trace.trace_id, "tool": tc.tool_name, "error": tc.error})
                elif not isinstance(tc.arguments, dict):
                    failed_calls += 1
                    failures.append({"trace_id": trace.trace_id, "tool": tc.tool_name, "error": "Arguments not a valid object"})

        pass_rate = 1.0 if total_calls == 0 else (total_calls - failed_calls) / total_calls
        passed = failed_calls == 0
        
        return EvaluationRecord(
            test_id="DET-TOOL-001",
            category="deterministic",
            metric_name="tool_call_syntax_fidelity",
            passed=passed,
            score=round(pass_rate, 4),
            threshold=1.0,
            details={"total_calls": total_calls, "failed_calls": failed_calls, "sample_failures": failures[:5]},
            message="All tool calls have valid syntax" if passed else f"Found {failed_calls} malformed tool calls"
        )

    @staticmethod
    def evaluate_loop_prevention(traces: List[TraceEvent], max_repeat: int = 2) -> EvaluationRecord:
        """Detects if an agent got stuck calling the same tool with identical arguments consecutively."""
        loop_traces = []
        for trace in traces:
            calls = trace.tool_calls
            if len(calls) < 2:
                continue
            repeat_count = 1
            for i in range(1, len(calls)):
                prev = calls[i - 1]
                curr = calls[i]
                if prev.tool_name == curr.tool_name and prev.arguments == curr.arguments:
                    repeat_count += 1
                    curr.is_loop = True
                    if repeat_count >= max_repeat:
                        loop_traces.append({
                            "trace_id": trace.trace_id,
                            "tool": curr.tool_name,
                            "repeats": repeat_count
                        })
                        break
                else:
                    repeat_count = 1

        total = len(traces)
        loops = len(loop_traces)
        score = 1.0 if total == 0 else (total - loops) / total
        passed = loops == 0

        return EvaluationRecord(
            test_id="DET-LOOP-002",
            category="deterministic",
            metric_name="agent_trajectory_loop_freedom",
            passed=passed,
            score=round(score, 4),
            threshold=0.98,
            details={"traces_with_loops": loops, "loop_samples": loop_traces[:5]},
            message="No infinite agent trajectory loops detected" if passed else f"Detected {loops} traces with infinite tool loops"
        )

    @staticmethod
    def evaluate_error_rate(traces: List[TraceEvent], max_allowed_error_rate: float = 0.05) -> EvaluationRecord:
        """Evaluates server and runtime error rate over trace population."""
        total = len(traces)
        if total == 0:
            return EvaluationRecord(
                test_id="DET-ERR-003",
                category="deterministic",
                metric_name="runtime_error_resilience",
                passed=True,
                score=1.0,
                threshold=1.0 - max_allowed_error_rate,
                details={"total": 0, "errors": 0},
                message="No traces evaluated"
            )

        errors = sum(1 for t in traces if t.error is not None)
        success_rate = (total - errors) / total
        passed = (errors / total) <= max_allowed_error_rate

        return EvaluationRecord(
            test_id="DET-ERR-003",
            category="deterministic",
            metric_name="runtime_error_resilience",
            passed=passed,
            score=round(success_rate, 4),
            threshold=round(1.0 - max_allowed_error_rate, 4),
            details={"total_traces": total, "error_count": errors, "error_rate": round(errors / total, 4)},
            message=f"Error rate {round(errors/total*100, 2)}% within tolerance {round(max_allowed_error_rate*100, 2)}%" if passed else f"Error rate {round(errors/total*100, 2)}% exceeded threshold"
        )
