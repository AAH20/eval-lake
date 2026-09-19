"""
Data schema definitions for EvalLake ETL & Analytics.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
import json


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ToolInvocation:
    tool_name: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    output: Optional[str] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    is_loop: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TraceEvent:
    trace_id: str
    timestamp: str
    model_name: str
    model_version: str = "default"
    prompt: str = ""
    response: str = ""
    latency_ms: float = 0.0
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    tool_calls: List[ToolInvocation] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["tool_calls"] = [tc.to_dict() if isinstance(tc, ToolInvocation) else tc for tc in self.tool_calls]
        d["token_usage"] = self.token_usage.to_dict() if isinstance(self.token_usage, TokenUsage) else self.token_usage
        return d


@dataclass
class EvaluationRecord:
    test_id: str
    category: str  # "deterministic", "safety", "semantic", "drift", "governance"
    metric_name: str
    passed: bool
    score: float
    threshold: float
    details: Dict[str, Any] = field(default_factory=dict)
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BatchEvaluationReceipt:
    batch_id: str
    timestamp: str
    dataset_source: str
    total_traces: int
    total_evaluations: int
    passed_evaluations: int
    failed_evaluations: int
    pass_rate: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    total_tokens: int
    total_cost_usd: float
    evaluations: List[EvaluationRecord] = field(default_factory=list)
    compliance_scorecards: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["evaluations"] = [e.to_dict() if isinstance(e, EvaluationRecord) else e for e in self.evaluations]
        return d

    def to_canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
