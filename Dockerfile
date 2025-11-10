# Dockerfile
FROM python:3.12-slim

# ---- System deps for TA‑Lib C library ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential wget && \
    wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && ./configure --prefix=/usr && make && make install && \
    cd .. && rm -rf ta-lib* && \
    apt-get purge -y --auto-remove build-essential wget && \
    rm -rf /var/lib/apt/lists/* \

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "bot.py"]