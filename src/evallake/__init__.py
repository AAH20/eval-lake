"""
EvalLake (OpenAssurance-AI)
The Open-Source GenAI Evaluation, DuckDB-powered ETL, and Cryptographic GRC Governance Lakehouse.
"""

__version__ = "1.0.0"
__author__ = "Ahmed Hassan (A2Z SOC)"

from evallake.etl.schema import TraceEvent, ToolInvocation, TokenUsage, EvaluationRecord
from evallake.etl.engine import AnalyticsEngine
from evallake.grc.dossier import ComplianceDossierGenerator
from evallake.crypto.oax import OAXEnvelope, sign_evaluation_receipt, verify_evaluation_receipt

__all__ = [
    "TraceEvent",
    "ToolInvocation",
    "TokenUsage",
    "EvaluationRecord",
    "AnalyticsEngine",
    "ComplianceDossierGenerator",
    "OAXEnvelope",
    "sign_evaluation_receipt",
    "verify_evaluation_receipt",
]
