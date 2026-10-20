import streamlit as st
import anthropic
import os
from dotenv import load_dotenv
from prompts import get_system_prompt
from rag_engine import get_rag_engine
from utils.exporters import extract_code_blocks, render_download_buttons
from utils.visualizer import render_visualization

load_dotenv()

# Инициализация клиента
auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN")
base_url = os.environ.get("ANTHROPIC_BASE_URL")
model = os.environ.get("ANTHROPIC_MODEL")

client = anthropic.Anthropic(auth_token=auth_token, base_url=base_url)

st.set_page_config(page_title="BioAgent NGS/cfDNA", layout="wide")
st.title("🧬 BioAgent: NGS & cfDNA Assistant")

# Инициализация RAG при старте
rag_engine = get_rag_engine()

# Sidebar с фильтрами RAG
with st.sidebar:
    st.header("Контекст анализа")
    task_type = st.selectbox("Фокус задачи", [
        "Variant Calling (SNV/Indel)", 
        "CNV & Fragmentomics (cfDNA)", 
        "QC & UMI Deduplication",
        "Pipeline Generation (Snakemake/Nextflow)"
    ])

    st.divider()
    st.subheader("🔍 RAG Filters")
    use_rag = st.checkbox("Использовать базу знаний", value=False)
    
    if use_rag:
        category_filter = st.multiselect(
            "Категории",
            ["tool_reference", "best_practices", "code_examples", "troubleshooting"],
            default=["tool_reference", "best_practices"]
        )
        top_k = st.slider("Количество источников", 3, 10, 5)
    
    st.divider()
    if st.button("🗑 Очистить историю"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    mode = st.radio(
        "Режим работы",
        ["💬 Чат-ассистент", "🔍 Code Review"],
        index=0
    )

# Основной контент в зависимости от режима
if mode == "💬 Чат-ассистент": 
    # Init messages
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Привет! Я BioAgent. Готов помочь с пайплайнами для NGS и cfDNA. Опишите ваш дизайн эксперимента."}
        ]

    # Render history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input с RAG
    if prompt := st.chat_input("Опишите задачу (например: WES cfDNA, поиск мутаций в TP53...)"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Ищу в базе знаний и анализирую..."):
                # RAG Retrieval
                rag_context = ""
                sources_used = []
                
                if use_rag:
                    # Определяем фильтр по утилите, если упоминается в запросе
                    tool_filter = None
                    known_tools = ["gatk", "fgbio", "bwa-mem2", "samtools", "picard", "ichorcna", "lofreq", "sinvict"]
                    for tool in known_tools:
                        if tool in prompt.lower():
                            tool_filter = tool
                            break
                    
                    # Получаем релевантные чанки
                    relevant_chunks = rag_engine.retrieve_relevant_context(
                        query=prompt,
                        top_k=top_k,
                        category_filter=category_filter[0] if len(category_filter) == 1 else None,
                        tool_filter=tool_filter
                    )
                    
                    # Форматируем контекст
                    if relevant_chunks:
                        rag_context = "\n\n### РЕЛЕВАНТНАЯ ИНФОРМАЦИЯ ИЗ БАЗЫ ЗНАНИЙ:\n\n"
                        for i, chunk in enumerate(relevant_chunks, 1):
                            rag_context += f"**Источник {i}:** {chunk['source']} (категория: {chunk['category']})\n"
                            rag_context += f"```\n{chunk['content']}\n```\n\n"
                            sources_used.append(chunk['source'])
                
                # Формируем system prompt с RAG контекстом
                base_system_prompt = get_system_prompt(task_type)
                full_system_prompt = base_system_prompt + rag_context
                
                # API Call
                api_messages = [m for m in st.session_state.messages if m["role"] != "system"]
                
                try:
                    with client.messages.stream(
                        model=model,
                        max_tokens=4096,
                        system=full_system_prompt,
                        messages=api_messages
                    ) as stream:
                        response_text = ""
                        text_placeholder = st.empty()
                        for text in stream.text_stream:
                            response_text += text
                            text_placeholder.markdown(response_text + "▌")
                        
                        text_placeholder.markdown(response_text)
                        
                        # Показываем использованные источники
                        if sources_used:
                            with st.expander("📚 Использованные источники"):
                                for source in set(sources_used):
                                    st.write(f"- {source}")
                    
                    st.session_state.messages.append({"role": "assistant", "content": response_text})

                    # Парсим код из ответа
                    code_blocks = extract_code_blocks(response_text)
                
                    # Рендерим кнопки скачивания
                    render_download_buttons(code_blocks)

                    # Рендерим кнопки визуализации
                    render_visualization(code_blocks)
                
                    # # Добавляем кнопку "Сгенерировать Dockerfile" если есть инструменты
                    # if code_blocks and st.button("🐳 Сгенерировать Dockerfile для этого пайплайна"):
                    #     # Определяем инструменты из контекста
                    #     detected_tools = _detect_tools_in_text(response_text)
                        
                    #     if detected_tools:
                    #         with st.spinner("Генерирую Dockerfile..."):
                    #             docker_prompt = generate_dockerfile_prompt(detected_tools)
                    #             # Вызов API с этим промптом...
                    #             # (код аналогичен основному чату)
                except Exception as e:
                    st.error(f"Ошибка API: {e}")

elif mode == "🔍 Code Review":
    st.title("🔍 Code Review для NGS-кода")
    st.markdown("Вставьте ваш код, и я проверю его на производительность, корректность и best practices для работы с NGS данными.")

    col1, col2 = st.columns([1, 3])
    with col1:
        review_lang = st.selectbox("Язык кода", ["Python", "R", "C++", "Snakemake"])
        review_focus = st.multiselect(
            "На чем сфокусироваться",
            ["Производительность", "Память", "Корректность NGS", "Воспроизводимость", "Стиль кода"],
            default=["Производительность", "Корректность NGS"]
        )
    
    with col2:
        code_input = st.text_area(
            "Ваш код:",
            height=400,
            placeholder="# Вставьте код здесь\nimport pysam\n\nbam = pysam.AlignmentFile('sample.bam')\n# ..."
        )
    
    if st.button("🚀 Запустить Code Review", type="primary"):
        if not code_input.strip():
            st.warning("Пожалуйста, вставьте код для ревью")
        else:
            with st.spinner("Анализирую код..."):
                review_prompt = f"""
Проведи детальный code review следующего {review_lang} кода для работы с NGS данными.

Сфокусируйся на следующих аспектах: {', '.join(review_focus)}

КРИТЕРИИ ПРОВЕРКИ:
1. **Производительность:** 
   - Используются ли векторизованные операции pandas/numpy вместо циклов?
   - Для C++: эффективное использование памяти, кэшей
   - Используются ли итераторы (pysam, pyvcf) вместо загрузки всего в память?

2. **Потребление памяти:**
   - Обрабатываются ли большие файлы (BAM, VCF) построчно/потоково?
   - Нет ли утечек памяти в циклах?
   - Используются ли генераторы вместо списков?

3. **Корректность NGS:**
   - Правильно ли обрабатываются multiallelic sites в VCF?
   - Учитывается ли качество баз (BASEQ) при фильтрации?
   - Правильно ли считается VAF (Variant Allele Frequency)?
   - Обрабатываются ли дубликаты (если нужно)?

4. **Воспроизводимость:**
   - Зафиксированы ли random seeds?
   - Указаны ли версии библиотек?
   - Есть ли обработка ошибок?

ФОРМАТ ОТВЕТА:
## 🚨 Критические проблемы
(список проблем, которые нужно исправить обязательно)

## ⚠️ Рекомендации
(улучшения производительности и стиля)

## ✅ Оптимизированный код
(полностью переписанный код с исправлениями)

## 📊 Оценка
(общая оценка кода от 1 до 10 с обоснованием)

КОД ДЛЯ РЕВЬЮ:
```{review_lang.lower()}
{code_input}
"""

                # Вызов API
                response = client.messages.create(
                    model=model,
                    max_tokens=4096,
                    system=get_system_prompt("Code Review"),
                    messages=[{"role": "user", "content": review_prompt}]
                )
                
                review_text = response.content[0].text
                
                # Отображаем результат
                st.markdown("---")
                st.markdown(review_text)
                
                # Парсим и даем скачать оптимизированный код
                code_blocks = extract_code_blocks(review_text)
                if code_blocks:
                    st.markdown("### 📦 Скачать оптимизированный код:")
                    render_download_buttons(code_blocks)
