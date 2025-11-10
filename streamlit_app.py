import streamlit as st
import shutil, glob, os

# ---------------------------------------------------
# ✅ HARD RESET: Delete Chroma DB files every rerun
# prevents "read-only database" crashes in Streamlit
# ---------------------------------------------------
for folder in ["db", "chroma", "index", ".chroma"]:
    shutil.rmtree(folder, ignore_errors=True)

for file in glob.glob("*.sqlite*"):
    os.remove(file)
# ---------------------------------------------------

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaLLM

st.set_page_config(page_title="RAG Demo", layout="wide")
st.title("📘 RAG Demo with Ollama + Streamlit")

uploaded_pdf = st.file_uploader("Upload a PDF", type=["pdf"])
query = st.text_input("Ask a question based on the PDF")

if uploaded_pdf:
    # Save uploaded PDF
    pdf_path = "uploaded.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_pdf.read())

    st.success("✅ PDF uploaded successfully.")

    # 1. Load PDF
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    # 2. Chunking
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(docs)

    # 3. Embeddings
    emb = OllamaEmbeddings(model="mxbai-embed-large")

    # 4. In-Memory Vector DB (streamlit-safe)
    db = Chroma.from_documents(chunks, emb)

    # 5. Retriever
    retriever = db.as_retriever(search_kwargs={"k": 5})

    # 6. LLM
    llm = OllamaLLM(model="llama3.1")

    if query:
        # Retrieve
        results = retriever.invoke(query)
        retrieved_text = "\n\n".join([doc.page_content for doc in results])

        # Build prompt
        prompt = f"""
You may ONLY use the text provided below.
Do not invent or guess anything.

TEXT START
{retrieved_text}
TEXT END

Answer the following question:
{query}
"""

        # LLM generate
        answer = llm.invoke(prompt)

        # Show answer
        st.subheader("✅ Answer")
        st.write(answer)

        # Show retrieved chunks
        with st.expander("🔍 Retrieved Chunks"):
            st.write(retrieved_text)

else:
    st.info("Upload a PDF to begin.")

