FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download model at build time to avoid download on first run
RUN python -c "from transformers import pipeline; pipeline('sentiment-analysis'); pipeline('summarization', model='t5-small')"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
