Certamente, ecco le modifiche nei file Docker Compose, Dockerfile NGINX e NGINX.conf:

1. **docker-compose.yml**

```yaml
version: '3'

services:
  fastapi_service:
    build:
      context: ./fastapi_service
    ports:
      - "8000:80"
    depends_on:
      - consul
    environment:
      - CONSUL_HTTP_ADDR=consul:8500
      - SERVICE_NAME=fastapi_service
      - SERVICE_PORT=80
    restart: "unless-stopped"
    command: ["sh", "-c", "python main.py"]
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:80/health"]
      interval: 1s
      timeout: 3s
      retries: 30

  consul:
    image: consul:1.10.3
    ports:
      - "8500:8500"
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8500/v1/status/leader"]
      interval: 1s
      timeout: 3s
      retries: 3

  nginx:
    build: ./nginx
    ports:
      - "8081:8081"
    depends_on:
      - consul
      - fastapi_service
```

2. **nginx/Dockerfile**

```Dockerfile
# nginx/Dockerfile
FROM nginx:latest

# Copia il file di configurazione di Nginx nella directory corretta
COPY nginx.conf /etc/nginx/nginx.conf

# Rimuovi la configurazione di default di Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Esponi la porta 8081
EXPOSE 8081
```

3. **nginx/nginx.conf**

```nginx
# nginx/nginx.conf
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    server {
        listen 8081;

        location / {
            proxy_pass http://fastapi_service:80;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

Ora puoi eseguire `docker-compose up --build` nella directory contenente il file `docker-compose.yml` per avviare i tuoi servizi. NGINX sarà configurato come gateway per il tuo servizio FastAPI.