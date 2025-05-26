# 📊 FIAP Tech Challenge - Fase 1

Este projeto é parte do Tech Challenge da FIAP e tem como objetivo central coletar e disponibilizar via API pública os dados de vitivinicultura da Embrapa, que podem ser utilizados futuramente para alimentar modelos de Machine Learning.

---

## 🚀 Visão Geral

A aplicação consiste em:

- Extração de dados do site oficial da Embrapa via scraping atraves do beautifulsoup4.
- Armazenamento estruturado em banco de dados PostgreSQL.
- Exposição desses dados por meio de uma REST API criada com FastAPI.
- Execução agendada de scrapers com APScheduler.
- Execução de testes automatizados com Pytest.
- Deploy via Docker Compose.

---

## 🏗️ Estrutura do Projeto
```
fiap-techchalenge-f1/
├── app/                    # Aplicação principal da API FastAPI
│   ├── main.py             # Entrypoint da aplicação FastAPI
│   ├── routes/             # Rotas da API (produção, comercialização, etc)
│   │   ├── producao.py
│   │   ├── comercializacao.py
│   │   ├── processamento.py
│   │   ├── importacao.py
│   │   ├── exportacao.py
│   │   └── auth.py         # Rota de autenticação
│   └── tests/              # Testes automatizados com Pytest
│       ├── routes/         # Testes de integração das rotas da API
│       │   ├── producao_test.py
│       │   ├── comercializacao_test.py
│       │   ├── processamento_test.py
│       │   ├── importacao_test.py
│       │   ├── exportacao_test.py
│       │   └── auth_test.py  # Testes da rota de autenticação
├── auth/                   # Módulo de autenticação (na raiz do projeto)
│   ├── jwt.py              # Lógica para geração e validação de tokens JWT
│   ├── schemas.py          # Schemas relacionados à autenticação
│   └── services.py         # Serviços de autenticação
├── captura/                # Módulo responsável pelo web scraping
│   ├── scrapers/           # Scrapers específicos por tipo de dado
│   ├── processor.py        # Processo de ETL dos dados
│   ├── scheduler.py        # Agendador de scraping com APScheduler
├── database/               # Lógica de banco de dados (PostgreSQL)
│   ├── db.py               # Engine e sessão SQLAlchemy
│   ├── models/             # Modelos ORM das tabelas
│   └── repos/              # Repositórios para acesso a dados
├── run_api_tests.sh        # Script automatizado para rodar testes via Docker
├── requirements.txt        # Dependências da aplicação
├── docker-compose.yml      # Configuração dos containers
├── Dockerfile              # Imagem da aplicação FastAPI
└── README.md               # Documentação do projeto
```

## 🌐 Endpoints da API

A API possui as seguintes rotas:

### Produção

- `GET /v1/producao/`
  - Parâmetros opcionais: `ano`, `item`
  - Exemplo de resposta:
    ```json
    {
      "ano": 2020,
      "item": "SUCO",
      "quantidade": 15000
    }
    ```

### Comercialização

- `GET /v1/comercializacao/`
  - Parâmetros opcionais: `ano`, `item`
  - Exemplo de resposta:
    ```json
    {
      "ano": 2021,
      "item": "ESPUMANTES",
      "valor": 20000
    }
    ```

### Processamento

- `GET /v1/processamento/`
  - Parâmetros opcionais: `ano`, `category`, `grape_type`
  - Ex: `/v1/processamento/?ano=2020&category=TINTAS&grape_type=viniferas`

### Importação

- `GET /v1/importacao/`
  - Parâmetros opcionais: `ano`, `categoria`
  - Ex: `/v1/importacao/?ano=2019&categoria=vinhos_de_mesa`

### Exportação

- `GET /v1/exportacao/`
  - Parâmetros opcionais: `ano`, `categoria`
  - Ex: `/v1/exportacao/?ano=2022&categoria=espumantes`

---

## 🚀 Como Executar Localmente com Docker Compose

### Pré-requisitos

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Passos para rodar o projeto:

```bash
# 1. Clone o repositório
git clone https://github.com/nelsonjunior-developer/fiap-techchalenge-f1.git
cd fiap-techchalenge-f1

# 2. Inicie todos os containers do projeto
docker-compose up --build
```

## Banco de dados
#### Para acessar o PgAdmin (PostgreSQL UI) depois que os containers foram iniciados no passo anterior, execute o seguinte comando do docker:
1. Run this command:
```shell
docker run -d \
  --name pgadmin \
  --network fiap-techchalenge-f1_fiap_net \
  -p 8080:80 \
  -e PGADMIN_DEFAULT_EMAIL=admin@admin.com \
  -e PGADMIN_DEFAULT_PASSWORD=admin \
  dpage/pgadmin4
```
2. Entao acesso atraves do link:
[http://localhost/browser](http://localhost/browser/)

---

## 🧪 Como Rodar os Testes

### Com Docker utilizando o script de testes (recomendado):

```bash
./run_api_tests.sh
```

### Manualmente:

```bash
docker-compose up -d --build
docker-compose exec fiap_api bash
PYTHONPATH=/app pytest /app/app/tests/
```

---

## 📦 Dependências

Listadas em `requirements.txt`:

- [FastAPI](https://fastapi.tiangolo.com/) == 0.95.2
- [SQLAlchemy](https://www.sqlalchemy.org/) == 1.4.46
- [APScheduler](https://apscheduler.readthedocs.io/) == 3.10.1
- ...

---

## 📤 Deploy

A aplicacao se encontra atualmente deployada no render e pode ser acessada atraves do seguinte link:  
[Renderer](https://fiap-techchalenge-f1.onrender.com/docs)

Cenário de uso proposto para ML
Prevendo a produção de uva por tipo e região com base em dados históricos de comercialização, importação e processamento.