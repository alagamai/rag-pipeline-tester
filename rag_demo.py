from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaLLM

# 1. Load PDF
loader = PyPDFLoader("rag_study.pdf")
docs = loader.load()

# 2. Chunk (larger chunks keep sections together)
splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
chunks = splitter.split_documents(docs)

# 3. Embeddings
emb = OllamaEmbeddings(model="mxbai-embed-large")

# 4. Vector DB
db = Chroma.from_documents(chunks, emb, persist_directory="./db")

# 5. LLM
llm = OllamaLLM(model="llama3.1")

# 6. Stronger retriever
retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)


# 7. Retrieval query
query = "Find the RAG sections and related headings."
results = retriever.invoke(query)

print("\n=== RETRIEVED CHUNKS ===")
for d in results:
    print(d.page_content[:350])
    print("\n----------------------------\n")

context = "\n\n".join([d.page_content for d in results])

# 8. Build prompt
prompt = f"""
You may ONLY use the text provided below.
Do not invent or guess anything.

TEXT START
{context}
TEXT END

Your task:
1. List all section titles.
2. From the 3rd section, extract the first 2 lines exactly as written.
3. Do NOT paraphrase.
4. If text is incomplete, return only what is present.
"""

# 9. Ask the model
answer = llm.invoke(prompt)
print("\n=== ANSWER ===\n")
print(answer)

