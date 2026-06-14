# Zabbix → Redmine Auto Ticketing System

A Python-based middleware that automatically creates and closes Redmine tickets based on Zabbix alerts.

---

## Architecture

```
Zabbix Server
      |
      | Webhook
      v
Python Middleware (Flask) - Port 5000
      |
      | REST API
      v
Redmine (Docker) - Port 80
      |
      v
PostgreSQL (Docker)
```

---

## Requirements

- Ubuntu Server 24.04 LTS
- Docker + Docker Compose
- Python 3.x + Flask
- Zabbix 7.x
- Redmine 5.1

---

## Repository Structure

```
zabbix-redmine-integration/
├── README.md
├── docker-compose.yml
├── middleware/
│   ├── app.py
│   └── middleware.service
├── nginx/
│   └── redmine.conf
└── zabbix/
    └── webhook.js
```

---

## Server Setup

Before deploying anything, prepare the Ubuntu server:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git nano net-tools ufw

sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5000/tcp

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

---

## 1. docker-compose.yml

This file defines two containers: Redmine and PostgreSQL. They run on an isolated internal network and store data in persistent volumes so nothing is lost on restart or upgrade.

**Why PostgreSQL?**
More stable and better supported with Redmine long-term compared to MySQL or SQLite.

**Why Volumes?**
Containers are stateless by default. Volumes keep your data on disk even if the container is removed or recreated.

**Why a custom Network?**
Isolates Redmine and PostgreSQL from other containers on the server. They communicate using container names instead of IPs.

### Setup

Generate a secret key first:
```bash
openssl rand -hex 64
```

Copy the file and replace the placeholders:
- `YOUR_DB_PASSWORD` → strong password for PostgreSQL
- `YOUR_SECRET_KEY` → the value generated above

```bash
sudo mkdir -p /opt/redmine
cd /opt/redmine
cp /path/to/docker-compose.yml .
docker compose up -d
docker compose logs -f
```

---

## 2. nginx/redmine.conf

Nginx acts as a Reverse Proxy sitting in front of Redmine.

**Why Nginx?**
Redmine runs on port 3000 internally. Nginx listens on port 80 and forwards requests to Redmine. This means users access Redmine on the standard HTTP port without exposing port 3000 publicly.

### Setup

```bash
sudo apt install -y nginx
sudo cp nginx/redmine.conf /etc/nginx/sites-available/redmine
sudo ln -s /etc/nginx/sites-available/redmine /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx
```

Replace `YOUR_SERVER_IP` in the file with your actual server IP or domain name.

---

## 3. middleware/app.py

The core of the integration. A Flask web server that:

- Receives webhook events from Zabbix
- Checks if a ticket already exists for the same host and trigger (Deduplication)
- Creates a new Redmine ticket if none exists
- Closes the ticket automatically when Zabbix sends a Recovery event
- Maps Zabbix severity to Redmine priority
- Maps trigger keywords to the correct Redmine tracker

**Why a Middleware instead of direct Zabbix → Redmine?**
Direct integration is limited. The middleware gives full control over deduplication, priority mapping, tracker selection, and future features like Teams or Telegram notifications.

### Severity → Priority Mapping

| Zabbix | Redmine |
|---|---|
| Disaster | Immediate |
| High | Critical |
| Average | High |
| Warning | Normal |
| Information | Low |

### Trigger Keywords → Tracker Mapping

| Keywords | Tracker |
|---|---|
| down, unreachable, unavailable, service | Incident |
| cpu, memory, ram, load | Performance |
| disk, storage, filesystem | Storage |
| network, interface, bandwidth | Network |
| ssl, certificate, login, auth | Security |

### Setup

```bash
sudo mkdir -p /opt/middleware
sudo chown -R $USER:$USER /opt/middleware
pip3 install flask requests --break-system-packages
cp middleware/app.py /opt/middleware/
```

Edit `/opt/middleware/app.py` and replace:
- `YOUR_REDMINE_IP` → your Redmine server IP
- `YOUR_API_KEY` → API key generated from Redmine

---

## 4. middleware/middleware.service

A systemd service file that keeps the middleware running as a background service and restarts it automatically if it crashes or the server reboots.

### Setup

```bash
sudo cp middleware/middleware.service /etc/systemd/system/
```

Edit the file and replace `YOUR_USERNAME` with your Linux username, then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable middleware
sudo systemctl start middleware
sudo systemctl status middleware
```

---

## 5. zabbix/webhook.js

A JavaScript script that runs inside Zabbix when an alert fires. It formats the event data and sends it to the middleware via HTTP POST.

**Why JavaScript?**
Zabbix webhooks use a built-in JavaScript engine. The script reads the trigger parameters, determines if it's a Problem or Recovery event, and sends the data to the middleware.

### Setup in Zabbix

**Media Type:**
```
Alerts → Media types → Create media type
Name: Redmine Webhook
Type: Webhook
```

**Parameters:**

| Name | Value |
|---|---|
| event_id | {EVENT.ID} |
| event_type | {TRIGGER.STATUS} |
| host | {HOST.NAME} |
| ip | {HOST.IP} |
| severity | {EVENT.SEVERITY} |
| trigger | {TRIGGER.NAME} |
| zabbix_url | {$ZABBIX.URL} |
| event_time | {EVENT.TIME} {EVENT.DATE} |

Paste the content of `zabbix/webhook.js` into the Script field.

**User Media:**
```
Users → Admin → Media → Add
Type:        Redmine Webhook
Send to:     admin
Severities:  Disaster, High, Average, Warning
```

**Action:**
```
Alerts → Actions → Trigger actions → Create action
Name:      Redmine Ticket Action
Condition: Trigger severity >= Average

Operations:          Send message → Admin → Redmine Webhook
Recovery operations: Send message → Admin → Redmine Webhook
```

---

## Redmine Initial Configuration

After Redmine is running, configure it manually:

**Enable REST API:**
```
Administration → Settings → API → Enable REST web service
```

**Generate API Key:**
```bash
docker exec -it redmine_app bash

cat > /tmp/genkey.rb << 'EOF'
user = User.find_by_login('admin')
token = Token.new
token.user = user
token.action = 'api'
token.save
puts token.value
EOF

bundle exec rails runner /tmp/genkey.rb -e production
exit
```

**Project:**
```
Name:       Infrastructure Monitoring
Identifier: infrastructure-monitoring
Modules:    Issue tracking, Activity, Wiki
```

**Trackers:** Incident, Performance, Storage, Network, Security

**Statuses:** New, In Progress, Resolved, Feedback, Closed, Rejected

**Priorities:** Low, Normal, High, Critical, Immediate

**Custom Fields:**

| ID | Name | Format |
|---|---|---|
| 1 | Hostname | Text |
| 2 | IP Address | Text |
| 3 | Trigger Name | Text |
| 4 | Event ID | Text |
| 5 | Zabbix URL | Text |
| 6 | Recovery Time | Date |

---

## Testing

**Create a ticket:**
```bash
curl -X POST http://YOUR_MIDDLEWARE_IP:5000/webhook \
-H "Content-Type: application/json" \
-d '{
  "event_type": "problem",
  "host": "TEST-SERVER",
  "trigger": "CPU utilization is above 90%",
  "severity": "High",
  "ip": "192.168.1.100",
  "event_id": "12345",
  "zabbix_url": "http://zabbix/events/12345",
  "event_time": "2026-06-14 09:00:00"
}'
```

**Close a ticket:**
```bash
curl -X POST http://YOUR_MIDDLEWARE_IP:5000/webhook \
-H "Content-Type: application/json" \
-d '{
  "event_type": "recovery",
  "host": "TEST-SERVER",
  "trigger": "CPU utilization is above 90%",
  "event_time": "2026-06-14 09:30:00"
}'
```

---

## Monitoring

```bash
# View logs
tail -f /opt/middleware/middleware.log

# Service status
sudo systemctl status middleware

# Restart service
sudo systemctl restart middleware
```
