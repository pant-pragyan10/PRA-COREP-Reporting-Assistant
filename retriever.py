from typing import List, Dict

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
except Exception:
    try:
        from langchain.embeddings import HuggingFaceEmbeddings  # type: ignore
    except Exception as e:
        raise ImportError(
            "HuggingFaceEmbeddings is not available. Install `langchain-community` "
            "or upgrade `langchain`."
        ) from e
from langchain_community.vectorstores import FAISS


# -----------------------------
# Configuration
# -----------------------------
INDEX_PATH = "vector_index/faiss_index"
TOP_K = 5


# -----------------------------
# Load vector store
# -----------------------------
def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.load_local(
        INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectorstore


# -----------------------------
# Retrieval logic
# -----------------------------
def retrieve_relevant_chunks(
    question: str,
    scenario: str
) -> List[Dict]:
    """
    Retrieves top-k relevant regulatory text chunks
    based on the user question and scenario.
    """

    vectorstore = load_vectorstore()

    query = f"""
    Question: {question}
    Scenario: {scenario}
    """

    docs = vectorstore.similarity_search(query, k=TOP_K)

    results = []

    for doc in docs:
        results.append({
            "text": doc.page_content,
            "source": doc.metadata.get("source"),
            "page": doc.metadata.get("page"),
            "chunk_id": doc.metadata.get("chunk_id")
        })

    return results


# -----------------------------
# Manual test
# -----------------------------
if __name__ == "__main__":
    sample_question = "How should Common Equity Tier 1 capital be reported?"
    sample_scenario = "UK bank with ordinary shares and retained earnings."

    retrieved = retrieve_relevant_chunks(sample_question, sample_scenario)

    for i, r in enumerate(retrieved, start=1):
        print(f"\n--- Result {i} ---")
        print(f"Source: {r['source']} | Page: {r['page']}")
        print(r["text"][:500])
