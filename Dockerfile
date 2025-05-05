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

# 5. (Optional) Create the tables before running
#    This assumes your processor module will run metadata.create_all()
# ENTRYPOINT ["python", "-c", "from database.db import Base, engine; Base.metadata.create_all(bind=engine)"]

# 6. Default command: run your ETL processor
CMD ["python", "-m", "captura.processor"]