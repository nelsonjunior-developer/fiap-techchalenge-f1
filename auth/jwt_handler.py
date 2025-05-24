import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Configurações do JWT
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
EXPIRES_MINUTES = 30

# Bearer token extractor para uso em rotas protegidas
bearer_scheme = HTTPBearer()

def create_access_token(data: dict):
    """Cria um token JWT com tempo de expiração."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=EXPIRES_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    """Decodifica um token JWT e retorna os dados, ou None se inválido."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None

def verify_token(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    """Dependência FastAPI para proteger rotas com verificação JWT."""
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    return payload