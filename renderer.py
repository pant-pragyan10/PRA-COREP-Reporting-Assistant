from typing import Dict


def render_corep_table(corep_output: Dict) -> str:
    """
    Renders a human-readable COREP C 01.00 extract from structured output.
    """

    lines = []
    lines.append("COREP C 01.00 – Own Funds (Extract)")
    lines.append("-" * 45)

    for row in corep_output.get("rows", []):
        lines.append(f"Row {row['row_code']} – {row['label']}")
        lines.append(f"Amount: {row['amount']}")
        lines.append(
            f"Regulatory references: {', '.join(row.get('rule_references', []))}"
        )
        lines.append("")

    if corep_output.get("validation_warnings"):
        lines.append("Validation Warnings:")
        for w in corep_output["validation_warnings"]:
            lines.append(f"- {w}")

    if corep_output.get("assumptions"):
        lines.append("\nAssumptions:")
        for a in corep_output["assumptions"]:
            lines.append(f"- {a}")

    return "\n".join(lines)


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
                "rule_references": ["PRA Own Funds p.1", "COREP Instructions p.3"]
            }
        ],
        "validation_warnings": [
            "Row 010: Amount not provided."
        ],
        "assumptions": [
            "No numerical CET1 amount supplied in scenario."
        ]
    }

    print(render_corep_table(sample))
