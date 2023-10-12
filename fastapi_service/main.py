import asyncio
from registrazione_service import register_service
from fastapi import FastAPI
import uvicorn
app = FastAPI()

# Rotta per il controllo dello stato di salute
@app.get("/health")
async def health():
    return {"status": "ok"}
@app.get("/fast")
async def ciao():
    return {"message": "ciao dal primo livello"}
@app.get("/fast/lv2")
async def benvenuto():
    return {"message": "ciao dal secondo livello"}
if __name__ == "__main__":
    service_name = "fastapi_service"
    service_port = 80

    loop = asyncio.get_event_loop()
    loop.run_until_complete(register_service(service_name, service_port))

    # Avvia il server Uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=service_port, reload=True)
# 