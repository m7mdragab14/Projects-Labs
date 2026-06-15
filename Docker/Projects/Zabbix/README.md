# Zabbix on Docker

Deploy Zabbix using Docker Compose with PostgreSQL as the database.

---

## Architecture

```
Browser
   |
   | Port 80
   v
Zabbix Web (Nginx)
   |
   v
Zabbix Server
   |
   v
PostgreSQL
```

---

## Stack

| Component | Image | Role |
|---|---|---|
| Zabbix Server | zabbix/zabbix-server-pgsql:7.4-ubuntu-latest | Core monitoring engine |
| Zabbix Web | zabbix/zabbix-web-nginx-pgsql:7.4-ubuntu-latest | Web interface |
| PostgreSQL | postgres:16 | Database |

---

## Requirements

- Ubuntu Server 24.04 LTS
- Docker + Docker Compose
- Minimum 4 vCPU, 8GB RAM, 100GB Storage

---

## Step 1: Server Setup

Install Docker and required tools:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git nano net-tools ufw

sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 10051/tcp

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker
```

---

## Step 2: Deploy Zabbix

```bash
sudo mkdir -p /opt/zabbix
cd /opt/zabbix
cp docker-compose.yml .
cp .env.example .env
```

Edit `.env` and replace the password:

```env
POSTGRES_PASSWORD=YOUR_STRONG_PASSWORD
```

Start the containers:

```bash
docker compose up -d
```

Check that everything is running:

```bash
docker compose ps
```

You should see three containers all with status `Up`:

```
zabbix_postgres   Up
zabbix_server     Up
zabbix_web        Up
```

---

## Step 3: Access Zabbix

Open your browser and go to:

```
http://YOUR_SERVER_IP
```

Login with:

```
Username: Admin
Password: zabbix
```

Change the default password immediately after first login.

---

## Step 4: Post-Install Configuration

### Set Zabbix URL Macro

This is required for alert notifications to include a working link back to Zabbix.

```
Administration → Macros
```

Add:

```
Macro: {$ZABBIX.URL}
Value: http://YOUR_SERVER_IP
```

### Set Timezone

```
Administration → General → GUI
```

Set:

```
Default timezone: YOUR_TIMEZONE
```

---

## Monitoring

```bash
# View logs
docker compose logs -f

# Restart all containers
docker compose restart

# Stop all containers
docker compose down

# Start all containers
docker compose up -d
```

---

## Ports

| Port | Purpose |
|---|---|
| 80 | Zabbix Web Interface |
| 10051 | Zabbix Server (Agents connect here) |

---

## Notes

- Never commit `.env` to GitHub, it contains your database password
- Port 10051 must be reachable by all Zabbix Agents on your network
- Replace `YOUR_SERVER_IP` with your actual server IP or domain name
- Replace `Africa/Cairo` in `docker-compose.yml` with your actual timezone if different

---

## Repository Structure

```
zabbix-docker/
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```
