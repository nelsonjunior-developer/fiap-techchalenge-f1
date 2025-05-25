# create_tables.py
from database.db import Base, engine
import database.models.producao
import database.models.processamento
import database.models.comercializacao
import database.models.importacao
import database.models.exportacao
import database.models.execution_status
import database.models.error_log

print("🔧 Criando tabelas no banco de dados remoto...")
Base.metadata.create_all(bind=engine)
print("✅ Tabelas criadas com sucesso.")