"""
GRC Compliance Mapper.
Crosswalks technical evaluation results into formal regulatory compliance scorecards.
"""

from typing import List, Dict, Any
from evallake.etl.schema import EvaluationRecord
from evallake.grc.catalog import GRC_FRAMEWORKS


class ComplianceMapper:
    """Maps execution evaluation records to GRC controls and calculates conformity."""

    @staticmethod
    def map_evaluations_to_frameworks(evaluations: List[EvaluationRecord]) -> Dict[str, Any]:
        eval_by_id = {e.test_id: e for e in evaluations}
        results = {}

        for fw_key, fw_data in GRC_FRAMEWORKS.items():
            fw_name = fw_data["name"]
            controls_res = {}
            total_controls = len(fw_data["controls"])
            passed_controls = 0

            for ctrl_id, ctrl_info in fw_data["controls"].items():
                mapped_tests = ctrl_info["mapped_tests"]
                test_scores = []
                all_passed = True

                for t_id in mapped_tests:
                    if t_id in eval_by_id:
                        rec = eval_by_id[t_id]
                        test_scores.append(rec.score)
                        if not rec.passed:
                            all_passed = False
                    else:
                        # Test was not run; treat as unverified
                        test_scores.append(0.0)
                        all_passed = False

                avg_score = sum(test_scores) / len(test_scores) if test_scores else 0.0
                if all_passed:
                    passed_controls += 1

                controls_res[ctrl_id] = {
                    "title": ctrl_info["title"],
                    "description": ctrl_info["description"],
                    "status": "PASS" if all_passed else "FAIL",
                    "score": round(avg_score, 4),
                    "mapped_tests": mapped_tests
                }

            fw_score = round(passed_controls / total_controls, 4) if total_controls > 0 else 0.0
            fw_status = "CONFORMANT" if passed_controls == total_controls else ("PROVISIONAL" if passed_controls > 0 else "NON_CONFORMANT")

            results[fw_key] = {
                "framework_name": fw_name,
                "status": fw_status,
                "compliance_score": fw_score,
                "passed_controls": passed_controls,
                "total_controls": total_controls,
                "controls": controls_res
            }

        # Overall aggregate
        total_all_controls = sum(r["total_controls"] for r in results.values())
        passed_all_controls = sum(r["passed_controls"] for r in results.values())
        aggregate_ratio = passed_all_controls / total_all_controls if total_all_controls > 0 else 0.0

        if aggregate_ratio >= 1.0:
            grade = "A+"
            status = "CONFORMANT"
        elif aggregate_ratio >= 0.8:
            grade = "A"
            status = "PROVISIONAL"
        elif aggregate_ratio >= 0.6:
            grade = "B"
            status = "NEEDS_REMEDIATION"
        else:
            grade = "F"
            status = "NON_CONFORMANT"

        return {
            "overall_status": status,
            "overall_grade": grade,
            "aggregate_compliance_score": round(aggregate_ratio, 4),
            "passed_controls_count": passed_all_controls,
            "total_controls_count": total_all_controls,
            "frameworks": results
        }
