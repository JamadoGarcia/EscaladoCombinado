FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN pip install gunicorn

COPY . .

# Exponer puerto
EXPOSE 5000

# 👇 Arrancar con Gunicorn en vez de flask run
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
