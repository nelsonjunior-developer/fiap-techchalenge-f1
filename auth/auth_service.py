from fastapi import HTTPException
from auth.jwt_handler import create_access_token
from database.auth_users import users_db  # pode ser um dicionário com {username: password}

def authenticate_user(username: str, password: str):
    if username in users_db and users_db[username] == password:
        return create_access_token({"sub": username})
    raise HTTPException(status_code=401, detail="Credenciais inválidas")