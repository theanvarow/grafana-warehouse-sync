#!/usr/bin/env python3
import urllib.request
import json
import sys

GRAFANA_URL = "http://127.0.0.1:3000"
AUTH_HEADER = "Basic YWRtaW46YWRtaW4="
SQLITE_UID = "bfw4w68p7r5kwc"

dashboard_monitoring = {
    "dashboard": {
        "id": None,
        "uid": "warehouse_monitoring_dynamics",
        "title": "Мониторинг Склада — Динамика по направлениям и сменам",
        "tags": ["monitoring", "dynamics", "shifts", "warehouse", "directions"],
        "timezone": "browser",
        "refresh": "10s",
        "schemaVersion": 39,
        "version": 1,
        "panels": [
            # ----------------------------------------------------
            # ROW 1: HEADER & KPI CARDS
            # ----------------------------------------------------
            {
                "id": 1,
                "title": "🔄 Излишка: Всего операций",
                "type": "stat",
                "gridPos": {"h": 4, "w": 4, "x": 0, "y": 0},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": "SELECT count(*) as value FROM izlishka WHERE status != '';",
                    "rawQueryText": "SELECT count(*) as value FROM izlishka WHERE status != '';"
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
                "id": 2,
                "title": "📦 Излишка: Объем (шт)",
                "type": "stat",
                "gridPos": {"h": 4, "w": 4, "x": 4, "y": 0},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": "SELECT coalesce(sum(quantity), 0) as value FROM izlishka;",
                    "rawQueryText": "SELECT coalesce(sum(quantity), 0) as value FROM izlishka;"
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
                "id": 3,
                "title": "📋 Склад / Инвентарь: Объем (шт)",
                "type": "stat",
                "gridPos": {"h": 4, "w": 4, "x": 8, "y": 0},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": "SELECT coalesce(sum(quantity), 0) as value FROM inventory;",
                    "rawQueryText": "SELECT coalesce(sum(quantity), 0) as value FROM inventory;"
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
                "id": 4,
                "title": "👥 Активных сотрудников",
                "type": "stat",
                "gridPos": {"h": 4, "w": 4, "x": 12, "y": 0},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": "SELECT count(DISTINCT employee) as value FROM izlishka WHERE employee != 'Не указан' AND employee != '';",
                    "rawQueryText": "SELECT count(DISTINCT employee) as value FROM izlishka WHERE employee != 'Не указан' AND employee != '';"
                }],
                "options": {
                    "reduceOptions": {"values": False, "calcs": ["lastNotNull"]},
                    "colorMode": "value", "graphMode": "none"
                },
                "fieldConfig": {
                    "defaults": {"color": {"mode": "thresholds"}, "thresholds": {"mode": "absolute", "steps": [{"color": "cyan", "value": None}]}}
                }
            },
            {
                "id": 5,
                "title": "⚡ Доля подтверждения (%)",
                "type": "gauge",
                "gridPos": {"h": 4, "w": 4, "x": 16, "y": 0},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": "SELECT round(100.0 * count(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN 1 END) / nullif(count(*), 0), 1) as value FROM izlishka WHERE status != '';",
                    "rawQueryText": "SELECT round(100.0 * count(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN 1 END) / nullif(count(*), 0), 1) as value FROM izlishka WHERE status != '';"
                }],
                "options": {
                    "reduceOptions": {"values": False, "calcs": ["lastNotNull"]},
                    "showThresholdLabels": False,
                    "showThresholdMarkers": True
                },
                "fieldConfig": {
                    "defaults": {
                        "min": 0, "max": 100, "unit": "percent",
                        "color": {"mode": "thresholds"},
                        "thresholds": {"mode": "absolute", "steps": [
                            {"color": "red", "value": None},
                            {"color": "yellow", "value": 70},
                            {"color": "green", "value": 90}
                        ]}
                    }
                }
            },
            {
                "id": 6,
                "title": "❌ Отсутствует (шт)",
                "type": "stat",
                "gridPos": {"h": 4, "w": 4, "x": 20, "y": 0},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": "SELECT coalesce(sum(CASE WHEN status = 'Отсутствует' THEN quantity ELSE 0 END), 0) as value FROM izlishka;",
                    "rawQueryText": "SELECT coalesce(sum(CASE WHEN status = 'Отсутствует' THEN quantity ELSE 0 END), 0) as value FROM izlishka;"
                }],
                "options": {
                    "reduceOptions": {"values": False, "calcs": ["lastNotNull"]},
                    "colorMode": "value", "graphMode": "none"
                },
                "fieldConfig": {
                    "defaults": {"color": {"mode": "thresholds"}, "thresholds": {"mode": "absolute", "steps": [{"color": "red", "value": None}]}}
                }
            },

            # ----------------------------------------------------
            # ROW 2: ДИНАМИКА И СРАВНЕНИЕ СМЕН
            # ----------------------------------------------------
            {
                "id": 7,
                "title": "📅 Ежедневная динамика объема по направлениям (Излишка vs Инвентарь)",
                "type": "barchart",
                "gridPos": {"h": 8, "w": 14, "x": 0, "y": 4},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": """
                    SELECT 
                        substr(created_at, 1, 10) as "Дата",
                        sum(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN quantity ELSE 0 END) as "Подтверждено (Излишка)",
                        sum(CASE WHEN status = 'Отсутствует' THEN quantity ELSE 0 END) as "Отсутствует (Излишка)"
                    FROM izlishka
                    WHERE created_at != ''
                    GROUP BY "Дата"
                    ORDER BY "Дата" ASC;
                    """,
                    "rawQueryText": """
                    SELECT 
                        substr(created_at, 1, 10) as "Дата",
                        sum(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN quantity ELSE 0 END) as "Подтверждено (Излишка)",
                        sum(CASE WHEN status = 'Отсутствует' THEN quantity ELSE 0 END) as "Отсутствует (Излишка)"
                    FROM izlishka
                    WHERE created_at != ''
                    GROUP BY "Дата"
                    ORDER BY "Дата" ASC;
                    """
                }],
                "options": {
                    "xField": "Дата",
                    "stacking": {"mode": "normal"},
                    "legend": {"displayMode": "list", "placement": "bottom"}
                }
            },
            {
                "id": 8,
                "title": "⚖️ Сравнение смен (1 смена vs 2 смена: Объем шт)",
                "type": "barchart",
                "gridPos": {"h": 8, "w": 10, "x": 14, "y": 4},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": """
                    SELECT 
                        shift as "Смена",
                        coalesce(sum(quantity), 0) as "Объем (шт)",
                        count(DISTINCT barcode) as "Уникальных SKU",
                        count(*) as "Операций"
                    FROM izlishka
                    WHERE shift IN ('1 смена', '2 смена')
                    GROUP BY shift
                    ORDER BY shift;
                    """,
                    "rawQueryText": """
                    SELECT 
                        shift as "Смена",
                        coalesce(sum(quantity), 0) as "Объем (шт)",
                        count(DISTINCT barcode) as "Уникальных SKU",
                        count(*) as "Операций"
                    FROM izlishka
                    WHERE shift IN ('1 смена', '2 смена')
                    GROUP BY shift
                    ORDER BY shift;
                    """
                }],
                "options": {
                    "xField": "Смена",
                    "legend": {"displayMode": "list", "placement": "bottom"}
                }
            },

            # ----------------------------------------------------
            # ROW 3: СВОДНАЯ МАТРИЦА ДИНАМИКИ (ДЕНЬ × НАПРАВЛЕНИЕ × СМЕНА)
            # ----------------------------------------------------
            {
                "id": 9,
                "title": "📊 Ежедневная матрица выполнения: Направления × Смены (в динамике)",
                "type": "table",
                "gridPos": {"h": 9, "w": 24, "x": 0, "y": 12},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": """
                    SELECT 
                        substr(created_at, 1, 10) as "Дата",
                        'Излишка' as "Направление",
                        coalesce(nullif(shift, ''), 'Не указана') as "Смена",
                        count(DISTINCT barcode) as "Кол-во SKU",
                        coalesce(sum(quantity), 0) as "Всего объем (шт)",
                        sum(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN quantity ELSE 0 END) as "Подтверждено (шт)",
                        sum(CASE WHEN status = 'Отсутствует' THEN quantity ELSE 0 END) as "Отсутствует (шт)",
                        round(100.0 * sum(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN quantity ELSE 0 END) / nullif(sum(quantity), 0), 1) as "Выполнение %",
                        count(DISTINCT CASE WHEN employee != 'Не указан' AND employee != '' THEN employee END) as "Сотрудников"
                    FROM izlishka
                    WHERE created_at != ''
                    GROUP BY "Дата", "Смена"

                    UNION ALL

                    SELECT 
                        substr(created_at, 1, 10) as "Дата",
                        'Инвентарь / Склад' as "Направление",
                        coalesce(nullif(shift, ''), 'Смена 1') as "Смена",
                        count(DISTINCT barcode) as "Кол-во SKU",
                        coalesce(sum(quantity), 0) as "Всего объем (шт)",
                        coalesce(sum(quantity), 0) as "Подтверждено (шт)",
                        0 as "Отсутствует (шт)",
                        100.0 as "Выполнение %",
                        count(DISTINCT CASE WHEN employee != 'Не указан' AND employee != '' THEN employee END) as "Сотрудников"
                    FROM inventory
                    WHERE created_at != ''
                    GROUP BY "Дата", "Смена"

                    ORDER BY "Дата" DESC, "Направление" ASC, "Смена" ASC;
                    """,
                    "rawQueryText": """
                    SELECT 
                        substr(created_at, 1, 10) as "Дата",
                        'Излишка' as "Направление",
                        coalesce(nullif(shift, ''), 'Не указана') as "Смена",
                        count(DISTINCT barcode) as "Кол-во SKU",
                        coalesce(sum(quantity), 0) as "Всего объем (шт)",
                        sum(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN quantity ELSE 0 END) as "Подтверждено (шт)",
                        sum(CASE WHEN status = 'Отсутствует' THEN quantity ELSE 0 END) as "Отсутствует (шт)",
                        round(100.0 * sum(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN quantity ELSE 0 END) / nullif(sum(quantity), 0), 1) as "Выполнение %",
                        count(DISTINCT CASE WHEN employee != 'Не указан' AND employee != '' THEN employee END) as "Сотрудников"
                    FROM izlishka
                    WHERE created_at != ''
                    GROUP BY "Дата", "Смена"

                    UNION ALL

                    SELECT 
                        substr(created_at, 1, 10) as "Дата",
                        'Инвентарь / Склад' as "Направление",
                        coalesce(nullif(shift, ''), 'Смена 1') as "Смена",
                        count(DISTINCT barcode) as "Кол-во SKU",
                        coalesce(sum(quantity), 0) as "Всего объем (шт)",
                        coalesce(sum(quantity), 0) as "Подтверждено (шт)",
                        0 as "Отсутствует (шт)",
                        100.0 as "Выполнение %",
                        count(DISTINCT CASE WHEN employee != 'Не указан' AND employee != '' THEN employee END) as "Сотрудников"
                    FROM inventory
                    WHERE created_at != ''
                    GROUP BY "Дата", "Смена"

                    ORDER BY "Дата" DESC, "Направление" ASC, "Смена" ASC;
                    """
                }],
                "options": {
                    "showHeader": True
                },
                "fieldConfig": {
                    "defaults": {
                        "custom": {
                            "align": "auto",
                            "displayMode": "auto"
                        }
                    },
                    "overrides": [
                        {
                            "matcher": {"id": "byName", "options": "Выполнение %"},
                            "properties": [
                                {"id": "custom.displayMode", "options": "color-background"},
                                {"id": "thresholds", "options": {
                                    "mode": "absolute",
                                    "steps": [
                                        {"color": "red", "value": None},
                                        {"color": "orange", "value": 50},
                                        {"color": "green", "value": 90}
                                    ]
                                }}
                            ]
                        }
                    ]
                }
            },

            # ----------------------------------------------------
            # ROW 4: ЛИДЕРЫ ПО СМЕНАМ (1 СМЕНА VS 2 СМЕНА)
            # ----------------------------------------------------
            {
                "id": 10,
                "title": "☀️ 1 смена: Топ сотрудников по объему",
                "type": "table",
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 21},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": """
                    SELECT 
                        employee as "Сотрудник",
                        count(DISTINCT barcode) as "SKU",
                        coalesce(sum(quantity), 0) as "Объем (шт)",
                        sum(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN 1 ELSE 0 END) as "Собрано строк",
                        count(*) as "Всего строк"
                    FROM izlishka
                    WHERE shift = '1 смена' AND employee != 'Не указан' AND employee != ''
                    GROUP BY employee
                    ORDER BY "Объем (шт)" DESC
                    LIMIT 15;
                    """,
                    "rawQueryText": """
                    SELECT 
                        employee as "Сотрудник",
                        count(DISTINCT barcode) as "SKU",
                        coalesce(sum(quantity), 0) as "Объем (шт)",
                        sum(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN 1 ELSE 0 END) as "Собрано строк",
                        count(*) as "Всего строк"
                    FROM izlishka
                    WHERE shift = '1 смена' AND employee != 'Не указан' AND employee != ''
                    GROUP BY employee
                    ORDER BY "Объем (шт)" DESC
                    LIMIT 15;
                    """
                }],
                "options": {"showHeader": True}
            },
            {
                "id": 11,
                "title": "🌙 2 смена: Топ сотрудников по объему",
                "type": "table",
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 21},
                "datasource": {"type": "frser-sqlite-datasource", "uid": SQLITE_UID},
                "targets": [{
                    "refId": "A",
                    "queryText": """
                    SELECT 
                        employee as "Сотрудник",
                        count(DISTINCT barcode) as "SKU",
                        coalesce(sum(quantity), 0) as "Объем (шт)",
                        sum(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN 1 ELSE 0 END) as "Собрано строк",
                        count(*) as "Всего строк"
                    FROM izlishka
                    WHERE shift = '2 смена' AND employee != 'Не указан' AND employee != ''
                    GROUP BY employee
                    ORDER BY "Объем (шт)" DESC
                    LIMIT 15;
                    """,
                    "rawQueryText": """
                    SELECT 
                        employee as "Сотрудник",
                        count(DISTINCT barcode) as "SKU",
                        coalesce(sum(quantity), 0) as "Объем (шт)",
                        sum(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN 1 ELSE 0 END) as "Собрано строк",
                        count(*) as "Всего строк"
                    FROM izlishka
                    WHERE shift = '2 смена' AND employee != 'Не указан' AND employee != ''
                    GROUP BY employee
                    ORDER BY "Объем (шт)" DESC
                    LIMIT 15;
                    """
                }],
                "options": {"showHeader": True}
            }
        ]
    },
    "overwrite": True
}

def publish_dashboard():
    req = urllib.request.Request(
        f"{GRAFANA_URL}/api/dashboards/db",
        headers={
            "Authorization": AUTH_HEADER,
            "Content-Type": "application/json"
        },
        data=json.dumps(dashboard_monitoring).encode('utf-8')
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print("✅ Grafana Dashboard created/updated successfully!")
            print(f"URL: {GRAFANA_URL}{data.get('url')}")
            print(f"UID: {data.get('uid')}")
    except Exception as e:
        print(f"❌ Failed to publish dashboard: {e}")
        if hasattr(e, 'read'):
            print(e.read().decode('utf-8'))
        sys.exit(1)

if __name__ == "__main__":
    publish_dashboard()
