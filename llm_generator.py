import json
from typing import List, Dict

import streamlit as st
from groq import Groq


# -----------------------------
# Configuration
# -----------------------------
MODEL_NAME = "llama-3.3-70b-versatile"


# -----------------------------
# Build system prompt
# -----------------------------
def build_system_prompt() -> str:
    return """
You are a regulatory reporting assistant for UK banks.

Your task:
- Use ONLY the provided regulatory text.
- Populate COREP C 01.00 (Own Funds).
- Focus on Common Equity Tier 1 capital (row 010).
- If an amount is not provided, set it to null.
- For every populated row, cite the regulatory sources used.

Output rules:
- Output ONLY valid JSON.
- Do NOT include explanations outside JSON.
- Follow the schema exactly.

This is a prototype; do not infer missing numerical values.
"""


# -----------------------------
# Build user prompt
# -----------------------------
def build_user_prompt(
    question: str,
    scenario: str,
    retrieved_chunks: List[Dict]
) -> str:
    context = "\n\n".join(
        [
            f"[Source: {c['source']} | Page: {c['page']}]\n{c['text']}"
            for c in retrieved_chunks
        ]
    )

    return f"""
USER QUESTION:
{question}

REPORTING SCENARIO:
{scenario}

RELEVANT REGULATORY TEXT:
{context}

Generate the COREP C 01.00 structured output now.
"""


# -----------------------------
# Call LLM and normalize output
# -----------------------------
def generate_corep_output(
    question: str,
    scenario: str,
    retrieved_chunks: List[Dict]
) -> Dict:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {
                "role": "user",
                "content": build_user_prompt(
                    question, scenario, retrieved_chunks
                )
            },
        ],
        temperature=0.1,
    )

    raw_output = response.choices[0].message.content.strip()

    # -----------------------------
    # Sanitize markdown code fences
    # -----------------------------
    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`")
        if raw_output.lower().startswith("json"):
            raw_output = raw_output[4:].strip()

    # -----------------------------
    # Parse JSON safely
    # -----------------------------
    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        return {
            "template": "COREP_C01",
            "rows": [],
            "validation_warnings": [
                "LLM output could not be parsed as JSON."
            ],
            "assumptions": [],
            "raw_llm_output": raw_output
        }

    # -----------------------------
    # Helper: normalize rule references
    # -----------------------------
    def normalize_sources(src):
        if src is None:
            return []
        if isinstance(src, list):
            return src
        return [str(src)]

    # -----------------------------
    # Case 1: Perfect schema already returned
    # -----------------------------
    if "rows" in parsed and isinstance(parsed["rows"], list) and parsed["rows"]:
        return parsed

    # -----------------------------
    # Case 2: Flat single-row structure
    # -----------------------------
    if "row" in parsed or "row_code" in parsed or "010" in parsed:
        # Safely extract row code
        if "010" in parsed:
            row_code = "010"
            cell = parsed.get("010", {})
        else:
            row_code = str(parsed.get("row") or parsed.get("row_code"))
            cell = parsed

        value = cell.get("value")
        source = normalize_sources(cell.get("source"))

        return {
            "template": "COREP_C01",
            "rows": [
                {
                    "row_code": str(row_code),
                    "label": "Common Equity Tier 1 capital",
                    "amount": value,
                    "rule_references": source,
                }
            ],
            "validation_warnings": [],
            "assumptions": [],
        }

    # -----------------------------
    # Case 3: Nested raw_llm_output
    # -----------------------------
    raw = parsed.get("raw_llm_output", {})
    if isinstance(raw, dict) and "row" in raw:
        return {
            "template": "COREP_C01",
            "rows": [
                {
                    "row_code": str(raw.get("row")),
                    "label": "Common Equity Tier 1 capital",
                    "amount": raw.get("value"),
                    "rule_references": normalize_sources(raw.get("source")),
                }
            ],
            "validation_warnings": [],
            "assumptions": [],
        }

    # -----------------------------
    # Fallback: structured empty but safe
    # -----------------------------
    return {
        "template": "COREP_C01",
        "rows": [],
        "validation_warnings": [
            "LLM output did not match expected COREP schema."
        ],
        "assumptions": [],
        "raw_llm_output": parsed
    }


# -----------------------------
# Manual test
# -----------------------------
if __name__ == "__main__":
    from retriever import retrieve_relevant_chunks

    q = "How should Common Equity Tier 1 capital be reported under COREP C 01.00?"
    s = "UK bank with ordinary shares and retained earnings, no deductions."

    retrieved = retrieve_relevant_chunks(q, s)
    result = generate_corep_output(q, s, retrieved)

    print(json.dumps(result, indent=2))
