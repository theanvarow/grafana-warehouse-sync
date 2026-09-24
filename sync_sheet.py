#!/usr/bin/env python3
import urllib.request
import csv
import sqlite3
import io
import time
import argparse
import sys
import os

SPREADSHEET_ID = "1vRYsfBey2qTmLf9iCkxSU4tb85e6nhYZzwaQ7DrMkII"
GID = "1220218080"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "warehouse.sqlite")

def sync_data():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Fetching Google Sheet data...")
    req = urllib.request.Request(CSV_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode('utf-8')

    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Received {len(rows)} rows from Google Sheets.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table with normalized column names
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        barcode TEXT,
        cell TEXT,
        category TEXT,
        description TEXT,
        quantity INTEGER,
        status TEXT,
        is_correct_placement TEXT,
        employee TEXT,
        shift TEXT,
        created_at TEXT,
        product_id INTEGER
    )
    """)

    # Create table with original Russian column names for compatibility
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory_ru (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        "ШК товара" TEXT,
        "Ячейка" TEXT,
        "Категория" TEXT,
        "Описание" TEXT,
        "Количество" INTEGER,
        "Статус" TEXT,
        "Товар размещён правильно" TEXT,
        "ФИО" TEXT,
        "Смена" TEXT,
        "Дата" TEXT,
        "product_id" INTEGER
    )
    """)

    cursor.execute("DELETE FROM inventory")
    cursor.execute("DELETE FROM inventory_ru")

    insert_norm = """
    INSERT INTO inventory (barcode, cell, category, description, quantity, status, is_correct_placement, employee, shift, created_at, product_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    insert_ru = """
    INSERT INTO inventory_ru ("ШК товара", "Ячейка", "Категория", "Описание", "Количество", "Статус", "Товар размещён правильно", "ФИО", "Смена", "Дата", "product_id")
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    data_norm = []
    data_ru = []

    for r in rows:
        barcode = r.get('ШК товара', '').strip()
        cell = r.get('Ячейка', '').strip()
        category = r.get('Категория', '').strip()
        description = r.get('Описание', '').strip()
        
        try:
            quantity = int(r.get('Количество', 0))
        except (ValueError, TypeError):
            quantity = 0

        status = r.get('Статус', '').strip()
        is_correct = r.get('Товар размещён правильно', '').strip()
        employee = r.get('ФИО', '').strip()
        shift = r.get('Смена ', r.get('Смена', '')).strip()
        created_at = r.get('Дата', '').strip()

        try:
            product_id = int(r.get('product_id', 0))
        except (ValueError, TypeError):
            product_id = 0

        data_norm.append((barcode, cell, category, description, quantity, status, is_correct, employee, shift, created_at, product_id))
        data_ru.append((barcode, cell, category, description, quantity, status, is_correct, employee, shift, created_at, product_id))

    cursor.executemany(insert_norm, data_norm)
    cursor.executemany(insert_ru, data_ru)

    # Create indexes for fast Grafana querying
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_barcode ON inventory(barcode)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_cell ON inventory(cell)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_status ON inventory(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_category ON inventory(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_employee ON inventory(employee)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_created ON inventory(created_at)")

    conn.commit()
    conn.close()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Database synced successfully ({len(rows)} records stored in {DB_PATH}).")

def main():
    parser = argparse.ArgumentParser(description="Sync Google Sheets to SQLite for Grafana")
    parser.add_argument("--loop", type=int, default=0, help="Sync interval in seconds (0 = run once)")
    args = parser.parse_args()

    if args.loop > 0:
        print(f"Starting continuous sync daemon every {args.loop} seconds...")
        while True:
            try:
                sync_data()
            except Exception as e:
                print(f"Error during sync: {e}", file=sys.stderr)
            time.sleep(args.loop)
    else:
        sync_data()

if __name__ == "__main__":
    main()
