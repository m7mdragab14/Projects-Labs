# Zabbix → Redmine Integration
## Auto Ticketing System

---

## Architecture

```
Zabbix Server
     |
     | Webhook
     v
Python Middleware (Flask)
     |
     | REST API
     v
Redmine (Docker)
     |
PostgreSQL (Docker)
```

---

## Requirements 

- Ubuntu Server 24.04 LTS
- Docker + Docker Compose
- Python 3.x
- Zabbix Server
- Redmine 5.1

---

## Step-01: Install Ubuntu Server

### Hyper-V VM Setting 

| Setting |
|---|---|
| CPU | 4 vCPU |
| RAM | 8 GB |
| Storage | 100 GB |
| Generation | Generation 2 |
| Secure Boot | Disabled |


## Step-02: Server setup


# Update and upgrade the system
- sudo apt update && sudo apt upgrade -y



# Firewall Configuration
- sudo ufw enable
- sudo ufw allow 22/tcp
- sudo ufw allow 80/tcp
- sudo ufw allow 443/tcp

# Install Docker
- curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

- echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

- sudo apt update
- sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

- sudo systemctl Status docker

- sudo usermod -aG docker $USER

---

## Step-03: Install redmine on docker

- sudo mkdir -p /opt/redmine
- cd /opt/redmine


### docker-compose.yml


services:
  postgres:
    image: postgres:16
    container_name: redmine_postgres
    restart: always
    environment:
      POSTGRES_DB: redmine
      POSTGRES_USER: redmine
      POSTGRES_PASSWORD: StrongPassword123!
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - redmine_network

  redmine:
    image: redmine:5.1
    container_name: redmine_app
    restart: always
    depends_on:
      - postgres
    environment:
      REDMINE_DB_POSTGRES: postgres
      REDMINE_DB_DATABASE: redmine
      REDMINE_DB_USERNAME: redmine
      REDMINE_DB_PASSWORD: StrongPassword123!
      REDMINE_SECRET_KEY_BASE: supersecretkey123changethis
    volumes:
      - redmine_files:/usr/src/redmine/files
      - redmine_plugins:/usr/src/redmine/plugins
      - redmine_themes:/usr/src/redmine/public/themes
    ports:
      - "3000:3000"
    networks:
      - redmine_network

volumes:
  postgres_data:
  redmine_files:
  redmine_plugins:
  redmine_themes:

networks:
  redmine_network:
    driver: bridge



# Start redmine
- docker compose up -d
