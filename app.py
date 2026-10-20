import streamlit as st
import anthropic
import os
from dotenv import load_dotenv
from prompts import get_system_prompt

load_dotenv()

# Инициализация клиента
auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN")
base_url = os.environ.get("ANTHROPIC_BASE_URL")
model = os.environ.get("ANTHROPIC_MODEL")
# api_key = os.environ.get("ANTHROPIC_API_KEY")
# if not api_key:
#     st.error("API ключ не найден. Установите переменную окружения ANTHROPIC_API_KEY.")
#     st.stop()

client = anthropic.Anthropic(auth_token=auth_token, base_url=base_url)

st.set_page_config(page_title="BioAgent NGS/cfDNA", layout="wide")
st.title("🧬 BioAgent: NGS & cfDNA Assistant")

# Sidebar
with st.sidebar:
    st.header("Контекст анализа")
    task_type = st.selectbox("Фокус задачи", [
        "Variant Calling (SNV/Indel)", 
        "CNV & Fragmentomics (cfDNA)", 
        "QC & UMI Deduplication",
        "Pipeline Generation (Snakemake/Nextflow)"
    ])
    st.divider()
    if st.button("🗑 Очистить историю"):
        st.session_state.messages = []
        st.rerun()

# Init messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Привет! Я BioAgent. Готов помочь с пайплайнами для NGS и cfDNA. Опишите ваш дизайн эксперимента."}
    ]

# Render history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Опишите задачу (например: WES cfDNA, поиск мутаций в TP53...)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # API Call with Streaming
    with st.chat_message("assistant"):
        with st.spinner("Анализирую протокол и подбираю инструменты..."):
            system_prompt = get_system_prompt(task_type)
            
            # Формируем историю для API
            api_messages = [m for m in st.session_state.messages if m["role"] != "system"]
            
            try:
                with client.messages.stream(
                    model=model,
                    max_tokens=4096,
                    system=system_prompt,
                    messages=api_messages
                ) as stream:
                    response_text = ""
                    text_placeholder = st.empty()
                    for text in stream.text_stream:
                        response_text += text
                        text_placeholder.markdown(response_text + "▌")
                    
                    text_placeholder.markdown(response_text) # Убираем курсор в конце
                    
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                st.error(f"Ошибка API: {e}")
