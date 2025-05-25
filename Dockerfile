# Dockerfile

FROM python:3.9-slim
ENV TZ=Europe/Amsterdam

# Render default project root
WORKDIR /opt/render/project/src

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos da aplicação
COPY . .

# Expondo a porta esperada
EXPOSE 8000

# Comando padrão para iniciar o servidor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]