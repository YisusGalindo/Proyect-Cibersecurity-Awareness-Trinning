FROM python:3.11-slim

# Instalar dependencias del sistema para matplotlib y reportlab
RUN apt-get update && apt-get install -y --no-install-recommends \
    libfreetype6 libpng16-16 libjpeg62-turbo libfontconfig1 fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python", "report.py"]