from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configura i middleware CORS per consentire le richieste da qualsiasi origine
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configura il routing per i tuoi microservizi
@app.get("/user/{path:path}")
def route_to_user_service(path: str):
    # Implementa la logica per instradare la richiesta al servizio user_management
    return("ciao dal gateway di souhail")

# Aggiungi altri endpoint per gli altri microservizi

if __name__ == "__main__":
    import uvicorn

    # Avvia il tuo gateway su http://localhost:8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
