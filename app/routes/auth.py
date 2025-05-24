from fastapi import APIRouter
from auth.schemas import LoginRequest, TokenResponse
from auth.auth_service import authenticate_user

router = APIRouter(prefix="/v1/auth", tags=["Autenticação"])

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest):
    token = authenticate_user(credentials.username, credentials.password)
    return TokenResponse(access_token=token)