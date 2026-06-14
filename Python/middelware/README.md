## app.py - What it does

This is the brain of the integration. It sits between Zabbix and Redmine and handles three things:

---

### 1. Receives alerts from Zabbix
When any trigger fires in Zabbix, Zabbix sends the event details to this script via HTTP POST. The data includes the host name, IP, trigger name, severity, and whether it's a new problem or a recovery.

---

### 2. Decides what to do
Before creating anything, it checks if a ticket already exists for the same host and trigger. This prevents flooding Redmine with duplicate tickets when Zabbix keeps firing the same alert.

- If a ticket already exists → do nothing
- If no ticket exists → create one
- If it's a recovery event → close the existing ticket

---

### 3. Creates or closes tickets in Redmine
When creating a ticket it automatically:
- Picks the right **Tracker** based on keywords in the trigger name (CPU → Performance, Disk → Storage, etc.)
- Sets the correct **Priority** based on Zabbix severity (Disaster → Immediate, High → Critical, etc.)
- Fills in all the details (hostname, IP, trigger, event time, link to Zabbix)

When closing a ticket it adds a comment with the exact time the problem was resolved.
