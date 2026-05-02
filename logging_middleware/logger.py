import requests
import os
from dotenv import load_dotenv
from typing import Literal

load_dotenv()

AUTH_TOKEN = os.getenv("EVALUATION_BEARER_TOKEN")
LOG_URL = "http://20.207.122.201/evaluation-service/logs"

VALID_STACK = {"backend", "frontend"}
VALID_LEVEL = {"debug", "info", "warn", "error", "fatal"}
VALID_PACKAGE = {
    "cache", "controller", "cron_job", "db", "domain",
    "auth", "config", "middleware", "utils"
}

def Log(
    stack: Literal["backend", "frontend"],
    level: Literal["debug", "info", "warn", "error", "fatal"],
    package: Literal["cache", "controller", "cron_job", "db", "domain", "auth", "config", "middleware", "utils"],
    message: str
):

    if not AUTH_TOKEN:
        print("[FAIL] Missing AUTH_TOKEN")
        return None

    if stack not in VALID_STACK or level not in VALID_LEVEL or package not in VALID_PACKAGE:
        print("[FAIL] Invalid log input")
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
        print("STATUS:", getattr(e.response, "status_code", None))
        print("RESPONSE:", getattr(e.response, "text", None))
        print("ERROR:", str(e))
        return None