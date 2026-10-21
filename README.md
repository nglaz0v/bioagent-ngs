# 🧬 BioAgent: NGS & cfDNA Assistant

AI-ассистент для биоинформатов и исследователей, работающих с NGS данными и cfDNA.

---

## 📋 О проекте

BioAgent — специализированный AI-ассистент для биоинформатиков, работающих с NGS данными и cfDNA (cell-free DNA). Проект решает ключевую проблему: **рутина, связанная с выбором инструментов, настройкой пайплайнов и интерпретацией результатов**.

### 🎯 Для кого этот проект?

- **Биоинформатики** — ускорение работы с пайплайнами в 3-12 раз
- **Молекулярные биологи** — помощь в анализе NGS данных без глубоких знаний программирования
- **Исследователи в области онкологии** — экспертиза по жидким биопсиям и cfDNA
- **Студенты** — обучение best practices в биоинформатике

### 💡 Почему BioAgent?

| Проблема | Решение BioAgent |
|----------|------------------|
| Гугление параметров утилит | 📚 RAG по документации GATK, fgbio, ichorCNA |
| Переписывание одного и того же кода | 📦 Экспорт пайплайнов в один клик |
| Ошибки в обработке NGS данных | 🔍 Code Review с NGS-специфичными проверками |
| Переключение контекста (чат → Jupyter) | 📊 Визуализация прямо в UI |

---

## ✨ Возможности

### 💬 Чат-ассистент с доменной экспертизой
- Глубокое понимание специфики cfDNA (низкий VAF, фрагментация ~166 bp, UMI)
- Знание GATK Best Practices, fgbio, bwa-mem2, ichorCNA
- Генерация Snakemake/Nextflow пайплайнов
- Стриминг ответов в реальном времени

### 🔍 Code Review для NGS-кода
- Проверка Python/R/C++ кода на производительность и корректность
- Поиск специфичных багов (неправильный парсинг VAF, multiallelic sites)
- Рекомендации по оптимизации памяти и скорости
- Автоматическая генерация исправленного кода

### 📦 Экспорт пайплайнов
- Скачивание Snakemake файлов, Dockerfile, config.yaml
- Автоматическая генерация Dockerfile с bioconda
- Правильные расширения файлов и именование

### 📊 Визуализация в UI
- Запуск matplotlib/plotly кода прямо в браузере
- Интерактивные графики (Manhattan plots, гистограммы фрагментов)
- Не нужно открывать Jupyter

### 📚 RAG по базе знаний
- 847 чанков из документации и статей
- Фильтрация по категориям и утилитам
- Точные параметры без галлюцинаций

---

## 📸 Скриншоты

### Основной интерфейс
<div align="center">
<img src="pics/query-1a.png.png" alt="Main Interface" width="800"/>
<p><em>Чат-интерфейс с боковой панелью настроек и RAG фильтрами</em></p>
</div>

### Code Review в действии
<div align="center">
<img src="pics/query-2a.png.png" alt="Code Review" width="800"/>
<p><em>Автоматический поиск баг в Python-коде для обработки VCF</em></p>
</div>

---

## 🏗 Архитектура

```
┌─────────────────┐
│  Streamlit UI   │
│  (app.py)       │
└────────┬────────┘
         │
         ├──────────────┐
         │              │
    ┌────▼────┐    ┌────▼─────┐
    │   RAG   │    │  Claude  │
    │ Engine  │    │   API    │
    │(FAISS)  │    │  3.5     │
    └────┬────┘    └────┬─────┘
         │              │
    ┌────▼────┐    ┌────▼─────┐
    │ OpenAI  │    │ Anthropic│
    │Embedding│    │          │
    └─────────┘    └──────────┘
```

### Компоненты

- **Streamlit UI** — интерактивный интерфейс с чатом, Code Review, визуализацией
- **RAG Engine** — векторный поиск по базе знаний (FAISS + OpenAI embeddings)
- **Claude 3.5 Sonnet** — генерация ответов и кода
- **Knowledge Base** — 847 чанков из документации GATK, fgbio, статей по cfDNA

---

## 🚀 Быстрый старт

### Локальная установка

#### Требования
- Python 3.10+
- API ключи: [Anthropic](https://console.anthropic.com/), [OpenAI](https://platform.openai.com/)
- 2 GB RAM (для FAISS индекса)

#### 1. Клонируйте репозиторий
```bash
git clone https://github.com/nikolay-ds/bioagent-ngs.git
cd bioagent-ngs
```

#### 2. Создайте виртуальное окружение
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

#### 3. Установите зависимости
```bash
pip install -r requirements.txt
```

#### 4. Настройте API ключи
```bash
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"
```

Или создайте файл `.env`:
```bash
ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key
```

#### 5. Соберите базу знаний (первый запуск)
```bash
python scripts/ingest_docs.py
```

Это создаст FAISS индекс из markdown-файлов в папке `docs/`. Занимает ~2 минуты.

#### 6. Запустите приложение
```bash
streamlit run app.py
```

Откройте браузер: `http://localhost:8501`

### Docker

```bash
# Сборка образа
docker build -t bioagent-ngs .

# Запуск
docker run -p 8501:7860 \
  -e ANTHROPIC_API_KEY=your-key \
  -e OPENAI_API_KEY=your-key \
  bioagent-ngs
```

---

## 📖 Использование

### Пример 1: Анализ WES cfDNA

**Запрос:**
```
Нужно проанализировать WES данные cfDNA для поиска соматических мутаций в TP53. 
Покрытие 1000x, парных нормальных образцов нет.
```

**Что сделает агент:**
1. Предложит пайплайн с Mutect2 в режиме tumor-only
2. Сгенерирует код для создания Panel of Normals (PoN)
3. Добавит фильтрацию germline resource (gnomAD)
4. Предоставит готовый Snakemake пайплайн
5. Даст кнопки для скачивания файлов

### Пример 2: Code Review

1. Переключитесь в режим "🔍 Code Review"
2. Вставьте свой Python-код:
```python
import pysam

vcf = pysam.VariantFile('sample.vcf.gz')
for record in vcf:
    vaf = record.info.get('VAF', 0)
    print(f"{record.pos}: {vaf}")
```
3. Агент найдет багу: `record.info.get('VAF', 0)` не работает для multiallelic sites
4. Предложит исправленный код с `record.samples[0]['AF']`

### Пример 3: Визуализация

**Запрос:**
```
Покажи код для визуализации распределения размеров фрагментов cfDNA
```

**Что сделает агент:**
1. Сгенерирует Python-код с matplotlib
2. Покажет кнопку "🚀 Запустить визуализацию"
3. Отрендерит график прямо в UI (пик ~166 bp)
