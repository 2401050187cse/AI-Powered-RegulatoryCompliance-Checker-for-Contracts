# rag_system.py
"""
Contract Compliance Analyzer + RAG
Output matches screenshot exactly.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# LangChain imports
# ---------------- LangChain (Modern 1.2+) ----------------

# Document loading
from langchain_community.document_loaders import TextLoader, PyPDFLoader

# Text splitting
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Vector store
from langchain_community.vectorstores import FAISS

# Embeddings
from langchain_community.embeddings import HuggingFaceEmbeddings


# Prompt & runnable pipeline
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# LLM (Groq)
from langchain_groq import ChatGroq



from langchain_groq import ChatGroq


# ---------------- CONFIG ----------------

DATASET_PATH = Path(r"D:\AI-Powered-RegulatoryCompliance-Checker-for-Contracts\Dataset")
INDEX_PATH = Path("./faiss_index")
REBUILD_INDEX = True

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHAT_MODEL = "llama-3.1-8b-instant"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 4

QUESTION = """
Analyze the contract against compliance standards and provide output in this strict format:

Analysis Result:

KEY CLAUSES:
- Clause Name (Clause #)
- Clause Name (Clause #)

POTENTIAL COMPLIANCE ISSUES:
- Issue description (Risk Level: Low/Medium/High)
Reason: Explain clearly.

Only use the provided context.
"""


# -------------- LOAD API KEY --------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise SystemExit("❌ ERROR: Add GROQ_API_KEY to .env file")


# -------------- LOAD DOCUMENTS --------------
def find_files(path: Path):
    allowed = {".txt", ".pdf"}
    return [p for p in path.rglob("*") if p.suffix.lower() in allowed]


def load_documents(paths):
    docs = []
    for p in paths:
        try:
            if p.suffix.lower() == ".txt":
                docs.extend(TextLoader(str(p)).load())
            elif p.suffix.lower() == ".pdf":
                docs.extend(PyPDFLoader(str(p)).load())
        except Exception as e:
            print(f"[WARN] Cannot load {p}: {e}")
    return docs


# -------------- SPLIT DOCS --------------
def split_docs(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_documents(docs)


# -------------- FAISS --------------
def build_faiss(chunks):
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

    if REBUILD_INDEX or not INDEX_PATH.exists():
        print("🔁 Building FAISS index...")
        vs = FAISS.from_documents(chunks, embeddings)
        INDEX_PATH.mkdir(exist_ok=True)
        vs.save_local(str(INDEX_PATH))
        print("✅ Index saved.")
        return vs

    print("📦 Loading FAISS index...")
    return FAISS.load_local(
        str(INDEX_PATH),
        embeddings,
        allow_dangerous_deserialization=True
    )


# -------------- RETRIEVER --------------
def get_retriever(vs):
    return vs.as_retriever(
        search_type="mmr",
        search_kwargs={"k": TOP_K}
    )


# -------------- RAG CHAIN --------------
def make_chain(retriever):
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a senior legal compliance AI. "
            "Provide structured contract compliance analysis "
            "using ONLY the given context."
        ),
        (
            "human",
            "Question:\n{input}\n\nContext:\n{context}"
        )
    ])

    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=CHAT_MODEL,
        temperature=0.1
    )

    chain = (
        {
            "context": retriever,
            "input": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain



# -------------- MAIN --------------
def main():
    print("🚀 Starting Contract Compliance RAG Analyzer...\n")

    files = find_files(DATASET_PATH)
    if not files:
        raise SystemExit("❌ No documents found in Dataset folder!")

    print(f"📄 Found {len(files)} contract files")

    docs = load_documents(files)
    chunks = split_docs(docs)

    print(f"✂️ Created {len(chunks)} chunks")

    vs = build_faiss(chunks)
    retriever = get_retriever(vs)
    chain = make_chain(retriever)

    print("🔍 Analyzing contract against compliance standards...\n")

    resp = chain.invoke(QUESTION)

    print("📝 Analysis Result:\n")
    print(resp)



if __name__ == "__main__":
    main()
