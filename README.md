---
title: BioAgent NGS/cfDNA
emoji: 🧬
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: true
short_description: AI-ассистент для биоинформатиков (NGS, cfDNA, жидкая биопсия)
---

# 🧬 BioAgent: NGS & cfDNA Assistant

AI-ассистент для биоинформатов и исследователей, работающих с NGS данными и cfDNA.

## Возможности
- 💬 Чат-ассистент с экспертизой в GATK, fgbio, ichorCNA
- 🔍 Code Review для NGS-кода (Python/R/C++)
- 📦 Экспорт пайплайнов (Snakemake, Dockerfile)
- 📊 Визуализация графиков прямо в UI
- 📚 RAG по базе знаний (GATK Best Practices, документация)

## Использование
Опишите ваш эксперимент, например:
- *"WES cfDNA, поиск соматических мутаций в TP53, покрытие 1000x"*
- *"Как сделать UMI deduplication для таргетной панели?"*
- *"Проверь мой Python-скрипт для обработки VCF"*

## Технологии
- Anthropic Claude 3.5 Sonnet
- OpenAI Embeddings (text-embedding-3-small)
- FAISS для векторного поиска
- Streamlit для UI

![CI/CD](https://github.com/nglaz0v/bioagent-ngs/actions/workflows/ci.yml/badge.svg)
