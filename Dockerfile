# Dockerfile

# 1. Base image with Python
FROM python:3.9-slim

# Time zone
ENV TZ=Europe/Amsterdam

# 2. Set a working directory
WORKDIR /app

# 3. Copy and install dependencies first (cacheable layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy all of your application code
COPY . .