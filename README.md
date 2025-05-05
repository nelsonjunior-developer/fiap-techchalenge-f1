# fiap-techchalenge-f1
Fiap Tech Chalenge Fase 1

Estrutura basica do projeto:
```
/projeto_fiap
│
├── .venv/                      # Virtualenv: isolated Python environment                    
│   └── …                                            
│
├── app/                        # Main API application
│   ├── main.py                 # Entry point for the Flask/FastAPI server
│   └── routes/                 # HTTP route definitions (one file per resource)
│       └── …                   
│
├── auth/                       # Authentication & Authorization
│   ├── jwt_handler.py          # Create & verify JWT tokens
│   ├── auth_service.py         # Login logic, credential validation
│   └── schemas.py              # Pydantic models: LoginRequest, TokenResponse, etc.
│
├── captura/                    # Scraping module for Embrapa data
│   ├── __init__.py             # Package indicator
│   ├── config.py               # URLs, timeouts, retry counts, constants
│   ├── data_handler.py         # Cleanse & validate scraped values
│   ├── exceptions.py           # Custom exceptions: ScrapeError, ParseError, etc.
│   ├── processor.py            # ETL orchestration for scraping and saving
│   ├── scheduler.py            # APScheduler setup to run scrapes on a schedule
│   ├── scrapers/               # Separated scraper logic by tab
│   │   ├── __init__.py         
│   │   ├── producao_scraper.py           # Scraping da aba Produção
│   │   ├── commercializacao_scraper.py   # Scraping da aba Comercialização
│   │   └── processamento_scraper.py      # Scraping da aba Processamento
│   └── tests/                  # Unit & integration tests for this module
│       ├── __init__.py         
│       ├── test_scraper.py     
│       ├── test_data_handler.py
│       └── test_scheduler.py   
│
├── database/                   # Database connectivity, models, and repos
│   ├── __init__.py             # Package root
│   ├── db.py                   # SQLAlchemy engine, SessionLocal, Base
│   ├── fake_users.py           # In-memory user fixtures for testing auth
│   │
│   ├── models/                 # SQLAlchemy ORM table definitions
│   │   ├── __init__.py         
│   │   ├── producao.py         # Producao model (item, subitem, quantidade, created, updated)
│   │   ├── processamento.py    # Processamento model (category, variety, quantidade, grape_type)
│   │   ├── error_log.py        # ErrorLog model (timestamp, stage, error text)
│   │   └── execution_status.py # ExecutionStatus model & enums (status, tab, error_message, created)
│   │
│   └── repos/                  # Persistence-layer functions (one per model/table)
│       ├── __init__.py         
│       ├── production_repo.py          # save_producao_records(): upsert logic for Producao
│       ├── processamento_repo.py       # save_processamento_records(): upsert logic for Processamento
│       ├── commercializacao_repo.py    # save_commercializacao_records(): upsert logic for Comercialização
│       ├── error_repo.py               # save_error_record(): insert into ErrorLog
│       └── execution_repo.py           # save_execution_status(): insert into ExecutionStatus
│
├── tests/                      # End-to-end & integration tests
│   ├── test_main.py            # Tests for API endpoints in app/main.py
│   ├── test_auth.py            # Auth flow tests (login, token validation)
│   └── test_captura.py         # Full ETL run tests for captura module
│
├── requirements.txt            # Pin all Python dependencies (Flask, SQLAlchemy, etc.)
├── Dockerfile                  # Container recipe: install deps, copy code, run processor/API
├── docker-compose.yml          # Compose services: db, fiap_app, (optional pgAdmin)
├── .gitignore                  # Files & folders to exclude from Git (e.g. .venv, __pycache__)
└── README.md                   # Project overview, Python version, setup & usage instructions

```

## Requisitos de Ambiente

- Python 3.9.7

> **Observação:** Este projeto foi desenvolvido e testado utilizando Python 3.9.7. Recomendamos o uso de versões da família 3.9 (por exemplo, 3.9.7 ou superiores da mesma linha) para garantir a compatibilidade. Embora versões mais recentes como 3.10 ou 3.11 possam funcionar, essas não foram testadas.



## Install the python libraries from the requirements file
```bash
pip install -r requirements.txt
```

## Run the project

```bash
python -m captura.processor 
```

Start the database:
```bash
# 1. Start everything (in detached mode):
docker-compose up -d --build

# 2. Run the processor inside the running app container:
docker-compose exec fiap_app python -m captura.processor

# 3. Check logs
docker-compose logs        # shows logs from all services
docker-compose logs app    # shows logs only from the `app` service
```