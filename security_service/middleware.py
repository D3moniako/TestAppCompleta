# security_service/middleware.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .repository import SecurityRepository
from jose import JWTError, jwt
from .models_auth import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class RoleMiddleware:
    def __init__(self, security_repo: SecurityRepository = Depends(SecurityRepository)):
        self.security_repo = security_repo

    async def __call__(self, request, token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            # Verifica se il microservizio è registrato
            if not self.security_repo.is_microservice_registered(request.state.db, username):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Microservice not registered",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            user = self.security_repo.get_user_by_username(request.state.db, username)
            # Verifica i ruoli per l'accesso alle rotte
            if "admin" not in user.roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have access to this resource",
                )
            return user
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

def get_current_user(token: str = Depends(SecurityRepository().verify_token)):
    return token
