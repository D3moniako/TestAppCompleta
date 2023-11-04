from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from repository import SecurityRepository, UserManagementRepository
from jose import JWTError,jwt
from db.modelli import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class RoleMiddleware:
    def __init__(self, user_repo: SecurityRepository = Depends(UserManagementRepository)):
        self.user_repo = user_repo

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
            user = self.user_repo.get_user_by_username(request.state.db, username)
            # Verifica i ruoli per l'accesso alle rotte
            if "admin" not in user.roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have access to this resource",
                )
            return user
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
def get_current_user(token: str = Depends(SecurityRepository().verify_token)):
    return token
