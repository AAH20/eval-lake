"""
ETL Parser for Ingesting Multi-format LLM & Agent Traces.
Supports JSONL, OpenTelemetry GenAI Semantic Conventions, and Agent Trajectories.
"""

import json
from typing import List, Dict, Any, Union
from pathlib import Path
from evallake.etl.schema import TraceEvent, ToolInvocation, TokenUsage


class TraceParser:
    """Parses heterogeneous AI trace formats into canonical TraceEvent records."""

    @staticmethod
    def parse_jsonl(filepath: Union[str, Path]) -> List[TraceEvent]:
        events: List[TraceEvent] = []
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Trace file not found: {filepath}")

        with open(path, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f, start=1):
                clean = line.strip()
                if not clean:
                    continue
                try:
                    data = json.loads(clean)
                    event = TraceParser.normalize_record(data, fallback_id=f"trace_{line_idx}")
                    events.append(event)
                except json.JSONDecodeError as err:
                    # Non-fatal log or raise
                    continue
        return events

    @staticmethod
    def normalize_record(record: Dict[str, Any], fallback_id: str = "trace_0") -> TraceEvent:
        # Check if OpenTelemetry GenAI format
        if "attributes" in record or "resourceSpans" in record:
            return TraceParser._normalize_otel(record, fallback_id)

        # Standard / Canonical format
        trace_id = str(record.get("trace_id") or record.get("id") or fallback_id)
        timestamp = str(record.get("timestamp") or record.get("created_at") or "2026-09-19T00:00:00Z")
        model_name = str(record.get("model") or record.get("model_name") or "unknown-model")
        model_version = str(record.get("model_version") or record.get("version") or "v1")
        prompt = str(record.get("prompt") or record.get("input") or "")
        response = str(record.get("response") or record.get("output") or "")
        latency_ms = float(record.get("latency_ms") or record.get("duration_ms") or 0.0)
        
        # Token usage
        raw_usage = record.get("token_usage") or record.get("usage") or {}
        p_tokens = int(raw_usage.get("prompt_tokens") or raw_usage.get("input_tokens") or 0)
        c_tokens = int(raw_usage.get("completion_tokens") or raw_usage.get("output_tokens") or 0)
        tot_tokens = int(raw_usage.get("total_tokens") or (p_tokens + c_tokens))
        
        # Cost estimate: ~$2.50/M prompt, $10.00/M completion as baseline if not provided
        cost = float(raw_usage.get("estimated_cost_usd") or (p_tokens * 2.5e-6 + c_tokens * 1.0e-5))
        usage = TokenUsage(prompt_tokens=p_tokens, completion_tokens=c_tokens, total_tokens=tot_tokens, estimated_cost_usd=cost)

        # Tool calls
        tool_calls: List[ToolInvocation] = []
        raw_tools = record.get("tool_calls") or record.get("tools") or []
        for t in raw_tools:
            if isinstance(t, dict):
                t_name = str(t.get("tool_name") or t.get("name") or t.get("function", {}).get("name", "unknown_tool"))
                args = t.get("arguments") or t.get("args") or t.get("function", {}).get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except Exception:
                        args = {"raw": args}
                tool_calls.append(ToolInvocation(
                    tool_name=t_name,
                    arguments=args if isinstance(args, dict) else {"value": args},
                    output=t.get("output") or t.get("result"),
                    error=t.get("error"),
                    duration_ms=float(t.get("duration_ms", 0.0))
                ))

        metadata = record.get("metadata") or {}
        error = record.get("error")

        return TraceEvent(
            trace_id=trace_id,
            timestamp=timestamp,
            model_name=model_name,
            model_version=model_version,
            prompt=prompt,
            response=response,
            latency_ms=latency_ms,
            token_usage=usage,
            tool_calls=tool_calls,
            metadata=metadata,
            error=error
        )

    @staticmethod
    def _normalize_otel(record: Dict[str, Any], fallback_id: str) -> TraceEvent:
        attrs = record.get("attributes", {})
        trace_id = str(record.get("traceId") or fallback_id)
        model = str(attrs.get("gen_ai.request.model") or attrs.get("gen_ai.response.model") or "otel-llm")
        prompt = str(attrs.get("gen_ai.prompt") or "")
        response = str(attrs.get("gen_ai.completion") or "")
        p_tokens = int(attrs.get("gen_ai.usage.input_tokens") or attrs.get("gen_ai.usage.prompt_tokens") or 0)
        c_tokens = int(attrs.get("gen_ai.usage.output_tokens") or attrs.get("gen_ai.usage.completion_tokens") or 0)
        latency = float(record.get("durationNano", 0)) / 1e6 if record.get("durationNano") else 0.0

        usage = TokenUsage(
            prompt_tokens=p_tokens,
            completion_tokens=c_tokens,
            total_tokens=p_tokens + c_tokens,
            estimated_cost_usd=(p_tokens * 2.5e-6 + c_tokens * 1.0e-5)
        )

        return TraceEvent(
            trace_id=trace_id,
            timestamp=str(record.get("startTimeUnixNano") or "2026-09-19T00:00:00Z"),
            model_name=model,
            prompt=prompt,
            response=response,
            latency_ms=latency,
            token_usage=usage,
            tool_calls=[],
            metadata=attrs
        )
