# Complete Regulatory Compliance & Crosswalk Matrix

This document defines the formal mapping between technical evaluation heuristics in `eval-lake` and international AI governance standards.

---

## 1. European Union Artificial Intelligence Act (Regulation EU 2024/1689)

### Article 9: Risk Management System
* **Regulatory Intent:** Providers of high-risk AI systems must establish, implement, document, and maintain a risk management system. This includes testing to identify the most appropriate risk management measures against known and foreseeable risks.
* **EvalLake Technical Control:**
  * `SAF-INJ-002` (Adversarial Prompt Injection Defense): Probes system resilience against hostile inputs.
  * `DET-ERR-003` (Runtime Error Resilience): Tracks system fault rates and unhandled exceptions.
  * `DFT-EVO-001` (Cross-Revision Stability): Evaluates systemic performance drift before deploying updates.

### Article 10: Data and Data Governance
* **Regulatory Intent:** Training, validation, and testing datasets shall be subject to appropriate data governance and management practices (data collection, mitigation of privacy infringements, PII scrubbing).
* **EvalLake Technical Control:**
  * `SAF-PII-001` (PII and Credential Sanitization): Audits raw inputs and generated responses for emails, Social Security Numbers, credit cards, and leaked API secret tokens.

### Article 12: Record-Keeping & Automated Logging
* **Regulatory Intent:** High-risk AI systems shall technically allow for the automatic recording of events ('logs') over their lifetime. Logging capabilities shall ensure a level of traceability throughout the system's life cycle.
* **EvalLake Technical Control:**
  * `DET-TOOL-001` (Tool-Call Syntax Fidelity): Records every agent action, tool invocation, and argument payload.
  * `OPS-LAT-001` (P95 Latency SLA): Timestamped execution duration tracing for all model interactions.

### Article 15: Accuracy, Robustness and Cybersecurity
* **Regulatory Intent:** High-risk AI systems shall be resilient as regards errors, faults, or inconsistencies that may occur within the system or the environment in which it operates. They shall be resilient against attempts by unauthorized third parties to alter their use or performance.
* **EvalLake Technical Control:**
  * `DET-LOOP-002` (Agent Trajectory Loop Freedom): Detects infinite recursive tool-calling loops that deplete compute.
  * `SAF-INJ-002` (Adversarial Injection Defense): Validates model guardrails against jailbreaks.

---

## 2. NIST AI Risk Management Framework (NIST AI RMF 1.0)

| Function | Category | Subcategory | EvalLake Evaluator |
| :--- | :--- | :--- | :--- |
| **GOVERN** | 1.2 | Legal & Regulatory Compliance Safeguards | `SAF-PII-001`, `OPS-CST-002` |
| **MAP** | 1.5 | Categorization of AI Risks & Impacts | `SAF-INJ-002`, `DET-LOOP-002` |
| **MEASURE** | 2.3 | Accuracy, Reliability, and Robustness | `DET-TOOL-001`, `DET-ERR-003` |
| **MEASURE** | 2.6 | Privacy & Data Extraction Vulnerabilities | `SAF-PII-001` |
| **MANAGE** | 1.3 | Continuous Monitoring & Drift Mitigation | `DFT-EVO-001`, `OPS-LAT-001` |

---

## 3. ISO/IEC 42001:2023 (Artificial Intelligence Management System)

| Control Domain | Control ID | Control Purpose | EvalLake Evaluator |
| :--- | :--- | :--- | :--- |
| **AI Risk Assessment** | `A.6.1` | Identify and assess operational AI risks | `SAF-INJ-002`, `DET-ERR-003` |
| **Data for AI Systems** | `A.8.2` | Data quality, provenance, and privacy | `SAF-PII-001` |
| **AI System Lifecycle** | `A.9.3` | Continuous validation and regression testing | `DET-TOOL-001`, `DFT-EVO-001` |
