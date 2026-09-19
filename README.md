# EvalLake (OpenAssurance-AI)

**The Open-Source GenAI Evaluation, DuckDB-powered ETL, and Cryptographic GRC Governance Lakehouse.**

[![CI](https://github.com/AAH20/fde-bounty-snr/actions/workflows/ci.yml/badge.svg)](https://github.com/AAH20/fde-bounty-snr/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](pyproject.toml)
[![License](https://img.shields.io/badge/License-Apache_2.0-green)](LICENSE)
[![Regulatory](https://img.shields.io/badge/Conformity-EU_AI_Act_|_NIST_AI_RMF_|_ISO_42001-red)](docs/compliance-matrix.md)
[![Protocol](https://img.shields.io/badge/Protocol-OAX_v1_Ed25519-purple)](https://open-assurance.a2zsoc.com)
[![Platform](https://img.shields.io/badge/Enterprise-A2Z_SOC-0F172A)](https://a2zsoc.com)

Compile messy agent trajectories, tool invocations, and LLM traces into **deterministic quality metrics, distribution drift analysis, and cryptographically signed regulatory audit dossiers** (EU AI Act, NIST AI RMF, ISO 42001) in milliseconds.

---

## The Urgent Problem: The Evals-to-Compliance Chasm

* **AI & Data Engineers** test models using fragmented scripts that fail to catch subtle prompt drift, agent tool-call loops, and credential leaks before deploying to production.
* **Legal & Compliance Teams** face mandatory deadlines under the **EU AI Act (Regulation 2024/1689)** and **ISO/IEC 42001**, but lack verifiable evidence from engineering logs to prove conformity.
* **The Result:** Engineering runs evaluations in silos, while legal manually creates subjective spreadsheets that fail third-party regulatory audits.

```text
The Architecture Question:
"Can engineering test suites automatically compile into tamper-evident, cryptographically signed legal compliance dossiers in CI/CD?"
```

**EvalLake answers YES.**

---

## Core Capabilities

1. **High-Throughput ETL & Analytical Lakehouse:**
   * Stream ingestion of OpenTelemetry GenAI traces, JSONL, and Langfuse records.
   * In-process columnar processing using **DuckDB** and **PyArrow** (with zero-dependency standard library fallback).
   * Instant calculation of P50/P95/P99 latencies, token inflation, and cost-per-trace metrics.

2. **Multi-Faceted Evaluation Suite:**
   * **Deterministic Invariants:** JSON schema validation, tool invocation syntax fidelity, and infinite agent loop detection.
   * **Safety & Privacy:** Automated scanning for unmasked PII (SSN, credit cards, emails) and API credential leaks.
   * **Adversarial Resilience:** Real-time auditing of prompt injection and jailbreak neutralization.
   * **Cross-Revision Drift:** Automated detection of latency drift, refusal shifts, and token inflation between baseline and candidate models.

3. **Automated Regulatory Crosswalk:**
   * Maps technical evaluation outcomes directly into formal clauses of:
     * **EU Artificial Intelligence Act** (Articles 9, 10, 12, 15).
     * **NIST AI Risk Management Framework 1.0** (GOVERN, MAP, MEASURE, MANAGE).
     * **ISO/IEC 42001:2023** (Controls A.6, A.8, A.9).

4. **Cryptographic Provenance (OAX Protocol):**
   * Wraps test results in an **OpenAssurance Exchange (OAX v1)** envelope.
   * Canonical RFC 8785 JSON serialization, SHA-256 payload digest, and **Ed25519 digital signature**.
   * Any tampering with evaluation scores invalidates the cryptographic receipt.

---

## Quick Start

### 1. Installation

```bash
# Core package (zero external dependencies required)
pip install eval-lake

# With optional DuckDB & PyArrow acceleration
pip install "eval-lake[all]"
```

### 2. Run Continuous Evaluation & Generate Audit Dossier

```bash
eval-lake eval examples/traces/agent_production_traces.jsonl \
  --config examples/eval_rules.yaml \
  --output-dir ./generated/audit-artifacts
```

Output:
```text
[+] Ingesting and evaluating traces from: examples/traces/agent_production_traces.jsonl
[+] Total traces evaluated : 5
[+] Evaluations pass rate  : 100.0% (7/7)
[+] Executive GRC Status   : CONFORMANT (Grade: A+)
[+] P95 Latency            : 890.2 ms
[+] Total Tokens           : 4,568
[+] Artifacts written to   : ./generated/audit-artifacts
```

### 3. Verify Cryptographic Integrity

```bash
eval-lake verify ./generated/audit-artifacts/oax_signed_envelope.json \
  --key ./generated/audit-artifacts/public_key.pub
```

Output:
```text
[✔] VERIFIED: OAX envelope verified: signature valid, digest matched, zero tampering detected
    Envelope ID : oax_env_batch_e46319b913c1
    Digest      : sha256:a75605221be4aa682fde4ebaa0fc3de973518058dc26d0e9b57c488fec85b14a
```

### 4. Detect Cross-Revision Model & Prompt Drift

```bash
eval-lake drift examples/traces/agent_production_traces.jsonl \
  examples/traces/agent_drift_traces.jsonl \
  --threshold 25.0
```

---

## CLI Reference

| Command | Description | Example |
| :--- | :--- | :--- |
| `eval` | Ingests traces, runs evaluations, maps GRC, and writes receipts | `eval-lake eval traces.jsonl --output-dir ./out` |
| `drift` | Quantifies latency, token, and error drift across model releases | `eval-lake drift baseline.jsonl candidate.jsonl` |
| `dossier` | Generates executive Markdown & HTML compliance dossiers | `eval-lake dossier receipt.json --framework eu_ai_act` |
| `verify` | Independently verifies cryptographic Ed25519 OAX envelopes | `eval-lake verify envelope.json --key pub.key` |
| `sync` | Dispatches signed evidence directly into [A2Z SOC](https://a2zsoc.com) | `eval-lake sync envelope.json --api-key $KEY` |

---

## Regulatory Framework Control Matrix

| Framework | Control Clause | Requirement Description | Technical Evaluator Mapped |
| :--- | :--- | :--- | :--- |
| **EU AI Act** | **Article 9** | Risk Management System | `SAF-INJ-002`, `DET-ERR-003`, `DFT-EVO-001` |
| **EU AI Act** | **Article 10** | Data & Data Governance (Privacy/PII) | `SAF-PII-001` |
| **EU AI Act** | **Article 12** | Automatic Record-Keeping & Logging | `DET-TOOL-001`, `OPS-LAT-001` |
| **EU AI Act** | **Article 15** | Accuracy, Robustness & Cybersecurity | `DET-LOOP-002`, `SAF-INJ-002`, `DET-ERR-003` |
| **NIST AI RMF** | **GOVERN 1.2** | Accountability & Legal Safeguards | `SAF-PII-001`, `OPS-CST-002` |
| **NIST AI RMF** | **MEASURE 2.3** | AI System Accuracy & Reliability | `DET-TOOL-001`, `DET-LOOP-002`, `DET-ERR-003` |
| **NIST AI RMF** | **MEASURE 2.6** | Security & Privacy Evaluation | `SAF-PII-001`, `SAF-INJ-002` |
| **NIST AI RMF** | **MANAGE 1.3** | Continuous Monitoring & Drift Mitigation | `DFT-EVO-001`, `OPS-LAT-001` |
| **ISO 42001** | **Control A.6** | AI Risk Assessment & Treatment | `SAF-INJ-002`, `DET-ERR-003` |
| **ISO 42001** | **Control A.8** | Data for AI Systems | `SAF-PII-001` |
| **ISO 42001** | **Control A.9** | AI System Life Cycle Verification | `DET-TOOL-001`, `DET-LOOP-002`, `DFT-EVO-001` |

---

## Commercial Architecture & Pricing

EvalLake operates on an **Open Core + Enterprise GRC** business model:

```
┌─────────────────────────────────────────────────────────────┐
│                 COMMUNITY OPEN SOURCE (FOSS)                │
│  - 100% Free Apache-2.0 License                             │
│  - Full CLI, in-memory DuckDB analytics, 7 core evaluators  │
│  - Local Markdown and HTML dossier generation               │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 ENTERPRISE GRC & CLOUD TIERS                │
│              (Powered by A2Z SOC: https://a2zsoc.com)       │
│                                                             │
│  • Team Cloud ($499/mo): Continuous CI/CD drift tracking,   │
│    automated Slack/Teams alerting, 90-day trace retention.  │
│                                                             │
│  • Enterprise GRC ($35,000 – $75,000/yr):                   │
│    - Self-hosted VPC / Air-gapped deployment                │
│    - 1-Click EU AI Act Conformity Assessment Dossiers       │
│    - Ed25519 OAX Evidence Vault & Auditor Portal            │
│    - Centralized SOC 2, ISO 27001 & 42001 Continuous Trust  │
│    - Integration with 867 pre-mapped enterprise controls    │
└─────────────────────────────────────────────────────────────┘
```

For enterprise licensing and compliance platform access, visit **[a2zsoc.com](https://a2zsoc.com)**.

---

## License

Copyright 2025-2026 Ahmed Hassan. Licensed under the [Apache License, Version 2.0](LICENSE).
