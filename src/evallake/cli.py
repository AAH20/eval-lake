"""
Command-Line Interface for EvalLake (OpenAssurance-AI).
"""

import sys
import os
import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from evallake.etl.parser import TraceParser
from evallake.etl.engine import AnalyticsEngine
from evallake.etl.schema import BatchEvaluationReceipt, EvaluationRecord
from evallake.evals.deterministic import DeterministicEvaluator
from evallake.evals.safety import SafetyEvaluator
from evallake.evals.semantics import SemanticEvaluator
from evallake.evals.drift import DriftEvaluator
from evallake.grc.mapper import ComplianceMapper
from evallake.grc.dossier import ComplianceDossierGenerator
from evallake.crypto.ed25519 import CryptoSigner
from evallake.crypto.oax import sign_evaluation_receipt, verify_evaluation_receipt, canonicalize
from evallake.bridge.a2zsoc import A2ZSOCBridge


def run_eval_pipeline(traces_path: str, output_dir: str = "", sign_receipt: bool = True) -> BatchEvaluationReceipt:
    traces = TraceParser.parse_jsonl(traces_path)
    engine = AnalyticsEngine(traces)
    summary = engine.compute_summary()

    # Run evaluations
    evals: list[EvaluationRecord] = [
        DeterministicEvaluator.evaluate_tool_syntax(traces),
        DeterministicEvaluator.evaluate_loop_prevention(traces),
        DeterministicEvaluator.evaluate_error_rate(traces),
        SafetyEvaluator.evaluate_pii_leakage(traces),
        SafetyEvaluator.evaluate_prompt_injection(traces),
        SemanticEvaluator.evaluate_latency_sla(traces, max_p95_ms=3000.0),
        SemanticEvaluator.evaluate_cost_budget(traces, max_cost_per_trace_usd=0.05)
    ]

    total_evals = len(evals)
    passed_evals = sum(1 for e in evals if e.passed)
    pass_rate = round(passed_evals / total_evals, 4) if total_evals > 0 else 1.0

    # Crosswalk GRC
    scorecards = ComplianceMapper.map_evaluations_to_frameworks(evals)

    batch_id = f"batch_{uuid.uuid4().hex[:12]}"
    receipt = BatchEvaluationReceipt(
        batch_id=batch_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        dataset_source=os.path.basename(traces_path),
        total_traces=summary["total_traces"],
        total_evaluations=total_evals,
        passed_evaluations=passed_evals,
        failed_evaluations=total_evals - passed_evals,
        pass_rate=pass_rate,
        p50_latency_ms=summary["p50_latency_ms"],
        p95_latency_ms=summary["p95_latency_ms"],
        p99_latency_ms=summary["p99_latency_ms"],
        total_tokens=summary["total_tokens"],
        total_cost_usd=summary["total_cost_usd"],
        evaluations=evals,
        compliance_scorecards=scorecards,
        metadata={"engine": "eval-lake-analytics", "author": "A2Z SOC"}
    )

    if output_dir:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        # 1. Write evaluation receipt
        receipt_file = out_path / "evaluation_receipt.json"
        with open(receipt_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(receipt.to_dict(), indent=2))

        # 2. Write Markdown compliance dossier
        md_dossier = ComplianceDossierGenerator.generate_markdown(receipt)
        dossier_file = out_path / "compliance_dossier.md"
        with open(dossier_file, "w", encoding="utf-8") as f:
            f.write(md_dossier)

        # 3. Write HTML compliance dossier
        html_dossier = ComplianceDossierGenerator.generate_html(receipt)
        html_file = out_path / "compliance_dossier.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_dossier)

        # 4. Sign if requested
        if sign_receipt:
            priv_b64, pub_b64 = CryptoSigner.generate_keypair()
            envelope = sign_evaluation_receipt(receipt, priv_b64, pub_b64)
            env_file = out_path / "oax_signed_envelope.json"
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(envelope.to_canonical_json())

            # Save keys for verification demo
            with open(out_path / "public_key.pub", "w", encoding="utf-8") as f:
                f.write(pub_b64)
            with open(out_path / "private_key.key", "w", encoding="utf-8") as f:
                f.write(priv_b64)

    return receipt


def main():
    parser = argparse.ArgumentParser(
        prog="eval-lake",
        description="EvalLake: GenAI Evaluation, DuckDB ETL & Cryptographic GRC Governance Lakehouse"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Command: eval
    cmd_eval = subparsers.add_parser("eval", help="Ingest traces and run continuous evaluation suite")
    cmd_eval.add_argument("traces", help="Path to traces JSONL file")
    cmd_eval.add_argument("--config", help="Optional path to evaluation rules YAML", default="")
    cmd_eval.add_argument("--output-dir", help="Output directory for generated dossiers and receipts", default="")
    cmd_eval.add_argument("--sign", action="store_true", default=True, help="Sign evidence receipt with Ed25519")

    # Command: drift
    cmd_drift = subparsers.add_parser("drift", help="Evaluate distribution drift between baseline and candidate traces")
    cmd_drift.add_argument("baseline", help="Path to baseline traces JSONL")
    cmd_drift.add_argument("candidate", help="Path to candidate traces JSONL")
    cmd_drift.add_argument("--threshold", type=float, default=25.0, help="Max allowed drift percentage")

    # Command: dossier
    cmd_dossier = subparsers.add_parser("dossier", help="Generate compliance audit dossier from receipt")
    cmd_dossier.add_argument("receipt", help="Path to evaluation_receipt.json")
    cmd_dossier.add_argument("--framework", choices=["all", "eu_ai_act", "nist_ai_rmf", "iso_42001"], default="all")
    cmd_dossier.add_argument("--output-dir", default="")

    # Command: verify
    cmd_verify = subparsers.add_parser("verify", help="Cryptographically verify an OAX evidence envelope")
    cmd_verify.add_argument("envelope", help="Path to oax_signed_envelope.json")
    cmd_verify.add_argument("--key", help="Path to public key file or base64 key string", required=True)

    # Command: sync
    cmd_sync = subparsers.add_parser("sync", help="Synchronize signed evidence envelope with A2Z SOC")
    cmd_sync.add_argument("envelope", help="Path to oax_signed_envelope.json")
    cmd_sync.add_argument("--endpoint", default="", help="A2Z SOC API endpoint")
    cmd_sync.add_argument("--api-key", default="", help="A2Z SOC API key")

    args = parser.parse_args()

    if args.command == "eval":
        print(f"\n[+] Ingesting and evaluating traces from: {args.traces}")
        receipt = run_eval_pipeline(args.traces, output_dir=args.output_dir, sign_receipt=args.sign)
        sc = receipt.compliance_scorecards
        print(f"[+] Total traces evaluated : {receipt.total_traces}")
        print(f"[+] Evaluations pass rate  : {receipt.pass_rate * 100:.1f}% ({receipt.passed_evaluations}/{receipt.total_evaluations})")
        print(f"[+] Executive GRC Status   : {sc.get('overall_status')} (Grade: {sc.get('overall_grade')})")
        print(f"[+] P95 Latency            : {receipt.p95_latency_ms} ms")
        print(f"[+] Total Tokens           : {receipt.total_tokens:,}")
        if args.output_dir:
            print(f"[+] Artifacts written to   : {args.output_dir}")

    elif args.command == "drift":
        b_traces = TraceParser.parse_jsonl(args.baseline)
        c_traces = TraceParser.parse_jsonl(args.candidate)
        drift_rec = DriftEvaluator.calculate_drift(b_traces, c_traces, max_allowed_drift_pct=args.threshold)
        print("\n[+] Cross-Revision Drift Evaluation:")
        print(f"    Metric      : {drift_rec.metric_name}")
        print(f"    Passed      : {drift_rec.passed}")
        print(f"    Score       : {drift_rec.score * 100:.1f}%")
        print(f"    Summary     : {drift_rec.message}")
        print(f"    Details     : {json.dumps(drift_rec.details, indent=6)}")

    elif args.command == "dossier":
        with open(args.receipt, "r", encoding="utf-8") as f:
            data = json.load(f)
        receipt = BatchEvaluationReceipt(
            batch_id=data["batch_id"],
            timestamp=data["timestamp"],
            dataset_source=data["dataset_source"],
            total_traces=data["total_traces"],
            total_evaluations=data["total_evaluations"],
            passed_evaluations=data["passed_evaluations"],
            failed_evaluations=data["failed_evaluations"],
            pass_rate=data["pass_rate"],
            p50_latency_ms=data["p50_latency_ms"],
            p95_latency_ms=data["p95_latency_ms"],
            p99_latency_ms=data["p99_latency_ms"],
            total_tokens=data["total_tokens"],
            total_cost_usd=data["total_cost_usd"],
            evaluations=[EvaluationRecord(**e) for e in data.get("evaluations", [])],
            compliance_scorecards=data.get("compliance_scorecards", {}),
            metadata=data.get("metadata", {})
        )
        md = ComplianceDossierGenerator.generate_markdown(receipt)
        if args.output_dir:
            out_p = Path(args.output_dir)
            out_p.mkdir(parents=True, exist_ok=True)
            with open(out_p / "compliance_dossier.md", "w", encoding="utf-8") as f:
                f.write(md)
            print(f"[+] Compliance dossier saved to {out_p / 'compliance_dossier.md'}")
        else:
            print(md)

    elif args.command == "verify":
        with open(args.envelope, "r", encoding="utf-8") as f:
            env_data = json.load(f)
        
        # Determine public key
        key_str = args.key
        if os.path.exists(key_str):
            with open(key_str, "r", encoding="utf-8") as f:
                key_str = f.read().strip()

        valid, msg = verify_evaluation_receipt(env_data, key_str)
        if valid:
            print(f"\n[✔] VERIFIED: {msg}")
            print(f"    Envelope ID : {env_data.get('envelope_id')}")
            print(f"    Digest      : {env_data.get('payload_digest')}")
            print(f"    Issued At   : {env_data.get('issued_at')}")
            sys.exit(0)
        else:
            print(f"\n[✘] VERIFICATION FAILED: {msg}")
            sys.exit(1)

    elif args.command == "sync":
        with open(args.envelope, "r", encoding="utf-8") as f:
            env_data = json.load(f)
        envelope = OAXEnvelope(**env_data)
        bridge = A2ZSOCBridge(api_key=args.api_key, endpoint=args.endpoint)
        print(f"\n[+] Dispatching signed OAX envelope to A2Z SOC: {bridge.endpoint}")
        ok, res = bridge.sync_envelope(envelope)
        if ok:
            print("[✔] Successfully synchronized with A2Z SOC Trust Vault")
        else:
            print(f"[!] Sync notification: {res}")


if __name__ == "__main__":
    main()
