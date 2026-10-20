#!/bin/bash
set -e

echo "🧬 Starting BioAgent NGS/cfDNA..."

# Проверка API ключей
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ANTHROPIC_API_KEY not set"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY not set"
    exit 1
fi

# Проверка наличия FAISS индекса
if [ ! -f "data/faiss.index" ]; then
    echo "⚠️ FAISS index not found, building..."
    python scripts/ingest_docs.py
fi

echo "✅ All checks passed, starting Streamlit..."

# Запуск Streamlit
exec streamlit run app.py \
    --server.port=$PORT \
    --server.address=$HOST \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
