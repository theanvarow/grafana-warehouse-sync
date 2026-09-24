import urllib.request
import json
import os

BASE_DIR = "/Users/this/Desktop/Graffana conect with table"
JSON_OUT = os.path.join(BASE_DIR, "pinkbegonia989_izlishka_dashboard.json")

# Export Dashboard JSON ready for Grafana Cloud Import
GRAFANA_URL = "http://127.0.0.1:3000"
AUTH_HEADER = "Basic YWRtaW46YWRtaW4="

req = urllib.request.Request(
    f"{GRAFANA_URL}/api/dashboards/uid/izlishka_employee_svod",
    headers={"Authorization": AUTH_HEADER}
)

with urllib.request.urlopen(req) as resp:
    dash_data = json.loads(resp.read().decode('utf-8'))

dashboard_json = dash_data.get("dashboard", {})
# Set ID to None for clean import into Grafana Cloud
dashboard_json["id"] = None
dashboard_json["title"] = "Излишка — Сводный отчет (Grafana Cloud)"

# Clean export structure
export_payload = {
    "dashboard": dashboard_json,
    "overwrite": True
}

with open(JSON_OUT, "w", encoding="utf-8") as f:
    json.dump(dashboard_json, f, indent=2, ensure_ascii=False)

print(f"Exported clean dashboard JSON to: {JSON_OUT}")
