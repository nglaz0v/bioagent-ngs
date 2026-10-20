FROM python:3.10-slim as builder

# Системные зависимости для pysam и сборки
RUN apt-get update && apt-get install -y \
    build-essential \
    zlib1g-dev \
    libbz2-dev \
    liblzma-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Кэшируем установку зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Runtime stage
FROM python:3.10-slim

# Системные зависимости для runtime
RUN apt-get update && apt-get install -y \
    libhtslib1.14 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем установленные Python-пакеты
COPY --from=builder /install /usr/local

# Копируем код и данные
COPY . .

# Делаем entrypoint исполняемым
RUN chmod +x entrypoint.sh

# HF Spaces требует порт 7860
ENV PORT=7860
ENV HOST=0.0.0.0

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/_stcore/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]
