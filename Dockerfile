FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY auto_sync_all.py .

CMD ["python", "auto_sync_all.py", "30"]
