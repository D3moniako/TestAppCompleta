# user_management_service/api/roles.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from middleware import RoleMiddleware
from db.engine import get_engine,get_db

# from main  import get_session_local  # Corretto l'import per get_session_local
# Corretto l'import per get_session_local
from repository import UserManagementRepository,SecurityRepository
from db.modelli import Utente,UserRole

# Inizializza i repository e il middleware
router = APIRouter()
engine = get_engine()
# Funzione per ottenere la sessione locale

def get_session_local():
    engine = get_db()
    return Session(bind=engine)  # Cambia questa riga

user_repository = UserManagementRepository()
security_repository = SecurityRepository()  # Aggiunto l'invocazione della classe
role_middleware = RoleMiddleware
#########################CRUD RUOLI###################
###CREA RUOLI
###CREA RUOLI
@router.post("/create-role/", dependencies=[Depends(RoleMiddleware(allowed_roles=["admin"]))])
async def create_role(
    role_name: str,
    user: Utente = Depends(RoleMiddleware(allowed_roles=["admin"])),
    db: Session = Depends(get_session_local)
):
    existing_role = db.query(UserRole).filter_by(role_name=role_name).first()

    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ruolo con nome {role_name} esiste già",
        )

    new_role = user_repository.create_role(db, role_name)

    if new_role:
        return {"message": f"Nuovo ruolo {role_name} creato con successo"}

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to create role",
    )
   

###CANCELLA RUOLI 
@router.delete("/delete-role/{role_name}", dependencies=[Depends(RoleMiddleware(allowed_roles=["admin"]))])
async def delete_role(role_name: str, db: Session = Depends(get_session_local)):
    result = user_repository.delete_role(db, role_name)
    return result

### VISUALIZZA TUTTI I RUOLI
@router.get("/get-all-roles", dependencies=[Depends(RoleMiddleware(allowed_roles=["admin"]))])
async def get_all_roles(db: Session = Depends(get_session_local)):
    roles = user_repository.get_all_roles(db)
    return roles

### ASSEGNARE RUOLI
@router.post("/assign-role-with-userid/", dependencies=[Depends(RoleMiddleware(allowed_roles=["admin"]))])
async def assign_role_with_id(
    user_id: int,
    role_name: str,
    db: Session = Depends(get_session_local),
    user_repo: UserManagementRepository = Depends(UserManagementRepository)
):
    return user_repo.upload_role_to_user_by_name(db, user_id, role_name)

@router.post("/assign-role-by-username/", dependencies=[Depends(RoleMiddleware(allowed_roles=["admin"]))])
async def assign_role_by_username(
    username: str,
    role_name: str,
    db: Session = Depends(get_session_local),
    user_repo: UserManagementRepository = Depends(UserManagementRepository)
):
    user = user_repo.get_user_by_username(db, username)

    if user:
        if user.role_id:
            # Aggiorna il ruolo esistente
            user_repo.upload_role_to_user_by_name(db, user.id, role_name)
            return {"message": "Ruolo aggiornato con successo"}

        # Se l'utente non ha un ruolo, assegna il nuovo ruolo
        user_repo.upload_role_to_user_by_name(db, user.id, role_name)
        return {"message": "Ruolo assegnato con successo"}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Utente con username {username} non trovato",
    )
