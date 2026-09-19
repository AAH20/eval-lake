"""
Analytics Engine for EvalLake ETL.
Provides high-performance columnar aggregations, quantile calculations,
and optional DuckDB query capabilities.
"""

from typing import List, Dict, Any, Optional
import math
import json
from evallake.etl.schema import TraceEvent


class AnalyticsEngine:
    """High-throughput analytics engine for processing LLM and agent traces."""

    def __init__(self, traces: Optional[List[TraceEvent]] = None):
        self.traces: List[TraceEvent] = traces or []
        self._duckdb_available = False
        try:
            import duckdb  # type: ignore
            self._duckdb_available = True
        except ImportError:
            self._duckdb_available = False

    def add_traces(self, new_traces: List[TraceEvent]) -> None:
        self.traces.extend(new_traces)

    def compute_summary(self) -> Dict[str, Any]:
        """Computes comprehensive metrics over all ingested traces."""
        n = len(self.traces)
        if n == 0:
            return {
                "total_traces": 0,
                "error_rate": 0.0,
                "p50_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "p99_latency_ms": 0.0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "total_tool_calls": 0,
                "tool_loop_count": 0,
                "unique_models": []
            }

        latencies = sorted([t.latency_ms for t in self.traces])
        errors = sum(1 for t in self.traces if t.error is not None)
        tot_tokens = sum(t.token_usage.total_tokens for t in self.traces)
        tot_cost = sum(t.token_usage.estimated_cost_usd for t in self.traces)
        
        # Tool call metrics
        all_tools = [tc for t in self.traces for tc in t.tool_calls]
        tool_count = len(all_tools)
        tool_loops = sum(1 for tc in all_tools if tc.is_loop)
        
        models = sorted(list({t.model_name for t in self.traces}))

        return {
            "total_traces": n,
            "error_count": errors,
            "error_rate": round(errors / n, 4),
            "p50_latency_ms": round(self._quantile(latencies, 0.50), 2),
            "p90_latency_ms": round(self._quantile(latencies, 0.90), 2),
            "p95_latency_ms": round(self._quantile(latencies, 0.95), 2),
            "p99_latency_ms": round(self._quantile(latencies, 0.99), 2),
            "total_tokens": tot_tokens,
            "prompt_tokens": sum(t.token_usage.prompt_tokens for t in self.traces),
            "completion_tokens": sum(t.token_usage.completion_tokens for t in self.traces),
            "total_cost_usd": round(tot_cost, 6),
            "total_tool_calls": tool_count,
            "tool_loop_count": tool_loops,
            "unique_models": models
        }

    @staticmethod
    def _quantile(sorted_data: List[float], q: float) -> float:
        if not sorted_data:
            return 0.0
        idx = int(math.ceil(q * len(sorted_data))) - 1
        return sorted_data[max(0, min(idx, len(sorted_data) - 1))]

    def query_sql(self, sql_query: str) -> List[Dict[str, Any]]:
        """Runs a SQL query over traces using DuckDB if available, or in-memory SQLite fallback."""
        if self._duckdb_available:
            import duckdb  # type: ignore
            data = [t.to_dict() for t in self.traces]
            con = duckdb.connect(database=":memory:")
            # Register json table
            con.execute("CREATE TABLE traces AS SELECT * FROM read_json_auto(?)", [json.dumps(data)])
            res = con.execute(sql_query).fetchall()
            cols = [desc[0] for desc in con.description]
            return [dict(zip(cols, row)) for row in res]
        else:
            import sqlite3
            con = sqlite3.connect(":memory:")
            cur = con.cursor()
            cur.execute("""
                CREATE TABLE traces (
                    trace_id TEXT,
                    timestamp TEXT,
                    model_name TEXT,
                    model_version TEXT,
                    prompt TEXT,
                    response TEXT,
                    latency_ms REAL,
                    total_tokens INTEGER,
                    cost_usd REAL,
                    has_error INTEGER
                )
            """)
            rows = [
                (
                    t.trace_id,
                    t.timestamp,
                    t.model_name,
                    t.model_version,
                    t.prompt,
                    t.response,
                    t.latency_ms,
                    t.token_usage.total_tokens,
                    t.token_usage.estimated_cost_usd,
                    1 if t.error else 0
                )
                for t in self.traces
            ]
            cur.executemany("INSERT INTO traces VALUES (?,?,?,?,?,?,?,?,?,?)", rows)
            con.commit()
            try:
                cur.execute(sql_query)
                cols = [desc[0] for desc in cur.description]
                return [dict(zip(cols, r)) for r in cur.fetchall()]
            finally:
                con.close()
