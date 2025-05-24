#!/bin/bash

set -e

# Função para parar os containers quando o script for interrompido
cleanup() {
  echo -e "\n🧹 Encerrando containers..."
  docker-compose down
  exit 1
}

# Captura interrupções (Ctrl+C, etc.)
trap cleanup SIGINT SIGTERM

echo "🔄 (1/4) Buildando e subindo os containers..."
docker-compose up -d --build

echo "⏳ (2/4) Aguardando o container fiap_api estar pronto..."
until docker-compose exec fiap_api ls > /dev/null 2>&1; do
  sleep 1
done

echo "🧪 (3/4) Executando TODOS os testes da API dentro do container..."

# Cria um arquivo temporário para armazenar logs
LOG_FILE=$(mktemp)

# Executa os testes e salva saída no log
docker-compose exec fiap_api bash -c "PYTHONPATH=/app pytest /app/app/tests/" | tee "$LOG_FILE"
test_status=${PIPESTATUS[0]}

# Exibe os logs
echo "📄 Logs dos testes:"
cat "$LOG_FILE"

# Remove log temporário
rm "$LOG_FILE"

# Encerra os containers normalmente após os testes
echo "🧹 Finalizando containers após execução dos testes..."
docker-compose down

# Avalia resultado
if [ $test_status -eq 0 ]; then
  echo "✅ (4/4) Todos os testes passaram com sucesso."
else
  echo "❌ (4/4) Alguns testes falharam. Veja os logs acima."
  exit $test_status
fi