from typing import Dict, List


# -----------------------------
# Validation logic
# -----------------------------
def validate_corep_output(corep_output: Dict | None) -> Dict:
    if corep_output is None:
        return {
            "template": "COREP_C01",
            "rows": [],
            "validation_warnings": ["No COREP output generated."],
            "assumptions": []
        }

    """
    Applies basic validation rules to COREP C 01.00 output.
    Adds validation warnings where appropriate.
    """

    warnings: List[str] = []

    rows = corep_output.get("rows", [])

    if not rows:
        warnings.append("No COREP rows generated.")
        corep_output["validation_warnings"] = warnings
        return corep_output

    for row in rows:
        row_code = row.get("row_code")
        amount = row.get("amount")
        rules = row.get("rule_references", [])

        # Check amount presence
        if amount is None:
            warnings.append(
                f"Row {row_code}: Amount not provided."
            )

        # Check negative values
        if isinstance(amount, (int, float)) and amount < 0:
            warnings.append(
                f"Row {row_code}: Amount is negative."
            )

        # Check audit trail
        if not rules:
            warnings.append(
                f"Row {row_code}: No regulatory rule references provided."
            )

    corep_output["validation_warnings"] = warnings
    return corep_output


# -----------------------------
# Manual test
# -----------------------------
if __name__ == "__main__":
    sample = {
        "template": "COREP_C01",
        "rows": [
            {
                "row_code": "010",
                "label": "Common Equity Tier 1 capital",
                "amount": None,
                "rule_references": []
            }
        ],
        "validation_warnings": [],
        "assumptions": []
    }

    validated = validate_corep_output(sample)

    for w in validated["validation_warnings"]:
        print("Warning:", w)
