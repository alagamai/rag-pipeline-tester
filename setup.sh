#!/bin/bash

echo "--------------------------------------"
echo "🧩 RAG + Ollama Environment Setup"
echo "--------------------------------------"

PROJECT_ROOT="$(pwd)"
VENV_PATH="$PROJECT_ROOT/.rag_env"

echo "📁 Project root: $PROJECT_ROOT"


# ----------------------------------------------------
# 1️⃣ Create/Activate Virtual Environment
# ----------------------------------------------------
if [ ! -d "$VENV_PATH" ]; then
    echo "🧱 Creating virtual environment (.rag_env)..."
    python3 -m venv "$VENV_PATH"
else
    echo "✅ Virtual environment already exists."
fi

echo "📦 Activating environment..."
source "$VENV_PATH/bin/activate"


# ----------------------------------------------------
# 2️⃣ Verify/Install Ollama
# ----------------------------------------------------
echo "🔍 Checking for Ollama..."

if ! command -v ollama &> /dev/null; then
    echo "⚙️ Ollama not found. Installing using Homebrew..."
    brew install ollama
else
    echo "✅ Ollama is already installed."
fi


# ----------------------------------------------------
# 3️⃣ Start Ollama server if not running
# ----------------------------------------------------
echo "🚀 Starting Ollama server..."

# kill old instance
PID=$(lsof -ti tcp:11434)
if [ ! -z "$PID" ]; then
    echo "🧹 Stopping old Ollama service..."
    kill -9 "$PID"
fi

# start fresh
ollama serve &

# wait for server
echo "⏳ Waiting for Ollama to start..."
sleep 3

# check API
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama server is running."
else
    echo "❌ ERROR: Ollama server is not responding."
    echo "👉 Try running: ollama serve"
    exit 1
fi


# ----------------------------------------------------
# 4️⃣ Install Python Libraries Needed for RAG
# ----------------------------------------------------
echo "📦 Installing RAG dependencies..."

pip install --upgrade pip

pip install \
    langchain \
    langchain-core \
    langchain-community \
    langchain-text-splitters \
    langchain-ollama \
    chromadb \
    pypdf \
    python-dotenv \
    streamlit

# ----------------------------------------------------
# 5️⃣ Pull Required Ollama Models
# ----------------------------------------------------
echo "📥 Pulling Ollama models..."

ollama pull mxbai-embed-large
ollama pull llama3.1


# ----------------------------------------------------
# 6️⃣ Verify Setup (LLM + Embedding)
# ----------------------------------------------------
echo "✅ Verifying final setup..."

python - <<EOF
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaLLM
print("✅ LangChain + Chroma + Ollama stack is working.")
EOF


echo "--------------------------------------"
echo "✅ RAG Setup Complete"
echo "Activate environment with:"
echo "   source .rag_env/bin/activate"
echo "Run your RAG demo with:"
echo "   python rag_simple.py"
echo "--------------------------------------"

