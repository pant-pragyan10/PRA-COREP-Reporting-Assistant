import os
import pickle
from typing import List, Dict

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

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
DATA_DIR = "data"
INDEX_DIR = "vector_index"
INDEX_PATH = os.path.join(INDEX_DIR, "faiss_index")
METADATA_PATH = os.path.join(INDEX_DIR, "metadata.pkl")

PRA_FILE = os.path.join(DATA_DIR, "pra_own_funds.pdf")
COREP_FILE = os.path.join(DATA_DIR, "corep_c01_instructions.pdf")


# -----------------------------
# Utility functions
# -----------------------------
def load_pdf_text(file_path: str) -> List[Dict]:
    """
    Reads a PDF and returns a list of text chunks with page-level metadata.
    """
    reader = PdfReader(file_path)
    documents = []

    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if text:
            documents.append({
                "text": text,
                "metadata": {
                    "source": os.path.basename(file_path),
                    "page": page_num
                }
            })

    return documents


def chunk_documents(documents: List[Dict]) -> List[Dict]:
    """
    Splits documents into smaller chunks suitable for embedding.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunked_docs = []

    for doc in documents:
        chunks = splitter.split_text(doc["text"])
        for i, chunk in enumerate(chunks):
            chunked_docs.append({
                "text": chunk,
                "metadata": {
                    **doc["metadata"],
                    "chunk_id": i
                }
            })

    return chunked_docs


# -----------------------------
# Main ingestion logic
# -----------------------------
def build_or_load_index(rebuild: bool = False):
    """
    Builds a FAISS index if not present, otherwise loads it from disk.
    """
    if not rebuild and os.path.exists(INDEX_PATH):
        print("Loading existing vector index...")
        vectorstore = FAISS.load_local(
            INDEX_PATH,
            HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
            allow_dangerous_deserialization=True
        )
        return vectorstore

    print("Building new vector index...")

    # Load documents (fall back to sample text when PDFs are missing)
    pra_docs = []
    corep_docs = []

    if os.path.exists(PRA_FILE):
        pra_docs = load_pdf_text(PRA_FILE)
    else:
        print(f"WARNING: {PRA_FILE} not found — using placeholder PRA text.")
        pra_docs = [{
            "text": "Placeholder PRA own funds guidance text.",
            "metadata": {"source": "placeholder_pra.txt", "page": 1}
        }]

    if os.path.exists(COREP_FILE):
        corep_docs = load_pdf_text(COREP_FILE)
    else:
        print(f"WARNING: {COREP_FILE} not found — using placeholder COREP instructions text.")
        corep_docs = [{
            "text": "Placeholder COREP C01 instructions excerpt.",
            "metadata": {"source": "placeholder_corep.txt", "page": 1}
        }]

    all_docs = pra_docs + corep_docs

    # Chunk documents
    chunked_docs = chunk_documents(all_docs)

    texts = [doc["text"] for doc in chunked_docs]
    metadatas = [doc["metadata"] for doc in chunked_docs]

    # Embeddings (local, fast, reliable)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas
    )

    os.makedirs(INDEX_DIR, exist_ok=True)
    vectorstore.save_local(INDEX_PATH)

    print("Vector index saved locally.")
    return vectorstore


# -----------------------------
# Script entry point
# -----------------------------
if __name__ == "__main__":
    build_or_load_index(rebuild=False)
