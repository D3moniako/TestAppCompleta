# Architettura del Progetto

## Panoramica

Il progetto è una complessa architettura di microservizi sviluppata in FastAPI (Python 3.9), con la gestione delle librerie affidata a Poetry e il deployment orchestrato attraverso Docker. L'intera infrastruttura è basata su un approccio event-driven con Kafka per la gestione degli eventi, e il registro dei microservizi è effettuato tramite Eureka e Consul.

## Struttura del Progetto

La struttura del progetto è organizzata gerarchicamente:

### Directory Principale (`project_root/`)

- **docker-compose.yml**: Il file di configurazione principale per Docker Compose, che orchestrerà l'intero sistema.

### Servizio di Autenticazione (`authentication_service/`)

- **main.py**: Punto di ingresso principale del microservizio di autenticazione.
- **models.py**: Definizione dei modelli dati utilizzati nel microservizio.
- **repository.py**: Gestione delle operazioni sul database, in particolare l'interazione con SQLModel e SQL Alchemy.
- **decorators.py**: Contiene decoratori personalizzati per l'applicazione FastAPI.
- **Dockerfile**: Configurazione per la creazione dell'immagine Docker del servizio di autenticazione.
- **docker-compose.yml.template**: Modello per la configurazione specifica di Docker Compose.
- **requirements.txt**: Elenco delle dipendenze necessarie al microservizio.
- **app/**: Package che contiene il modulo principale dell'applicazione.
- **scripts/**: Contiene script utili, tra cui costanti e generazione di Docker Compose.

### Altri Microservizi (`microservizi/`)

- **microservizio/**, **product_microservice/**, ecc.: Ogni microservizio segue una struttura simile a quella del servizio di autenticazione.

### Infrastruttura (`kafka/`, `eureka/`)

- **kafka/**: Contiene il Docker Compose per configurare l'ambiente Kafka.
- **eureka/**: Configurazione di Eureka, un sistema di registrazione dei microservizi.
  
### Script e Utility (`scripts/`)

- **constants/**: Contiene file Python con costanti specifiche per i vari microservizi.
- **generate_all_docker_compose.bat**: Script per generare tutti i file Docker Compose.
- **run_all_bat_scripts.bat**: Bat file per eseguire tutti gli script di ogni microservizio.

- **run_all_microservices.bat**: Bat file per avviare tutti i microservizi.

## Gestione delle Dipendenze

La gestione delle librerie comuni è centralizzata in uno script esterno che rileva le dipendenze condivise tra i vari microservizi, garantendo che vengano caricate una sola volta.

## Docker Compose Dinamico

Gli script esterni personalizzano i file Docker Compose, sostituendo i segnaposto con le costanti Python specifiche di ogni microservizio. Questa procedura include la gestione delle dipendenze e l'integrazione di ruoli e autenticazione.

## Middleware di Autenticazione

Il microservizio di autenticazione svolge un ruolo cruciale nella creazione di JWT e gestisce i ruoli attraverso un gateway dedicato. Il middleware verifica l'autenticità delle richieste, estrae il nome utente e controlla i ruoli prima di consentire l'accesso.

## Registrazione e Comunicazione tra Microservizi

- **register_microservice()**: Funzione per registrare nuovi microservizi durante l'avvio.
- L'uso di Eureka e Consul per la registrazione e la gestione dinamica dei microservizi.
- Un gateway garantisce che solo i microservizi registrati possano comunicare tra loro, impedendo la registrazione di servizi esterni.

## Sfide e Tecnologie Chiave

- Implementazione di un'architettura event-driven con Kafka.
- Chiara separazione delle responsabilità tra model, DTO, repository ed endpoint.
- Uso di SQLModel e SQL Alchemy per le operazioni sul database.
- Validazione dei dati con Pydantic e implementazione del typing delle variabili e paginazione .
-Gestione delle rotte  


Questa struttura ben organizzata e le tecnologie utilizzate offrono un sistema scalabile e gestibile, facilitando il deployment e la manutenzione dei microservizi.