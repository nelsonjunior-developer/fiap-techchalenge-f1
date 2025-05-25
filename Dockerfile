# Dockerfile

FROM python:3.9-slim
ENV TZ=Europe/Amsterdam

# Render default project root
WORKDIR /opt/render/project/src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "echo '🟢 Executando create_tables.py' && python create_tables.py && echo '🚀 Iniciando API...' && uvicorn app.main:app --host 0.0.0.0 --port 8000"]




# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
