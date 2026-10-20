import os
import json
import tiktoken
from pathlib import Path
from typing import List, Dict

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Разбивает текст на чанки с перекрытием"""
    encoding = tiktoken.encoding_for_model("gpt-4o")  # "claude-3-5-sonnet"
    tokens = encoding.encode(text)
    
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunks.append(encoding.decode(chunk_tokens))
        start = end - overlap
    
    return chunks

def extract_tool_name(filename: str) -> str:
    """Извлекает имя утилиты из имени файла"""
    known_tools = ["gatk", "fgbio", "bwa-mem2", "samtools", "picard", "ichorcna", "lofreq", "sinvict"]
    filename_lower = filename.lower()
    for tool in known_tools:
        if tool in filename_lower:
            return tool
    return "general"

def categorize_document(filename: str, content: str) -> str:
    """Определяет категорию документа"""
    filename_lower = filename.lower()
    content_lower = content.lower()
    
    if "reference" in filename_lower or "parameters" in filename_lower:
        return "tool_reference"
    elif "best_practices" in filename_lower or "guidelines" in filename_lower:
        return "best_practices"
    elif "example" in filename_lower or "snippet" in filename_lower or "```" in content:
        return "code_examples"
    elif "troubleshoot" in filename_lower or "faq" in filename_lower:
        return "troubleshooting"
    else:
        return "general"

def ingest_docs(docs_dir: str = "docs/", output_file: str = "data/knowledge_base.jsonl"):
    """Основная функция парсинга"""
    docs_path = Path(docs_dir)
    chunks_data = []
    
    for md_file in docs_path.glob("*.md"):
        print(f"Processing {md_file.name}...")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tool_name = extract_tool_name(md_file.name)
        category = categorize_document(md_file.name, content)
        
        chunks = chunk_text(content)
        
        for i, chunk in enumerate(chunks):
            chunks_data.append({
                "id": f"{md_file.stem}_chunk_{i}",
                "source": md_file.name,
                "category": category,
                "tool_name": tool_name,
                "content": chunk,
                "chunk_index": i
            })
    
    # Сохраняем в JSONL
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in chunks_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"✅ Ingested {len(chunks_data)} chunks to {output_file}")

if __name__ == "__main__":
    ingest_docs()
