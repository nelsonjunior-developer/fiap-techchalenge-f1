# Dockerfile

# 1. Base image
FROM python:3.9-slim

# 2. Time zone
ENV TZ=Europe/Amsterdam

# 3. Working directory
WORKDIR /app

# 4. Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application
COPY . .

# 6. Expose the port that Render will connect to
EXPOSE 8000

# 7. Entrypoint using the PORT from Render
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["sh", "-c", "python create_tables.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]