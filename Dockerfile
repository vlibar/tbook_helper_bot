# ---- Base image -------------------------------------------------
FROM python:3.12-slim

# ---- System packages (keep gcc for the whole build) -------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ---- Install TA‑Lib C library (source) -------------------------
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# ---- Python environment -----------------------------------------
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy bot code ---------------------------------------------
COPY . .

# ---- Clean up compiler (optional, reduces image size) ----------
# Uncomment the two lines below if you want a smaller final image
# RUN apt-get purge -y --auto-remove build-essential wget && \
#     rm -rf /var/lib/apt/lists/*

# ---- Start command ---------------------------------------------
CMD ["python", "bot.py"]