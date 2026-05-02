import requests
import os
from dotenv import load_dotenv
from typing import Literal


load_dotenv()
AUTH_TOKEN = os.getenv("EVALUATION_BEARER_TOKEN")
LOG_URL = "http://20.207.122.201/evaluation-service/logs"

def Log(
    stack: Literal["backend", "frontend"],
    level: Literal["debug", "info", "warn", "error", "fatal"],
    package: Literal["cache", "controller", "cron_job", "db", "domain", "auth", "config", "middleware", "utils"],
    message: str
):

    if not AUTH_TOKEN:
        print("[FAIL] Missing AUTH_TOKEN in environment variables.")
        return None

    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "stack": stack,
        "level": level,
        "package": package,
        "message": message
    }

    try:
        response = requests.post(LOG_URL, json=payload, headers=headers, timeout=5)
        response.raise_for_status() 
        print(f"[{level.upper()}] {message}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Server Log Error: {e}")
        return None