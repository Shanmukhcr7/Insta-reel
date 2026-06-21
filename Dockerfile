FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Install dependencies, including ffmpeg if yt-dlp needs it for merging formats
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Expose port
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
