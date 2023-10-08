
### Security Service

#### Struttura del Progetto
```
security_service/
|-- models_auth.py
|-- repository_auth.py
|-- middleware.py
|-- authentication_service.py
|-- database.py
|-- main.py
```

#### Descrizione
Il microservizio `security_service` è progettato per gestire la sicurezza, inclusa la registrazione dei microservizi. Ecco una breve descrizione dei componenti principali:

1. **`models_auth.py`**
   - Contiene le definizioni dei modelli di dati utilizzati dal microservizio di sicurezza, come `UserAuth` e `TokenData`.

2. **`repository_auth.py`**
   - Contiene la logica di accesso al database e le operazioni CRUD, inclusa la gestione dei microservizi registrati.

3. **`authentication_service.py`**
   - Contiene gli endpoint e la logica di gestione dell'autenticazione degli utenti, ad esempio, la registrazione dei microservizi.

4. **`middleware.py`**
   - Contiene il middleware per gestire i ruoli e l'accesso alle risorse protette, se necessario.

5. **`database.py`**
   - Contiene la configurazione del database.

6. **`main.py`**
   - Punto di ingresso dell'applicazione che assembla tutti i componenti.

#### Utilizzo
Per registrare un nuovo microservizio, è possibile fare una richiesta POST a `/register_microservice` fornendo i dettagli del microservizio. L'autenticazione è gestita utilizzando un token JWT.

---
### Microservizio `security_service`

#### Panoramica
Il microservizio `security_service` si concentra sulla sicurezza e l'autenticazione. Gestisce le operazioni legate alla verifica dei token JWT e fornisce un endpoint sicuro. Utilizza FastAPI, SQLModel e SQL Alchemy. Fa parte dell'architettura di microservizi con Kafka e Eureka.

#### Struttura del Progetto
- **`models_auth.py`**: Definizione dei modelli dati, come `TokenData`.
- **`repository_auth.py`**: Logica di accesso al database e operazioni CRUD.
- **`middleware.py`**: Middleware per verificare la presenza di un token valido durante le richieste sicure.
- **`authentication_service.py`**: Endpoint sicuro che richiede un token valido.
- **`database.py`**: Configurazione del database.
- **`main.py`**: Punto di ingresso dell'applicazione.

#### API Principali
- **Verifica Token JWT**:
  - **Endpoint**: `GET /secure-endpoint/`
  - **Descrizione**: Un endpoint sicuro che richiede un token JWT valido. Utilizza il middleware per la verifica.

#### Middleware e Sicurezza
- Middleware per la verifica del token JWT durante le richieste sicure.
- Gestione di potenziali problemi di sicurezza, come token scaduti o non validi.

#### Sfide e Tecnologie Chiave
- Implementazione di un sistema sicuro di gestione dei token JWT.
- Utilizzo di middleware per l'autenticazione nelle richieste sicure.
- Integrato con l'architettura generale dei microservizi per una gestione coesa della sicurezza.


