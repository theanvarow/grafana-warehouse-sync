#!/usr/bin/env python3
import urllib.request
import csv
import sqlite3
import io
import os
from collections import defaultdict

SPREADSHEET_ID = "1vRYsfBey2qTmLf9iCkxSU4tb85e6nhYZzwaQ7DrMkII"
IZLISHKA_GID = "2059071830"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={IZLISHKA_GID}"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "warehouse.sqlite")
CSV_OUT_PATH = os.path.join(BASE_DIR, "izlishka_svod_report.csv")
CSV_DAILY_OUT_PATH = os.path.join(BASE_DIR, "izlishka_daily_svod_report.csv")
CSV_DAILY_EMP_OUT_PATH = os.path.join(BASE_DIR, "izlishka_daily_employee_svod_report.csv")

def generate_report():
    print("Fetching 'Излишка' sheet data from Google Sheets...")
    req = urllib.request.Request(CSV_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode('utf-8')

    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)
    print(f"Loaded {len(rows)} rows from 'Излишка' sheet.")

    emp_stats = defaultdict(lambda: {
        'total_rows': 0,
        'total_qty': 0,
        'skus': set(),
        'cells': set(),
        'sobrano': 0,
        'missing': 0,
        'pending': 0,
        'dates': []
    })

    total_skus = set()
    total_cells = set()
    total_qty = 0
    total_rows = len(rows)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS izlishka;")
    cursor.execute("""
    CREATE TABLE izlishka (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        barcode TEXT,
        cell TEXT,
        category TEXT,
        description TEXT,
        quantity INTEGER,
        status TEXT,
        employee TEXT,
        shift TEXT,
        created_at TEXT
    )
    """)

    raw_data = []
    for r in rows:
        barcode = r.get('ШК товара', '').strip()
        cell = r.get('Ячейка', '').strip()
        category = r.get('Категория', '').strip()
        description = r.get('Описание', '').strip()
        
        try:
            qty = int(r.get('Количество', 0))
        except (ValueError, TypeError):
            qty = 0

        status = r.get('Статус', '').strip()
        employee = r.get('ФИО', '').strip() or 'Не указан'
        shift = r.get('Смена ', r.get('Смена', '')).strip() or 'Не указана'
        created_at = r.get('Дата', '').strip()

        raw_data.append((barcode, cell, category, description, qty, status, employee, shift, created_at))

        s = emp_stats[employee]
        s['total_rows'] += 1
        s['total_qty'] += qty
        if barcode: s['skus'].add(barcode)
        if cell: s['cells'].add(cell)
        if created_at: s['dates'].append(created_at)

        status_lower = status.lower()
        if 'собрано' in status_lower or 'подтвержден' in status_lower:
            s['sobrano'] += 1
        elif 'отсутствует' in status_lower:
            s['missing'] += 1
        else:
            s['pending'] += 1

        total_qty += qty
        if barcode: total_skus.add(barcode)
        if cell: total_cells.add(cell)

    cursor.executemany("""
    INSERT INTO izlishka (barcode, cell, category, description, quantity, status, employee, shift, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, raw_data)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_izl_emp ON izlishka(employee)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_izl_barcode ON izlishka(barcode)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_izl_cell ON izlishka(cell)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_izl_created ON izlishka(created_at)")

    # 1. Summary by Employee (Overall)
    cursor.execute("DROP TABLE IF EXISTS izlishka_employee_summary;")
    cursor.execute("""
    CREATE TABLE izlishka_employee_summary (
        employee TEXT PRIMARY KEY,
        unique_skus INTEGER,
        total_quantity INTEGER,
        unique_cells INTEGER,
        total_operations INTEGER,
        confirmed_count INTEGER,
        missing_count INTEGER,
        pending_count INTEGER,
        first_operation TEXT,
        last_operation TEXT
    )
    """)

    summary_rows = []
    for emp, s in sorted(emp_stats.items(), key=lambda x: x[1]['total_qty'], reverse=True):
        valid_dates = sorted([d for d in s['dates'] if d])
        first_op = valid_dates[0] if valid_dates else ''
        last_op = valid_dates[-1] if valid_dates else ''

        summary_rows.append((
            emp,
            len(s['skus']),
            s['total_qty'],
            len(s['cells']),
            s['total_rows'],
            s['sobrano'],
            s['missing'],
            s['pending'],
            first_op,
            last_op
        ))

    cursor.executemany("""
    INSERT INTO izlishka_employee_summary (employee, unique_skus, total_quantity, unique_cells, total_operations, confirmed_count, missing_count, pending_count, first_operation, last_operation)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, summary_rows)

    # 2. Daily Overall Summary Table
    cursor.execute("DROP TABLE IF EXISTS izlishka_daily_summary;")
    cursor.execute("""
    CREATE TABLE izlishka_daily_summary (
        date_day TEXT PRIMARY KEY,
        confirmed_skus INTEGER,
        confirmed_qty INTEGER,
        missing_skus INTEGER,
        missing_qty INTEGER,
        total_skus INTEGER,
        total_qty INTEGER,
        total_ops INTEGER
    )
    """)

    cursor.execute("""
    INSERT INTO izlishka_daily_summary (date_day, confirmed_skus, confirmed_qty, missing_skus, missing_qty, total_skus, total_qty, total_ops)
    SELECT 
        substr(created_at, 1, 10) as date_day,
        count(DISTINCT CASE WHEN status IN ('Собрано', 'Подтвержден') THEN barcode END) as confirmed_skus,
        sum(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN quantity ELSE 0 END) as confirmed_qty,
        count(DISTINCT CASE WHEN status = 'Отсутствует' THEN barcode END) as missing_skus,
        sum(CASE WHEN status = 'Отсутствует' THEN quantity ELSE 0 END) as missing_qty,
        count(DISTINCT barcode) as total_skus,
        sum(quantity) as total_qty,
        count(*) as total_ops
    FROM izlishka
    WHERE created_at != ''
    GROUP BY date_day
    ORDER BY date_day DESC
    """)

    cursor.execute("SELECT date_day, confirmed_skus, confirmed_qty, missing_skus, missing_qty, total_skus, total_qty, total_ops FROM izlishka_daily_summary ORDER BY date_day DESC")
    daily_rows = cursor.fetchall()

    # 3. Daily Per Employee Summary Table
    cursor.execute("DROP TABLE IF EXISTS izlishka_daily_employee_summary;")
    cursor.execute("""
    CREATE TABLE izlishka_daily_employee_summary (
        date_day TEXT,
        employee TEXT,
        confirmed_skus INTEGER,
        confirmed_qty INTEGER,
        missing_skus INTEGER,
        missing_qty INTEGER,
        total_skus INTEGER,
        total_qty INTEGER,
        total_ops INTEGER,
        PRIMARY KEY (date_day, employee)
    )
    """)

    cursor.execute("""
    INSERT INTO izlishka_daily_employee_summary (date_day, employee, confirmed_skus, confirmed_qty, missing_skus, missing_qty, total_skus, total_qty, total_ops)
    SELECT 
        substr(created_at, 1, 10) as date_day,
        employee,
        count(DISTINCT CASE WHEN status IN ('Собрано', 'Подтвержден') THEN barcode END) as confirmed_skus,
        sum(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN quantity ELSE 0 END) as confirmed_qty,
        count(DISTINCT CASE WHEN status = 'Отсутствует' THEN barcode END) as missing_skus,
        sum(CASE WHEN status = 'Отсутствует' THEN quantity ELSE 0 END) as missing_qty,
        count(DISTINCT barcode) as total_skus,
        sum(quantity) as total_qty,
        count(*) as total_ops
    FROM izlishka
    WHERE created_at != '' AND employee != 'Не указан' AND employee != ''
    GROUP BY date_day, employee
    ORDER BY date_day DESC, total_qty DESC
    """)

    cursor.execute("SELECT date_day, employee, confirmed_skus, confirmed_qty, missing_skus, missing_qty, total_skus, total_qty, total_ops FROM izlishka_daily_employee_summary ORDER BY date_day DESC, total_qty DESC")
    daily_emp_rows = cursor.fetchall()

    conn.commit()
    conn.close()

    # Export Overall Employee CSV (All headers in Russian)
    with open(CSV_OUT_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ФИО сотрудника', 'Уникальных SKU', 'Общее количество (шт)', 'Уникальных ячеек', 'Всего операций', 'Собрано (Подтверждено)', 'Отсутствует', 'В процессе / Пусто', 'Первая операция (Дата/Время)', 'Последняя операция (Дата/Время)'])
        for r in summary_rows:
            writer.writerow(r)

    # Export Daily Summary CSV (All headers in Russian)
    with open(CSV_DAILY_OUT_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Дата', 'Собрано SKU', 'Собрано Кол-во (шт)', 'Отсутствует SKU', 'Отсутствует Кол-во (шт)', 'Всего SKU', 'Всего Кол-во (шт)', 'Всего операций'])
        for r in daily_rows:
            writer.writerow(r)

    # Export Daily Employee CSV (All headers in Russian)
    with open(CSV_DAILY_EMP_OUT_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Дата', 'ФИО сотрудника', 'Собрано SKU', 'Собрано Кол-во (шт)', 'Отсутствует SKU', 'Отсутствует Кол-во (шт)', 'Всего SKU', 'Всего Кол-во (шт)', 'Всего операций'])
        for r in daily_emp_rows:
            writer.writerow(r)

    print(f"Report with Russian headers generated successfully!")
    print(f"SQLite database updated: {DB_PATH}")
    print(f"Daily Employee CSV Report saved: {CSV_DAILY_EMP_OUT_PATH}")

    return {
        'total_rows': total_rows,
        'total_qty': total_qty,
        'total_skus': len(total_skus),
        'total_cells': len(total_cells),
        'total_employees': len(emp_stats),
        'daily_emp_rows': daily_emp_rows
    }

if __name__ == '__main__':
    res = generate_report()
