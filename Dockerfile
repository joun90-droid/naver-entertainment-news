FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Cloud Run uses PORT environment variable (default 8080)
EXPOSE 8080

CMD ["python", "server.py"]
