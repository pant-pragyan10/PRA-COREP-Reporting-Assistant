# corep_reporting_assistant

A prototype LLM-assisted reporting assistant for the Prudential Regulation Authority (PRA) COREP C 01.00 (Own Funds) template.

## Overview

This repository demonstrates a small, focused workflow for mapping a natural-language regulatory question and a reporting scenario to structured COREP output using retrieval-augmented LLMs.

**Key goals:**

- Provide a reproducible ingestion → retrieval → LLM → validation → render pipeline.
- Produce structured JSON outputs that align to a simple COREP schema.
- Preserve auditability by attaching regulatory source references to populated fields.

> **Note:** This is a development prototype. It does not compute or validate numerical capital amounts for production use.

## Project Structure

- `data/` — example input PDFs (placeholders).
- `ingest.py` — read PDFs, split text, build FAISS vector index.
- `retriever.py` — query the FAISS index for relevant regulatory chunks.
- `llm_generator.py` — build prompts and call the LLM (Groq) to produce structured COREP output.
- `validator.py` — simple validation rules that flag missing or inconsistent data.
- `renderer.py` — human-readable extract renderer for COREP output.
- `app.py` — Streamlit demo UI for local testing.
- `.streamlit/secrets.toml` — local secrets file (should NOT be committed).

## Quickstart

1. Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Add your Groq API key (Streamlit secrets):

Create `.streamlit/secrets.toml` and add:

```toml
GROQ_API_KEY = "your_groq_api_key"
```

3. (Optional) Build the vector index locally:

```bash
python ingest.py
```

4. Run the Streamlit demo:

```bash
streamlit run app.py
```

## Security & Best Practices

- **Do not commit secrets.** The repository includes `.gitignore` entries to exclude `.streamlit/secrets.toml` and the `vector_index/` folder.
- **Avoid `allow_dangerous_deserialization=True`** in production — do not load untrusted serialized files.
- **Pin dependencies** for reproducibility before deploying or sharing.

### Removing accidentally committed secrets

If you previously committed secrets (API keys, tokens) to the repository, remove them from the working tree and then rewrite history to purge them:

1. Remove the secret file from the repository and replace it with a placeholder (already done in this repo):

```bash
git rm --cached .streamlit/secrets.toml
rm .streamlit/secrets.toml
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
git add .streamlit/secrets.toml .gitignore
git commit -m "Remove committed secrets; add placeholder and ignore rules"
```

2. Rewrite git history to purge the secret from all commits (use one of these tools):

- Using `git filter-repo` (recommended):

```bash
# Install: pip install git-filter-repo
git filter-repo --invert-paths --paths .streamlit/secrets.toml
```

- Or using the BFG Repo-Cleaner:

```bash
# Install BFG, then:
bfg --delete-files .streamlit/secrets.toml
git reflog expire --expire=now --all && git gc --prune=now --aggressive
```

3. Push the cleaned repository (force push) to remote:

```bash
git push --force --all
git push --force --tags
```

4. **Rotate the compromised key** immediately at the provider (Groq) — assume it is compromised.

If you'd like, I can run the simple local edits here (remove file contents) — I will not run git-history rewriting tools without your confirmation.

## Recommended Next Steps

- Replace placeholder logic with production-grade ingestion and parsing.
- Add unit tests for the normalization and validation layers.
- Replace prints with structured logging and move demo/test scripts to `scripts/`.

## Contributing

1. Fork the repository and create a feature branch.
2. Add tests and documentation for any substantive change.
3. Open a pull request describing your changes.

---

This prototype is intended to be a starting point for developers building LLM-assisted regulatory reporting tools. Use responsibly and ensure regulatory and data governance standards are met before production use.