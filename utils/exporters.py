import re
import streamlit as st
from typing import List, Dict

def extract_code_blocks(markdown_text: str) -> List[Dict]:
    """Парсит markdown и извлекает блоки кода"""
    # Паттерн для ```language\ncode\n```
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, markdown_text, re.DOTALL)
    
    code_blocks = []
    for lang, code in matches:
        lang = lang.lower() if lang else "text"
        
        # Маппинг языков на расширения файлов
        ext_map = {
            "python": "py",
            "py": "py",
            "snakefile": "smk",
            "snakemake": "smk",
            "smk": "smk",
            "r": "R",
            "bash": "sh",
            "sh": "sh",
            "dockerfile": "Dockerfile",
            "yaml": "yml",
            "yml": "yml",
            "cpp": "cpp",
            "c++": "cpp"
        }
        
        ext = ext_map.get(lang, "txt")
        
        # Определяем осмысленное имя файла
        filename = _guess_filename(lang, code, ext)
        
        code_blocks.append({
            "language": lang,
            "code": code.strip(),
            "extension": ext,
            "filename": filename
        })
    
    return code_blocks

def _guess_filename(lang: str, code: str, ext: str) -> str:
    """Пытается угадать осмысленное имя файла из содержимого"""
    code_lower = code.lower()
    
    if lang in ["snakefile", "snakemake", "smk"]:
        if "variant_calling" in code_lower:
            return "variant_calling.smk"
        elif "qc" in code_lower:
            return "qc_pipeline.smk"
        return "Snakefile"
    
    if lang == "dockerfile":
        return "Dockerfile"
    
    if lang in ["yaml", "yml"]:
        return "config.yaml"
    
    if lang == "python":
        if "ichorcna" in code_lower:
            return "run_ichorcna.py"
        elif "visualization" in code_lower or "plot" in code_lower:
            return "visualize.py"
        return "script.py"
    
    if lang == "r":
        return "analysis.R"
    
    return f"code.{ext}"

def render_download_buttons(code_blocks: List[Dict]):
    """Рендерит кнопки скачивания для каждого блока кода"""
    if not code_blocks:
        return
    
    st.markdown("---")
    st.markdown("**📦 Скачать сгенерированный код:**")
    
    cols = st.columns(min(len(code_blocks), 4))
    
    for i, block in enumerate(code_blocks):
        col = cols[i % len(cols)]
        with col:
            # Определяем MIME тип
            mime_map = {
                "py": "text/x-python",
                "smk": "text/plain",
                "R": "text/plain",
                "sh": "text/x-shellscript",
                "Dockerfile": "text/plain",
                "yml": "text/yaml",
                "cpp": "text/x-c++src"
            }
            mime = mime_map.get(block["extension"], "text/plain")
            
            st.download_button(
                label=f"📥 {block['filename']}",
                data=block["code"],
                file_name=block["filename"],
                mime=mime,
                key=f"download_{i}_{hash(block['code'])}"
            )

def generate_dockerfile_prompt(tools: List[str]) -> str:
    """Генерирует промпт для создания Dockerfile"""
    tools_str = ", ".join(tools)
    return f"""
Сгенерируй Dockerfile для биоинформатического пайплайна со следующими инструментами: {tools_str}.

Требования:
- Базовый образ: condaforge/mambaforge (или miniforge3)
- Используй bioconda и conda-forge каналы
- Укажи конкретные версии инструментов (последние стабильные)
- Добавь метаданные (LABEL maintainer, version)
- Оптимизируй размер (multi-stage build если нужно, очистка кэша conda)
- Добавь ENTRYPOINT и CMD
- Верни ТОЛЬКО код Dockerfile в блоке ```dockerfile
"""
