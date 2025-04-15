FROM python:3.12-slim

# Gerekli sistem paketlerini kur
RUN apt-get update && apt-get install -y gcc g++ libmariadb-dev curl

# Çalışma dizinini ayarla
WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# ---  Chrome / chromedriver  ---------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        chromium-driver \
        chromium \
        fonts-liberation \
        libasound2 \
        libnss3 \
        libx11-xcb1 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        libgbm1 \
        libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV PATH="$PATH:/usr/bin"

# -------------------------------------------------------------


# Ortam değişkenleri
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Uygulamayı başlat
CMD ["gunicorn", "-w", "4", "-t", "120", "-b", "0.0.0.0:5000", "run:app"]

