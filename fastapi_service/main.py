import asyncio
from fastapi import FastAPI, HTTPException, Form
import uvicorn
import json
import requests
from registrazione_service import register_service

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

@app.post("/submit_comment")
async def submit_comment(username: str = Form(...), product_id: str = Form(...), comment: str = Form(...)):
    # Esegui le operazioni necessarie per elaborare il commento
    event_data = {"event_type": "comment_submitted", "username": username, "product_id": product_id, "comment": comment}
    
    # Invia l'evento al microservizio principale (user_management_service) utilizzando il nome del servizio
    response = requests.post("http://user_management_service/handle_comment_submission", json=event_data)
    
    if response.status_code == 200:
        return {"message": "Comment submitted successfully"}
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to submit comment")

if __name__ == "__main__":
    service_name = "fastapi_service"
    service_port = 80

    loop = asyncio.get_event_loop()
    loop.run_until_complete(register_service(service_name, service_port))

    # Avvia il server Uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=service_port, reload=True)
