"""
Authoritative Catalog of GRC Controls for AI Governance.
Covers EU AI Act, NIST AI RMF 1.0, and ISO/IEC 42001:2023.
"""

from typing import Dict, Any

GRC_FRAMEWORKS = {
    "eu_ai_act": {
        "name": "EU Artificial Intelligence Act (Regulation 2024/1689)",
        "controls": {
            "EU-AI-ACT-ART-09": {
                "title": "Article 9: Risk Management System",
                "description": "Continuous identification, evaluation, and mitigation of foreseeable risks during operation.",
                "mapped_tests": ["SAF-INJ-002", "DET-ERR-003", "DFT-EVO-001"]
            },
            "EU-AI-ACT-ART-10": {
                "title": "Article 10: Data and Data Governance",
                "description": "Validation and mitigation of privacy violations, bias, and unauthorized PII leakage in AI inputs/outputs.",
                "mapped_tests": ["SAF-PII-001"]
            },
            "EU-AI-ACT-ART-12": {
                "title": "Article 12: Record-Keeping & Automated Logging",
                "description": "High-risk AI systems shall technically allow for the automatic recording of events over their lifetime.",
                "mapped_tests": ["DET-TOOL-001", "OPS-LAT-001"]
            },
            "EU-AI-ACT-ART-15": {
                "title": "Article 15: Accuracy, Robustness and Cybersecurity",
                "description": "Resilience against exploitation, adversarial input manipulation, and cyclic execution failures.",
                "mapped_tests": ["DET-LOOP-002", "SAF-INJ-002", "DET-ERR-003"]
            }
        }
    },
    "nist_ai_rmf": {
        "name": "NIST AI Risk Management Framework 1.0",
        "controls": {
            "NIST-GOVERN-1.2": {
                "title": "GOVERN 1.2: Accountability & Legal Compliance",
                "description": "Policies and technical safeguards for responsible, verified AI usage are implemented.",
                "mapped_tests": ["SAF-PII-001", "OPS-CST-002"]
            },
            "NIST-MEASURE-2.3": {
                "title": "MEASURE 2.3: AI System Accuracy & Reliability",
                "description": "System performance, execution fidelity, and error resilience are quantified and verified.",
                "mapped_tests": ["DET-TOOL-001", "DET-LOOP-002", "DET-ERR-003"]
            },
            "NIST-MEASURE-2.6": {
                "title": "MEASURE 2.6: Security & Privacy Evaluation",
                "description": "Evaluation of vulnerabilities including prompt injection, data extraction, and secret leakage.",
                "mapped_tests": ["SAF-PII-001", "SAF-INJ-002"]
            },
            "NIST-MANAGE-1.3": {
                "title": "MANAGE 1.3: Continuous Monitoring & Drift Mitigation",
                "description": "System updates, prompt changes, and fine-tunes are continuously evaluated for regression.",
                "mapped_tests": ["DFT-EVO-001", "OPS-LAT-001"]
            }
        }
    },
    "iso_42001": {
        "name": "ISO/IEC 42001:2023 AI Management System",
        "controls": {
            "ISO-42001-A.6": {
                "title": "Control A.6: AI Risk Assessment",
                "description": "Identification and treatment of functional and operational AI risks.",
                "mapped_tests": ["SAF-INJ-002", "DET-ERR-003"]
            },
            "ISO-42001-A.8": {
                "title": "Control A.8: Data for AI Systems",
                "description": "Data governance, provenance, sanitization, and PII protection.",
                "mapped_tests": ["SAF-PII-001"]
            },
            "ISO-42001-A.9": {
                "title": "Control A.9: AI System Life Cycle",
                "description": "Continuous validation, verification, and regression control across model lifecycle.",
                "mapped_tests": ["DET-TOOL-001", "DET-LOOP-002", "DFT-EVO-001", "OPS-LAT-001"]
            }
        }
    }
}
