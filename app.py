import streamlit as st
from prompts import get_system_prompt
import anthropic

st.set_page_config(page_title="BioAgent NGS/cfDNA", layout="wide")
st.title("🧬 BioAgent: NGS & cfDNA Assistant")

# Sidebar
with st.sidebar:
    st.header("Настройки анализа")
    task_type = st.selectbox("Тип задачи", [
        "Variant Calling (SNV/Indel)", 
        "CNV Analysis (cfDNA)", 
        "QC & Preprocessing",
        "Pipeline Generation (Snakemake)"
    ])
    st.info("Агент использует GATK Best Practices и специализированные инструменты для cfDNA.")

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Здравствуйте! Я BioAgent. Опишите ваш эксперимент (например, WES cfDNA, поиск мутаций EGFR), и я предложу пайплайн и код."}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Опишите задачу..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Здесь будет вызов API, пока заглушка
    with st.chat_message("assistant"):
        response = f"Анализирую задачу: {task_type}. Генерирую пайплайн..."
        st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
