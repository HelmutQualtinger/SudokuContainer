# Basis-Image
FROM python:3.9-slim

# Arbeitsverzeichnis
WORKDIR /app

# Flask installieren
RUN pip install flask

# Code kopieren
COPY . .

# Port freigeben
EXPOSE 5000

# App starten
CMD ["python", "app.py"]