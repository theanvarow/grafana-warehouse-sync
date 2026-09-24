import urllib.request
import json

GRAFANA_URL = "http://127.0.0.1:3000"
AUTH_HEADER = "Basic YWRtaW46YWRtaW4="
SQLITE_UID = "bfw4w68p7r5kwc"

LATEST_DAY_SQL = "(SELECT max(substr(created_at, 1, 10)) FROM izlishka WHERE created_at != '')"

dashboard_izlishka = {
    "dashboard": {
        "id": None,
        "uid": "izlishka_employee_svod",
        "title": "Излишка — Сводный отчет по сотрудникам и по дням",
        "tags": ["izlishka", "employees", "summary", "warehouse", "daily"],
        "timezone": "browser",
        "refresh": "10s",
        "schemaVersion": 39,
        "version": 30,
        "panels": [
            # Row 1: KPI Stats (Кунлик Статистика за последний день)
            {
                "id": 1,
                "title": "Собрано SKU (За день)",
                "type": "stat",
                "gridPos": {"h": 4, "w": 4, "x": 0, "y": 0},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": f"SELECT count(DISTINCT CASE WHEN status IN ('Собрано', 'Подтвержден') THEN barcode END) as value FROM izlishka WHERE substr(created_at, 1, 10) = {LATEST_DAY_SQL};",
                    "rawQueryText": f"SELECT count(DISTINCT CASE WHEN status IN ('Собрано', 'Подтвержден') THEN barcode END) as value FROM izlishka WHERE substr(created_at, 1, 10) = {LATEST_DAY_SQL};"
                }],
                "options": {
                    "reduceOptions": {"values": False, "calcs": ["lastNotNull"]},
                    "colorMode": "value", "graphMode": "none"
                },
                "fieldConfig": {
                    "defaults": {"color": {"mode": "thresholds"}, "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}]}}
                }
            },
            {
                "id": 2,
                "title": "Собрано Кол-во (шт) (За день)",
                "type": "stat",
                "gridPos": {"h": 4, "w": 4, "x": 4, "y": 0},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": f"SELECT sum(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN quantity ELSE 0 END) as value FROM izlishka WHERE substr(created_at, 1, 10) = {LATEST_DAY_SQL};",
                    "rawQueryText": f"SELECT sum(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN quantity ELSE 0 END) as value FROM izlishka WHERE substr(created_at, 1, 10) = {LATEST_DAY_SQL};"
                }],
                "options": {
                    "reduceOptions": {"values": False, "calcs": ["lastNotNull"]},
                    "colorMode": "value", "graphMode": "none"
                },
                "fieldConfig": {
                    "defaults": {"color": {"mode": "thresholds"}, "thresholds": {"mode": "absolute", "steps": [{"color": "purple", "value": None}]}}
                }
            },
            {
                "id": 3,
                "title": "Отсутствует SKU (За день)",
                "type": "stat",
                "gridPos": {"h": 4, "w": 4, "x": 8, "y": 0},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": f"SELECT count(DISTINCT CASE WHEN status = 'Отсутствует' THEN barcode END) as value FROM izlishka WHERE substr(created_at, 1, 10) = {LATEST_DAY_SQL};",
                    "rawQueryText": f"SELECT count(DISTINCT CASE WHEN status = 'Отсутствует' THEN barcode END) as value FROM izlishka WHERE substr(created_at, 1, 10) = {LATEST_DAY_SQL};"
                }],
                "options": {
                    "reduceOptions": {"values": False, "calcs": ["lastNotNull"]},
                    "colorMode": "value", "graphMode": "none"
                },
                "fieldConfig": {
                    "defaults": {"color": {"mode": "thresholds"}, "thresholds": {"mode": "absolute", "steps": [{"color": "red", "value": None}]}}
                }
            },
            {
                "id": 4,
                "title": "Отсутствует Кол-во (шт) (За день)",
                "type": "stat",
                "gridPos": {"h": 4, "w": 4, "x": 12, "y": 0},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": f"SELECT sum(CASE WHEN status = 'Отсутствует' THEN quantity ELSE 0 END) as value FROM izlishka WHERE substr(created_at, 1, 10) = {LATEST_DAY_SQL};",
                    "rawQueryText": f"SELECT sum(CASE WHEN status = 'Отсутствует' THEN quantity ELSE 0 END) as value FROM izlishka WHERE substr(created_at, 1, 10) = {LATEST_DAY_SQL};"
                }],
                "options": {
                    "reduceOptions": {"values": False, "calcs": ["lastNotNull"]},
                    "colorMode": "value", "graphMode": "none"
                },
                "fieldConfig": {
                    "defaults": {"color": {"mode": "thresholds"}, "thresholds": {"mode": "absolute", "steps": [{"color": "orange", "value": None}]}}
                }
            },
            {
                "id": 5,
                "title": "Всего SKU (За день)",
                "type": "stat",
                "gridPos": {"h": 4, "w": 4, "x": 16, "y": 0},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": f"SELECT count(DISTINCT barcode) as value FROM izlishka WHERE substr(created_at, 1, 10) = {LATEST_DAY_SQL};",
                    "rawQueryText": f"SELECT count(DISTINCT barcode) as value FROM izlishka WHERE substr(created_at, 1, 10) = {LATEST_DAY_SQL};"
                }],
                "options": {
                    "reduceOptions": {"values": False, "calcs": ["lastNotNull"]},
                    "colorMode": "value", "graphMode": "none"
                },
                "fieldConfig": {
                    "defaults": {"color": {"mode": "thresholds"}, "thresholds": {"mode": "absolute", "steps": [{"color": "blue", "value": None}]}}
                }
            },
            {
                "id": 12,
                "title": "Всего Кол-во (шт) (За день)",
                "type": "stat",
                "gridPos": {"h": 4, "w": 4, "x": 20, "y": 0},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": f"SELECT sum(quantity) as value FROM izlishka WHERE substr(created_at, 1, 10) = {LATEST_DAY_SQL};",
                    "rawQueryText": f"SELECT sum(quantity) as value FROM izlishka WHERE substr(created_at, 1, 10) = {LATEST_DAY_SQL};"
                }],
                "options": {
                    "reduceOptions": {"values": False, "calcs": ["lastNotNull"]},
                    "colorMode": "value", "graphMode": "none"
                },
                "fieldConfig": {
                    "defaults": {"color": {"mode": "thresholds"}, "thresholds": {"mode": "absolute", "steps": [{"color": "teal", "value": None}]}}
                }
            },

            # Row 2: Daily Per Employee Summary Table
            {
                "id": 11,
                "title": "Ежедневный свод выработки по каждому сотруднику (Дата, ФИО, Собрано vs Отсутствует)",
                "type": "table",
                "gridPos": {"h": 12, "w": 24, "x": 0, "y": 4},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": "SELECT date_day as 'Дата', employee as 'ФИО сотрудника', confirmed_skus as 'Собрано SKU', confirmed_qty as 'Собрано Кол-во (шт)', missing_skus as 'Отсутствует SKU', missing_qty as 'Отсутствует Кол-во (шт)', total_skus as 'Всего SKU', total_qty as 'Всего Кол-во (шт)', total_ops as 'Всего операций' FROM izlishka_daily_employee_summary ORDER BY date_day DESC, total_qty DESC;",
                    "rawQueryText": "SELECT date_day as 'Дата', employee as 'ФИО сотрудника', confirmed_skus as 'Собрано SKU', confirmed_qty as 'Собрано Кол-во (шт)', missing_skus as 'Отсутствует SKU', missing_qty as 'Отсутствует Кол-во (шт)', total_skus as 'Всего SKU', total_qty as 'Всего Кол-во (шт)', total_ops as 'Всего операций' FROM izlishka_daily_employee_summary ORDER BY date_day DESC, total_qty DESC;"
                }],
                "options": {
                    "footer": {"show": True, "enablePagination": True}
                }
            },

            # Row 3: Daily Summary Table (Ежедневный общий свод)
            {
                "id": 10,
                "title": "Ежедневный общий свод по дням (Дата, Собрано vs Отсутствует)",
                "type": "table",
                "gridPos": {"h": 10, "w": 24, "x": 0, "y": 16},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": "SELECT date_day as 'Дата', confirmed_skus as 'Собрано SKU', confirmed_qty as 'Собрано Кол-во (шт)', missing_skus as 'Отсутствует SKU', missing_qty as 'Отсутствует Кол-во (шт)', total_skus as 'Всего SKU', total_qty as 'Всего Кол-во (шт)', total_ops as 'Всего операций' FROM izlishka_daily_summary ORDER BY date_day DESC;",
                    "rawQueryText": "SELECT date_day as 'Дата', confirmed_skus as 'Собрано SKU', confirmed_qty as 'Собрано Кол-во (шт)', missing_skus as 'Отсутствует SKU', missing_qty as 'Отсутствует Кол-во (шт)', total_skus as 'Всего SKU', total_qty as 'Всего Кол-во (шт)', total_ops as 'Всего операций' FROM izlishka_daily_summary ORDER BY date_day DESC;"
                }],
                "options": {
                    "footer": {"show": True, "enablePagination": False}
                }
            },

            # Row 4: Bar Gauges / Visual Charts (Fully compatible & rendered in Grafana)
            {
                "id": 6,
                "title": "Динамика операций по дням",
                "type": "bargauge",
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 26},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": "SELECT date_day as 'Дата', total_ops as 'Количество операций' FROM izlishka_daily_summary ORDER BY date_day ASC;",
                    "rawQueryText": "SELECT date_day as 'Дата', total_ops as 'Количество операций' FROM izlishka_daily_summary ORDER BY date_day ASC;"
                }],
                "options": {
                    "orientation": "vertical",
                    "displayMode": "gradient",
                    "showUnfilled": True,
                    "reduceOptions": {"values": True, "calcs": [], "fields": ""}
                }
            },
            {
                "id": 7,
                "title": "Топ сотрудников по общему количеству товара (шт)",
                "type": "bargauge",
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 26},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": "SELECT employee as 'ФИО', total_quantity as 'Общее количество (шт)' FROM izlishka_employee_summary WHERE employee != 'Не указан' AND employee != '' ORDER BY total_quantity DESC LIMIT 15;",
                    "rawQueryText": "SELECT employee as 'ФИО', total_quantity as 'Общее количество (шт)' FROM izlishka_employee_summary WHERE employee != 'Не указан' AND employee != '' ORDER BY total_quantity DESC LIMIT 15;"
                }],
                "options": {
                    "orientation": "horizontal",
                    "displayMode": "gradient",
                    "showUnfilled": True,
                    "reduceOptions": {"values": True, "calcs": [], "fields": ""}
                }
            },

            # Row 5: Full Table Svod with Date Range per Employee
            {
                "id": 8,
                "title": "Сводная таблица по сотрудникам за весь период",
                "type": "table",
                "gridPos": {"h": 12, "w": 24, "x": 0, "y": 34},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": "SELECT employee as 'ФИО сотрудника', unique_skus as 'Уникальных SKU', total_quantity as 'Количество (шт)', unique_cells as 'Уникальных ячеек', total_operations as 'Всего операций', confirmed_count as 'Собрано (Подтверждено)', missing_count as 'Отсутствует', first_operation as 'Первая операция (Дата/Время)', last_operation as 'Последняя операция (Дата/Время)' FROM izlishka_employee_summary WHERE employee != 'Не указан' AND employee != '' ORDER BY total_quantity DESC;",
                    "rawQueryText": "SELECT employee as 'ФИО сотрудника', unique_skus as 'Уникальных SKU', total_quantity as 'Количество (шт)', unique_cells as 'Уникальных ячеек', total_operations as 'Всего операций', confirmed_count as 'Собрано (Подтверждено)', missing_count as 'Отсутствует', first_operation as 'Первая операция (Дата/Время)', last_operation as 'Последняя операция (Дата/Время)' FROM izlishka_employee_summary WHERE employee != 'Не указан' AND employee != '' ORDER BY total_quantity DESC;"
                }],
                "options": {
                    "footer": {"show": True, "enablePagination": True}
                }
            }
        ]
    },
    "overwrite": True
}

def import_dashboard():
    req = urllib.request.Request(
        f"{GRAFANA_URL}/api/dashboards/db",
        data=json.dumps(dashboard_izlishka).encode('utf-8'),
        headers={"Content-Type": "application/json", "Authorization": AUTH_HEADER}
    )
    try:
        resp = urllib.request.urlopen(req)
        res = json.loads(resp.read().decode('utf-8'))
        print(f"Dashboard 'Излишка — Сводный отчет по сотрудникам и по дням' updated successfully! URL: {GRAFANA_URL}{res.get('url')}")
    except Exception as e:
        print(f"Error importing dashboard: {e}")

if __name__ == "__main__":
    import_dashboard()
