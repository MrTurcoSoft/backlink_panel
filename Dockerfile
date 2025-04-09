FROM python:3.12-slim

# Gerekli sistem paketlerini kur
RUN apt-get update && apt-get install -y gcc g++ libmariadb-dev curl

# Çalışma dizinini ayarla
WORKDIR /app

# Kodları kopyala
COPY . .

# Gereksinimleri kur
RUN pip install --no-cache-dir -r requirements.txt

# Ortam değişkenleri
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Uygulamayı başlat
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
