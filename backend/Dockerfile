FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Write Google credentials from env vars at startup, then run the app
CMD ["sh", "-c", "echo \"$GOOGLE_CREDENTIALS\" | base64 -d > credentials.json && echo \"$GOOGLE_TOKEN\" | base64 -d > token.json && python main.py"]
