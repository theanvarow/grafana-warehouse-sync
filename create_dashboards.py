import urllib.request
import json

GRAFANA_URL = "http://127.0.0.1:3000"
AUTH_HEADER = "Basic YWRtaW46YWRtaW4="

SQLITE_UID = "bfw4w68p7r5kwc"
INFINITY_UID = "efw4w3vy5a0w0d"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1vRYsfBey2qTmLf9iCkxSU4tb85e6nhYZzwaQ7DrMkII/export?format=csv&gid=1220218080"

# 1. SQLite Warehouse Dashboard
dashboard_sqlite = {
    "dashboard": {
        "id": None,
        "uid": "warehouse_sqlite_dash",
        "title": "Складской Учет - Google Sheets (SQLite Data)",
        "tags": ["warehouse", "google-sheets", "sqlite"],
        "timezone": "browser",
        "refresh": "10s",
        "schemaVersion": 39,
        "version": 1,
        "panels": [
            # Row 1: KPI Stats
            {
                "id": 1,
                "title": "Всего позиций",
                "type": "stat",
                "gridPos": {"h": 4, "w": 4, "x": 0, "y": 0},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [
                    {
                        "refId": "A",
                        "queryText": "SELECT count(*) as total FROM inventory;",
                        "rawQueryText": "SELECT count(*) as total FROM inventory;"
                    }
                ],
                "options": {
                    "reduceOptions": {"values": False, "calcs": ["lastNotNull"], "fields": ""},
                    "colorMode": "value",
                    "graphMode": "none"
                },
                "fieldConfig": {
                    "defaults": {"color": {"mode": "thresholds"}, "thresholds": {"mode": "absolute", "steps": [{"color": "blue", "value": None}]}}
                }
            },
            {
                "id": 2,
                "title": "Общее количество (шт)",
                "type": "stat",
                "gridPos": {"h": 4, "w": 5, "x": 4, "y": 0},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [
                    {
                        "refId": "A",
                        "queryText": "SELECT sum(quantity) as total_qty FROM inventory;",
                        "rawQueryText": "SELECT sum(quantity) as total_qty FROM inventory;"
                    }
                ],
                "options": {
                    "reduceOptions": {"values": False, "calcs": ["lastNotNull"], "fields": ""},
                    "colorMode": "value",
                    "graphMode": "none"
                },
                "fieldConfig": {
                    "defaults": {"color": {"mode": "thresholds"}, "thresholds": {"mode": "absolute", "steps": [{"color": "purple", "value": None}]}}
                }
            },
            {
                "id": 3,
                "title": "Подтверждено",
                "type": "stat",
                "gridPos": {"h": 4, "w": 5, "x": 9, "y": 0},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [
                    {
                        "refId": "A",
                        "queryText": "SELECT count(*) as count FROM inventory WHERE status = 'Подтвержден';",
                        "rawQueryText": "SELECT count(*) as count FROM inventory WHERE status = 'Подтвержден';"
                    }
                ],
                "options": {
                    "reduceOptions": {"values": False, "calcs": ["lastNotNull"], "fields": ""},
                    "colorMode": "value",
                    "graphMode": "none"
                },
                "fieldConfig": {
                    "defaults": {"color": {"mode": "thresholds"}, "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}]}}
                }
            },
            {
                "id": 4,
                "title": "Отсутствует",
                "type": "stat",
                "gridPos": {"h": 4, "w": 5, "x": 14, "y": 0},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [
                    {
                        "refId": "A",
                        "queryText": "SELECT count(*) as count FROM inventory WHERE status = 'Отсутствует';",
                        "rawQueryText": "SELECT count(*) as count FROM inventory WHERE status = 'Отсутствует';"
                    }
                ],
                "options": {
                    "reduceOptions": {"values": False, "calcs": ["lastNotNull"], "fields": ""},
                    "colorMode": "value",
                    "graphMode": "none"
                },
                "fieldConfig": {
                    "defaults": {"color": {"mode": "thresholds"}, "thresholds": {"mode": "absolute", "steps": [{"color": "red", "value": None}]}}
                }
            },
            {
                "id": 5,
                "title": "Неверно размещено",
                "type": "stat",
                "gridPos": {"h": 4, "w": 5, "x": 19, "y": 0},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [
                    {
                        "refId": "A",
                        "queryText": "SELECT count(*) as count FROM inventory WHERE is_correct_placement = 'Нет';",
                        "rawQueryText": "SELECT count(*) as count FROM inventory WHERE is_correct_placement = 'Нет';"
                    }
                ],
                "options": {
                    "reduceOptions": {"values": False, "calcs": ["lastNotNull"], "fields": ""},
                    "colorMode": "value",
                    "graphMode": "none"
                },
                "fieldConfig": {
                    "defaults": {"color": {"mode": "thresholds"}, "thresholds": {"mode": "absolute", "steps": [{"color": "orange", "value": None}]}}
                }
            },

            # Row 2: Charts
            {
                "id": 6,
                "title": "Статусы размещения",
                "type": "piechart",
                "gridPos": {"h": 8, "w": 8, "x": 0, "y": 4},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [
                    {
                        "refId": "A",
                        "queryText": "SELECT status, count(*) as count FROM inventory GROUP BY status;",
                        "rawQueryText": "SELECT status, count(*) as count FROM inventory GROUP BY status;"
                    }
                ],
                "options": {
                    "pieType": "donut",
                    "reduceOptions": {"values": True},
                    "legend": {"displayMode": "list", "placement": "right"}
                }
            },
            {
                "id": 7,
                "title": "Топовые категории товаров",
                "type": "piechart",
                "gridPos": {"h": 8, "w": 8, "x": 8, "y": 4},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [
                    {
                        "refId": "A",
                        "queryText": "SELECT category, count(*) as count FROM inventory GROUP BY category ORDER BY count DESC LIMIT 8;",
                        "rawQueryText": "SELECT category, count(*) as count FROM inventory GROUP BY category ORDER BY count DESC LIMIT 8;"
                    }
                ],
                "options": {
                    "pieType": "pie",
                    "reduceOptions": {"values": True},
                    "legend": {"displayMode": "list", "placement": "right"}
                }
            },
            {
                "id": 8,
                "title": "Рабочая нагрузка по сотрудникам (ФИО)",
                "type": "barchart",
                "gridPos": {"h": 8, "w": 8, "x": 16, "y": 4},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [
                    {
                        "refId": "A",
                        "queryText": "SELECT employee as 'ФИО', count(*) as 'Количество операций' FROM inventory WHERE employee != '' GROUP BY employee ORDER BY count(*) DESC;",
                        "rawQueryText": "SELECT employee as 'ФИО', count(*) as 'Количество операций' FROM inventory WHERE employee != '' GROUP BY employee ORDER BY count(*) DESC;"
                    }
                ],
                "options": {
                    "orientation": "horizontal",
                    "legend": {"displayMode": "hidden"}
                }
            },

            # Row 3: Data Table
            {
                "id": 9,
                "title": "Таблица размещения товаров в ячейках (Google Sheet Live)",
                "type": "table",
                "gridPos": {"h": 12, "w": 24, "x": 0, "y": 12},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [
                    {
                        "refId": "A",
                        "queryText": "SELECT barcode as 'ШК товара', cell as 'Ячейка', category as 'Категория', description as 'Описание', quantity as 'Количество', status as 'Статус', is_correct_placement as 'Размещён правильно', employee as 'ФИО', shift as 'Смена', created_at as 'Дата', product_id FROM inventory ORDER BY id ASC;",
                        "rawQueryText": "SELECT barcode as 'ШК товара', cell as 'Ячейка', category as 'Категория', description as 'Описание', quantity as 'Количество', status as 'Статус', is_correct_placement as 'Размещён правильно', employee as 'ФИО', shift as 'Смена', created_at as 'Дата', product_id FROM inventory ORDER BY id ASC;"
                    }
                ],
                "options": {
                    "footer": {"show": True, "enablePagination": True}
                }
            }
        ]
    },
    "overwrite": True
}

# 2. Direct Infinity Google Sheets Dashboard
dashboard_infinity = {
    "dashboard": {
        "id": None,
        "uid": "warehouse_infinity_dash",
        "title": "Складской Учет - Google Sheets (Прямое подключение CSV)",
        "tags": ["warehouse", "google-sheets", "infinity"],
        "timezone": "browser",
        "refresh": "1m",
        "schemaVersion": 39,
        "version": 1,
        "panels": [
            {
                "id": 1,
                "title": "Полная таблица данных Google Sheets",
                "type": "table",
                "gridPos": {"h": 20, "w": 24, "x": 0, "y": 0},
                "datasource": {"type": "yesoreyeram-infinity-datasource", "uid": INFINITY_UID},
                "targets": [
                    {
                        "refId": "A",
                        "type": "csv",
                        "source": "url",
                        "url": SHEET_CSV_URL,
                        "format": "table"
                    }
                ],
                "options": {
                    "footer": {"show": True, "enablePagination": True}
                }
            }
        ]
    },
    "overwrite": True
}

def import_dashboards():
    for dash in [dashboard_sqlite, dashboard_infinity]:
        req = urllib.request.Request(
            f"{GRAFANA_URL}/api/dashboards/db",
            data=json.dumps(dash).encode('utf-8'),
            headers={"Content-Type": "application/json", "Authorization": AUTH_HEADER}
        )
        try:
            resp = urllib.request.urlopen(req)
            res = json.loads(resp.read().decode('utf-8'))
            print(f"Dashboard '{dash['dashboard']['title']}' imported successfully! URL: {GRAFANA_URL}{res.get('url')}")
        except Exception as e:
            print(f"Error importing dashboard: {e}")

if __name__ == "__main__":
    import_dashboards()
