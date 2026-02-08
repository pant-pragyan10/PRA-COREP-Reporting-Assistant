import streamlit as st

from retriever import retrieve_relevant_chunks
from llm_generator import generate_corep_output
from validator import validate_corep_output
from renderer import render_corep_table


st.set_page_config(page_title="LLM-assisted COREP Reporting", layout="wide")

st.title("📊 LLM-assisted PRA COREP Reporting Assistant")
st.write(
    "Prototype for COREP C 01.00 (Own Funds) using PRA rules and COREP instructions."
)

# -----------------------------
# User inputs
# -----------------------------
question = st.text_input(
    "Regulatory question",
    value="How should Common Equity Tier 1 capital be reported?"
)

scenario = st.text_area(
    "Reporting scenario",
    value="UK bank with ordinary shares and retained earnings, no deductions.",
    height=120
)

run_button = st.button("Generate COREP Extract")

# -----------------------------
# Main pipeline
# -----------------------------
if run_button:
    with st.spinner("Retrieving relevant regulatory guidance..."):
        retrieved_chunks = retrieve_relevant_chunks(question, scenario)

    st.subheader("📚 Retrieved Regulatory Text")
    for chunk in retrieved_chunks:
        with st.expander(f"{chunk['source']} – Page {chunk['page']}"):
            st.write(chunk["text"])

    with st.spinner("Generating structured COREP output..."):
        corep_output = generate_corep_output(
            question, scenario, retrieved_chunks
        )

    validated_output = validate_corep_output(corep_output)

    st.subheader("🧾 COREP C 01.00 Output (Structured JSON)")
    st.json(validated_output)

    st.subheader("📑 COREP C 01.00 Extract (Human-readable)")
    st.text(render_corep_table(validated_output))
