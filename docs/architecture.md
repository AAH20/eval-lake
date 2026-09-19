# System Architecture: EvalLake (OpenAssurance-AI)

EvalLake connects high-speed analytical data pipelines with cryptographic audit verification and regulatory compliance frameworks.

```mermaid
flowchart TD
  subgraph Ingestion ["1. INGESTION & ETL"]
    Traces["Agent / LLM Traces<br/>(JSONL / OTel / Langfuse)"] --> Parser["TraceParser<br/>(Format Normalization)"]
    Parser --> Engine["AnalyticsEngine<br/>(DuckDB / Columnar Vector Storage)"]
  end

  subgraph Evals ["2. EVALUATION & DRIFT"]
    Engine --> Det["Deterministic Evaluators<br/>(Tool Syntax, Loop Detection, Error Rate)"]
    Engine --> Safe["Safety & Privacy Evaluators<br/>(PII Auditing, Injection Defense)"]
    Engine --> Sem["Operational Evaluators<br/>(Latency SLA, Cost Budget)"]
    Engine --> Drift["Drift Evaluator<br/>(Cross-Revision Kolmogorov/Variance Shift)"]
  end

  subgraph GRC ["3. REGULATORY COMPLIANCE MAPPING"]
    Det & Safe & Sem & Drift --> Mapper["ComplianceMapper"]
    Mapper --> Cat["Control Catalog<br/>• EU AI Act (Arts 9, 10, 12, 15)<br/>• NIST AI RMF 1.0<br/>• ISO/IEC 42001:2023"]
    Mapper --> Dossier["ComplianceDossierGenerator<br/>(Markdown / HTML / JSON Audit Dossier)"]
  end

  subgraph Crypto ["4. CRYPTOGRAPHIC PROVENANCE (OAX v1)"]
    Dossier --> OAX["OAX Canonical Envelope<br/>(RFC 8785 JSON + SHA-256 Digest)"]
    OAX --> Signer["Ed25519 Cryptographic Signer"]
    Signer --> Verifier["Independent Verifier CLI"]
  end

  subgraph Enterprise ["5. COMMERCIAL CONTROL PLANE"]
    Signer -.-> Bridge["A2Z SOC Bridge Client"]
    Bridge -.-> SOC["A2Z SOC Enterprise Platform<br/>(https://a2zsoc.com)"]
  end
```

---

## Technical Invariants
1. **Zero External Dependencies Required:** Base evaluations, columnar queries, and RFC 8032 Ed25519 signing execute on standard Python 3.10+ runtimes.
2. **Columnar Acceleration:** When `duckdb` or `pyarrow` is installed, analytical queries run with vector processing speed.
3. **Cryptographic Tamper-Evidence:** Any byte altered in an evaluation record invalidates the SHA-256 digest and Ed25519 signature.
4. **Direct Regulatory Crosswalk:** Technical engineering metrics directly map into legal requirements for conformity assessments.
