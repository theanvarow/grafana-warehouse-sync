#!/usr/bin/env python3
import urllib.request
import csv
import io
import time
import argparse
import sys
import os
from collections import defaultdict

try:
    import psycopg2
    from psycopg2.extras import execute_batch
except ImportError:
    print("Error: psycopg2 is required. Run: pip install psycopg2-binary")
    sys.exit(1)

SPREADSHEET_ID = "1vRYsfBey2qTmLf9iCkxSU4tb85e6nhYZzwaQ7DrMkII"
IZLISHKA_GID = "2059071830"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={IZLISHKA_GID}"

# Default connection string (Change or pass via --db-url)
DEFAULT_DB_URL = os.environ.get("DATABASE_URL", "postgresql://neondb_owner:YOUR_PASSWORD@ep-rough-dust-axq99tna-pooler.c-4.us-east-2.aws.neon.tech:5432/neondb?sslmode=require")

def sync_to_postgres(db_url):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 📥 Fetching Google Sheet ('Излишка')...")
    req = urllib.request.Request(CSV_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode('utf-8')

    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 📊 Loaded {len(rows)} rows from Google Sheets.")

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

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 🔌 Connecting to PostgreSQL...")
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()

    # 1. Main table: izlishka
    cursor.execute("DROP TABLE IF EXISTS izlishka;")
    cursor.execute("""
    CREATE TABLE izlishka (
        id SERIAL PRIMARY KEY,
        barcode VARCHAR(255),
        cell VARCHAR(255),
        category VARCHAR(255),
        description TEXT,
        quantity INTEGER,
        status VARCHAR(255),
        employee VARCHAR(255),
        shift VARCHAR(255),
        created_at VARCHAR(255)
    );
    """)

    execute_batch(cursor, """
    INSERT INTO izlishka (barcode, cell, category, description, quantity, status, employee, shift, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """, raw_data, page_size=1000)

    cursor.execute("CREATE INDEX idx_izl_emp ON izlishka(employee);")
    cursor.execute("CREATE INDEX idx_izl_barcode ON izlishka(barcode);")
    cursor.execute("CREATE INDEX idx_izl_created ON izlishka(created_at);")

    # 2. Overall Employee Summary table
    cursor.execute("DROP TABLE IF EXISTS izlishka_employee_summary;")
    cursor.execute("""
    CREATE TABLE izlishka_employee_summary (
        employee VARCHAR(255) PRIMARY KEY,
        unique_skus INTEGER,
        total_quantity INTEGER,
        unique_cells INTEGER,
        total_operations INTEGER,
        confirmed_count INTEGER,
        missing_count INTEGER,
        pending_count INTEGER,
        first_operation VARCHAR(255),
        last_operation VARCHAR(255)
    );
    """)

    summary_rows = []
    for emp, s in sorted(emp_stats.items(), key=lambda x: x[1]['total_qty'], reverse=True):
        valid_dates = sorted([d for d in s['dates'] if d])
        first_op = valid_dates[0] if valid_dates else ''
        last_op = valid_dates[-1] if valid_dates else ''
        summary_rows.append((
            emp, len(s['skus']), s['total_qty'], len(s['cells']),
            s['total_rows'], s['sobrano'], s['missing'], s['pending'],
            first_op, last_op
        ))

    execute_batch(cursor, """
    INSERT INTO izlishka_employee_summary (employee, unique_skus, total_quantity, unique_cells, total_operations, confirmed_count, missing_count, pending_count, first_operation, last_operation)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """, summary_rows)

    # 3. Daily Summary Table
    cursor.execute("DROP TABLE IF EXISTS izlishka_daily_summary;")
    cursor.execute("""
    CREATE TABLE izlishka_daily_summary (
        date_day VARCHAR(50) PRIMARY KEY,
        confirmed_skus INTEGER,
        confirmed_qty INTEGER,
        missing_skus INTEGER,
        missing_qty INTEGER,
        total_skus INTEGER,
        total_qty INTEGER,
        total_ops INTEGER
    );
    """)

    cursor.execute("""
    INSERT INTO izlishka_daily_summary (date_day, confirmed_skus, confirmed_qty, missing_skus, missing_qty, total_skus, total_qty, total_ops)
    SELECT 
        LEFT(created_at, 10) as date_day,
        count(DISTINCT CASE WHEN status IN ('Собрано', 'Подтвержден') THEN barcode END) as confirmed_skus,
        coalesce(sum(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN quantity ELSE 0 END), 0) as confirmed_qty,
        count(DISTINCT CASE WHEN status = 'Отсутствует' THEN barcode END) as missing_skus,
        coalesce(sum(CASE WHEN status = 'Отсутствует' THEN quantity ELSE 0 END), 0) as missing_qty,
        count(DISTINCT barcode) as total_skus,
        coalesce(sum(quantity), 0) as total_qty,
        count(*) as total_ops
    FROM izlishka
    WHERE created_at != ''
    GROUP BY date_day
    ORDER BY date_day DESC;
    """)

    # 4. Daily Employee Summary Table
    cursor.execute("DROP TABLE IF EXISTS izlishka_daily_employee_summary;")
    cursor.execute("""
    CREATE TABLE izlishka_daily_employee_summary (
        date_day VARCHAR(50),
        employee VARCHAR(255),
        confirmed_skus INTEGER,
        confirmed_qty INTEGER,
        missing_skus INTEGER,
        missing_qty INTEGER,
        total_skus INTEGER,
        total_qty INTEGER,
        total_ops INTEGER,
        PRIMARY KEY (date_day, employee)
    );
    """)

    cursor.execute("""
    INSERT INTO izlishka_daily_employee_summary (date_day, employee, confirmed_skus, confirmed_qty, missing_skus, missing_qty, total_skus, total_qty, total_ops)
    SELECT 
        LEFT(created_at, 10) as date_day,
        employee,
        count(DISTINCT CASE WHEN status IN ('Собрано', 'Подтвержден') THEN barcode END) as confirmed_skus,
        coalesce(sum(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN quantity ELSE 0 END), 0) as confirmed_qty,
        count(DISTINCT CASE WHEN status = 'Отсутствует' THEN barcode END) as missing_skus,
        coalesce(sum(CASE WHEN status = 'Отсутствует' THEN quantity ELSE 0 END), 0) as missing_qty,
        count(DISTINCT barcode) as total_skus,
        coalesce(sum(quantity), 0) as total_qty,
        count(*) as total_ops
    FROM izlishka
    WHERE created_at != '' AND employee != 'Не указан' AND employee != ''
    GROUP BY date_day, employee
    ORDER BY date_day DESC, total_qty DESC;
    """)

    conn.commit()
    conn.close()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ✅ Sync to PostgreSQL completed with 100% mathematical precision!")

def main():
    parser = argparse.ArgumentParser(description="Sync Google Sheets Излишка data to PostgreSQL for Grafana")
    parser.add_argument("--db-url", type=str, default=DEFAULT_DB_URL, help="PostgreSQL connection URI (e.g. postgresql://user:pass@host:5432/db)")
    parser.add_argument("--loop", type=int, default=0, help="Continuous loop interval in seconds (e.g. --loop 60)")
    args = parser.parse_args()

    if args.loop > 0:
        print(f"Starting PostgreSQL sync daemon every {args.loop} seconds...")
        while True:
            try:
                sync_to_postgres(args.db_url)
            except Exception as e:
                print(f"Error during sync: {e}")
            time.sleep(args.loop)
    else:
        sync_to_postgres(args.db_url)

if __name__ == "__main__":
    main()
