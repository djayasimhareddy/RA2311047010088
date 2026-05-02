import requests
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logging_middleware.logger import Log

load_dotenv()

TOKEN = os.getenv("EVALUATION_BEARER_TOKEN")
BASE_URL = "http://20.207.122.201/evaluation-service"

def fetch_data(endpoint: str):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}", headers=headers, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        Log("backend", "error", "utils", f"{endpoint} fetch failed: {str(e)}")
        return {}

def optimize_schedule(budget_hours: int, vehicles: list):
    n = len(vehicles)
    dp = [[0 for _ in range(budget_hours + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        v_duration = vehicles[i-1]["Duration"]
        v_impact = vehicles[i-1]["Impact"]

        for w in range(1, budget_hours + 1):
            if v_duration <= w:
                dp[i][w] = max(dp[i-1][w], dp[i-1][w - v_duration] + v_impact)
            else:
                dp[i][w] = dp[i-1][w]

    max_impact = dp[n][budget_hours]
    w = budget_hours
    selected_tasks = []

    for i in range(n, 0, -1):
        if max_impact <= 0:
            break
        if dp[i][w] != dp[i-1][w]:
            selected_tasks.append(vehicles[i-1]["TaskID"])
            max_impact -= vehicles[i-1]["Impact"]
            w -= vehicles[i-1]["Duration"]

    return dp[n][budget_hours], selected_tasks

def main():
    Log("backend", "info", "cron_job", "Starting Scheduler")

    depots_data = fetch_data("depots")
    vehicles_data = fetch_data("vehicles")

    depots = depots_data.get("depots", [])
    vehicles = vehicles_data.get("vehicles", [])

    if not depots or not vehicles:
        Log("backend", "fatal", "controller", "Failed to load depots or vehicles")
        return

    for depot in depots:
        depot_id = depot["ID"]
        budget = depot["MechanicHours"]

        Log("backend", "info", "domain", f"Processing Depot {depot_id}")

        total_impact, scheduled_tasks = optimize_schedule(budget, vehicles)

        print("=" * 40)
        print(f"RESULTS FOR DEPOT {depot_id} (Budget: {budget})")
        print("=" * 40)
        print(f"Max Impact: {total_impact}")
        print(f"Tasks: {len(scheduled_tasks)}")
        for task in scheduled_tasks:
            print(f"- {task}")
        print("=" * 40)

        Log("backend", "info", "controller", f"Depot {depot_id} completed")

if __name__ == "__main__":
    main()