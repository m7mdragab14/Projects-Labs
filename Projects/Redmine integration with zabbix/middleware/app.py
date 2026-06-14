import os
from flask import Flask, request, jsonify
import requests
import logging

app = Flask(__name__)

logging.basicConfig(
    filename='/opt/middleware/middleware.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

# Redmine Settings from .env
REDMINE_URL = os.environ.get("REDMINE_URL")
REDMINE_API_KEY = os.environ.get("REDMINE_API_KEY")
REDMINE_PROJECT = os.environ.get("REDMINE_PROJECT", "infrastructure-monitoring")

# Tracker IDs
TRACKER_MAP = {
    "incident": 4,
    "performance": 5,
    "storage": 6,
    "network": 7,
    "security": 8
}

# Priority Mapping
PRIORITY_MAP = {
    "Disaster": 6,
    "High": 5,
    "Average": 4,
    "Warning": 3,
    "Information": 2,
    "Not classified": 1
}

def get_tracker(trigger_name):
    trigger_name = trigger_name.lower()
    if any(x in trigger_name for x in ["down", "unreachable", "unavailable", "service"]):
        return TRACKER_MAP["incident"]
    elif any(x in trigger_name for x in ["cpu", "memory", "ram", "load"]):
        return TRACKER_MAP["performance"]
    elif any(x in trigger_name for x in ["disk", "storage", "filesystem"]):
        return TRACKER_MAP["storage"]
    elif any(x in trigger_name for x in ["network", "interface", "bandwidth"]):
        return TRACKER_MAP["network"]
    elif any(x in trigger_name for x in ["ssl", "certificate", "login", "auth"]):
        return TRACKER_MAP["security"]
    else:
        return TRACKER_MAP["incident"]

def find_existing_issue(host, trigger):
    headers = {"X-Redmine-API-Key": REDMINE_API_KEY}
    params = {
        "project_id": REDMINE_PROJECT,
        "status_id": "open",
        "subject": f"[{host}] {trigger}"
    }
    response = requests.get(
        f"{REDMINE_URL}/issues.json",
        headers=headers,
        params=params
    )
    issues = response.json().get("issues", [])
    for issue in issues:
        if issue["subject"] == f"[{host}] {trigger}":
            return issue["id"]
    return None

def create_issue(data):
    headers = {
        "X-Redmine-API-Key": REDMINE_API_KEY,
        "Content-Type": "application/json"
    }
    host = data.get("host", "Unknown")
    trigger = data.get("trigger", "Unknown")
    severity = data.get("severity", "Average")
    ip = data.get("ip", "")
    event_id = data.get("event_id", "")
    zabbix_url = data.get("zabbix_url", "")
    event_time = data.get("event_time", "")

    issue_data = {
        "issue": {
            "project_id": REDMINE_PROJECT,
            "tracker_id": get_tracker(trigger),
            "priority_id": PRIORITY_MAP.get(severity, 4),
            "subject": f"[{host}] {trigger}",
            "description": f"""
## Problem Details

| Field      | Value        |
|------------|--------------|
| Host       | {host}       |
| IP Address | {ip}         |
| Trigger    | {trigger}    |
| Severity   | {severity}   |
| Event Time | {event_time} |
| Event ID   | {event_id}   |
| Zabbix URL | {zabbix_url} |
            """,
            "custom_fields": [
                {"id": 1, "value": host},
                {"id": 2, "value": ip},
                {"id": 3, "value": trigger},
                {"id": 4, "value": event_id},
                {"id": 5, "value": zabbix_url}
            ]
        }
    }
    response = requests.post(
        f"{REDMINE_URL}/issues.json",
        headers=headers,
        json=issue_data
    )
    return response

def close_issue(issue_id, data):
    headers = {
        "X-Redmine-API-Key": REDMINE_API_KEY,
        "Content-Type": "application/json"
    }
    issue_data = {
        "issue": {
            "status_id": 5,
            "notes": f"Problem resolved automatically at {data.get('event_time', '')}"
        }
    }
    response = requests.put(
        f"{REDMINE_URL}/issues/{issue_id}.json",
        headers=headers,
        json=issue_data
    )
    return response

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    logging.info(f"Received event: {data}")

    event_type = data.get("event_type", "problem")
    host = data.get("host", "Unknown")
    trigger = data.get("trigger", "Unknown")

    if event_type == "problem":
        existing_id = find_existing_issue(host, trigger)
        if existing_id:
            logging.info(f"Issue already exists: #{existing_id}")
            return jsonify({"status": "exists", "issue_id": existing_id})

        response = create_issue(data)
        if response.status_code == 201:
            issue_id = response.json()["issue"]["id"]
            logging.info(f"Created issue: #{issue_id}")
            return jsonify({"status": "created", "issue_id": issue_id})
        else:
            logging.error(f"Failed to create issue: {response.text}")
            return jsonify({"status": "error"}), 500

    elif event_type == "recovery":
        existing_id = find_existing_issue(host, trigger)
        if existing_id:
            close_issue(existing_id, data)
            logging.info(f"Closed issue: #{existing_id}")
            return jsonify({"status": "closed", "issue_id": existing_id})
        return jsonify({"status": "not_found"})

    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
