#!/usr/bin/env python3
import urllib.request
import csv
import io
import time
import os
import sys

# Load local .env if present
env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "1vRYsfBey2qTmLf9iCkxSU4tb85e6nhYZzwaQ7DrMkII")
IZLISHKA_GID = os.environ.get("IZLISHKA_GID", "2059071830")
SGT_GID = os.environ.get("SGT_GID", "1647276156")

IZLISHKA_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={IZLISHKA_GID}"
SGT_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={SGT_GID}"

NEON_URL = os.environ.get("DATABASE_URL", "postgresql://neondb_owner:YOUR_DATABASE_PASSWORD@ep-icy-sunset-aygvxck5-pooler.c-5.us-east-2.aws.neon.tech/neondb?sslmode=require")

try:
    import psycopg2
    from psycopg2.extras import execute_batch
    HAS_PG = True
except ImportError:
    HAS_PG = False

def fetch_csv(url):
    cache_bust_url = f"{url}&_t={int(time.time())}" if "?" in url else f"{url}?_t={int(time.time())}"
    req = urllib.request.Request(cache_bust_url, headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache", "Pragma": "no-cache"})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode('utf-8')

def sync_izlishka(cur_pg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 📥 Fetching 'Излишка' Sheet...")
    content = fetch_csv(IZLISHKA_CSV_URL)
    reader = csv.DictReader(io.StringIO(content))
    raw_data = []
    for r in reader:
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

        if barcode or employee != 'Не указан' or created_at:
            raw_data.append((barcode, cell, category, description, qty, status, employee, shift, created_at))

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 📊 Fetched {len(raw_data)} rows for Излишка.")

    cur_pg.execute("""
    CREATE TABLE IF NOT EXISTS public.izlishka (
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
    cur_pg.execute("TRUNCATE TABLE public.izlishka;")
    execute_batch(cur_pg, "INSERT INTO public.izlishka (barcode, cell, category, description, quantity, status, employee, shift, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);", raw_data, page_size=2000)

    # Recalculate izlishka daily summary
    cur_pg.execute("DROP TABLE IF EXISTS public.izlishka_daily_summary CASCADE;")
    cur_pg.execute("""
    CREATE TABLE public.izlishka_daily_summary (
        date_day VARCHAR(50) PRIMARY KEY,
        confirmed_rows INTEGER,
        confirmed_qty INTEGER,
        confirmed_skus INTEGER,
        missing_rows INTEGER,
        missing_qty INTEGER,
        missing_skus INTEGER,
        total_ops INTEGER,
        total_qty INTEGER,
        total_skus INTEGER
    );
    """)
    cur_pg.execute("""
    INSERT INTO public.izlishka_daily_summary
    SELECT 
        LEFT(created_at, 10),
        count(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN 1 END),
        coalesce(sum(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN quantity ELSE 0 END), 0),
        count(DISTINCT CASE WHEN status IN ('Собрано', 'Подтвержден') THEN barcode END),
        count(CASE WHEN status = 'Отсутствует' THEN 1 END),
        coalesce(sum(CASE WHEN status = 'Отсутствует' THEN quantity ELSE 0 END), 0),
        count(DISTINCT CASE WHEN status = 'Отсутствует' THEN barcode END),
        count(*),
        coalesce(sum(quantity), 0),
        count(DISTINCT barcode)
    FROM public.izlishka 
    WHERE created_at != '' 
    GROUP BY LEFT(created_at, 10) 
    ORDER BY LEFT(created_at, 10) DESC;
    """)

    # Recalculate izlishka daily employee summary
    cur_pg.execute("DROP TABLE IF EXISTS public.izlishka_daily_employee_summary CASCADE;")
    cur_pg.execute("""
    CREATE TABLE public.izlishka_daily_employee_summary (
        date_day VARCHAR(50),
        employee VARCHAR(255),
        confirmed_rows INTEGER,
        confirmed_qty INTEGER,
        confirmed_skus INTEGER,
        missing_rows INTEGER,
        missing_qty INTEGER,
        missing_skus INTEGER,
        total_ops INTEGER,
        total_qty INTEGER,
        total_skus INTEGER,
        PRIMARY KEY (date_day, employee)
    );
    """)
    cur_pg.execute("""
    INSERT INTO public.izlishka_daily_employee_summary
    SELECT 
        LEFT(created_at, 10),
        employee,
        count(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN 1 END),
        coalesce(sum(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN quantity ELSE 0 END), 0),
        count(DISTINCT CASE WHEN status IN ('Собрано', 'Подтвержден') THEN barcode END),
        count(CASE WHEN status = 'Отсутствует' THEN 1 END),
        coalesce(sum(CASE WHEN status = 'Отсутствует' THEN quantity ELSE 0 END), 0),
        count(DISTINCT CASE WHEN status = 'Отсутствует' THEN barcode END),
        count(*),
        coalesce(sum(quantity), 0),
        count(DISTINCT barcode)
    FROM public.izlishka 
    WHERE created_at != '' AND employee != 'Не указан' AND employee != '' 
    GROUP BY LEFT(created_at, 10), employee 
    ORDER BY LEFT(created_at, 10) DESC, coalesce(sum(quantity), 0) DESC;
    """)

    # Recalculate overall employee summary
    cur_pg.execute("DROP TABLE IF EXISTS public.izlishka_employee_summary CASCADE;")
    cur_pg.execute("""
    CREATE TABLE public.izlishka_employee_summary (
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
    cur_pg.execute("""
    INSERT INTO public.izlishka_employee_summary
    SELECT 
        employee,
        count(DISTINCT barcode),
        coalesce(sum(quantity), 0),
        count(DISTINCT cell),
        count(*),
        count(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN 1 END),
        count(CASE WHEN status = 'Отсутствует' THEN 1 END),
        count(CASE WHEN status NOT IN ('Собрано', 'Подтвержден', 'Отсутствует') THEN 1 END),
        min(created_at),
        max(created_at)
    FROM public.izlishka
    WHERE employee != 'Не указан' AND employee != ''
    GROUP BY employee
    ORDER BY coalesce(sum(quantity), 0) DESC;
    """)

def sync_sgt(cur_pg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 📥 Fetching 'СГТ' Sheet...")
    content = fetch_csv(SGT_CSV_URL)
    reader = csv.DictReader(io.StringIO(content))
    raw_data = []
    for r in reader:
        barcode = r.get('ШК товара', '').strip()
        cell = r.get('Ячейка', '').strip()
        category = r.get('Категория', '').strip()
        description = r.get('Описание', '').strip()
        try:
            qty = int(r.get('Количество', 0))
        except (ValueError, TypeError):
            qty = 0
        status = r.get('Статус', '').strip()
        is_placed = r.get('Товар размещён правильно', '').strip()
        employee = r.get('ФИО', '').strip() or 'Не указан'
        shift = r.get('Смена ', r.get('Смена', '')).strip() or 'Не указана'
        created_at = r.get('Дата', '').strip()
        product_id = r.get('product_id', '').strip()

        if barcode or employee != 'Не указан' or created_at:
            raw_data.append((barcode, cell, category, description, qty, status, is_placed, employee, shift, created_at, product_id))

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 📊 Fetched {len(raw_data)} rows for СГТ.")

    cur_pg.execute("""
    CREATE TABLE IF NOT EXISTS public.sgt (
        id SERIAL PRIMARY KEY,
        barcode VARCHAR(255),
        cell VARCHAR(255),
        category VARCHAR(255),
        description TEXT,
        quantity INTEGER,
        status VARCHAR(255),
        is_placed VARCHAR(255),
        employee VARCHAR(255),
        shift VARCHAR(255),
        created_at VARCHAR(255),
        product_id VARCHAR(255)
    );
    """)
    cur_pg.execute("TRUNCATE TABLE public.sgt;")
    execute_batch(cur_pg, "INSERT INTO public.sgt (barcode, cell, category, description, quantity, status, is_placed, employee, shift, created_at, product_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", raw_data, page_size=2000)

    # Recalculate sgt daily summary
    cur_pg.execute("DROP TABLE IF EXISTS public.sgt_daily_summary CASCADE;")
    cur_pg.execute("""
    CREATE TABLE public.sgt_daily_summary (
        date_day VARCHAR(50) PRIMARY KEY,
        confirmed_rows INTEGER,
        confirmed_qty INTEGER,
        confirmed_skus INTEGER,
        missing_rows INTEGER,
        missing_qty INTEGER,
        missing_skus INTEGER,
        total_ops INTEGER,
        total_qty INTEGER,
        total_skus INTEGER
    );
    """)
    cur_pg.execute("""
    INSERT INTO public.sgt_daily_summary
    SELECT 
        LEFT(created_at, 10),
        count(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN 1 END),
        coalesce(sum(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN quantity ELSE 0 END), 0),
        count(DISTINCT CASE WHEN status IN ('Собрано', 'Подтвержден') THEN barcode END),
        count(CASE WHEN status = 'Отсутствует' THEN 1 END),
        coalesce(sum(CASE WHEN status = 'Отсутствует' THEN quantity ELSE 0 END), 0),
        count(DISTINCT CASE WHEN status = 'Отсутствует' THEN barcode END),
        count(*),
        coalesce(sum(quantity), 0),
        count(DISTINCT barcode)
    FROM public.sgt 
    WHERE created_at != '' 
    GROUP BY LEFT(created_at, 10) 
    ORDER BY LEFT(created_at, 10) DESC;
    """)

    # Recalculate sgt daily employee summary
    cur_pg.execute("DROP TABLE IF EXISTS public.sgt_daily_employee_summary CASCADE;")
    cur_pg.execute("""
    CREATE TABLE public.sgt_daily_employee_summary (
        date_day VARCHAR(50),
        employee VARCHAR(255),
        confirmed_rows INTEGER,
        confirmed_qty INTEGER,
        confirmed_skus INTEGER,
        missing_rows INTEGER,
        missing_qty INTEGER,
        missing_skus INTEGER,
        total_ops INTEGER,
        total_qty INTEGER,
        total_skus INTEGER,
        PRIMARY KEY (date_day, employee)
    );
    """)
    cur_pg.execute("""
    INSERT INTO public.sgt_daily_employee_summary
    SELECT 
        LEFT(created_at, 10),
        employee,
        count(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN 1 END),
        coalesce(sum(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN quantity ELSE 0 END), 0),
        count(DISTINCT CASE WHEN status IN ('Собрано', 'Подтвержден') THEN barcode END),
        count(CASE WHEN status = 'Отсутствует' THEN 1 END),
        coalesce(sum(CASE WHEN status = 'Отсутствует' THEN quantity ELSE 0 END), 0),
        count(DISTINCT CASE WHEN status = 'Отсутствует' THEN barcode END),
        count(*),
        coalesce(sum(quantity), 0),
        count(DISTINCT barcode)
    FROM public.sgt 
    WHERE created_at != '' AND employee != 'Не указан' AND employee != '' 
    GROUP BY LEFT(created_at, 10), employee 
    ORDER BY LEFT(created_at, 10) DESC, coalesce(sum(quantity), 0) DESC;
    """)

    # Recalculate sgt employee summary
    cur_pg.execute("DROP TABLE IF EXISTS public.sgt_employee_summary CASCADE;")
    cur_pg.execute("""
    CREATE TABLE public.sgt_employee_summary (
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
    cur_pg.execute("""
    INSERT INTO public.sgt_employee_summary
    SELECT 
        employee,
        count(DISTINCT barcode),
        coalesce(sum(quantity), 0),
        count(DISTINCT cell),
        count(*),
        count(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN 1 END),
        count(CASE WHEN status = 'Отсутствует' THEN 1 END),
        count(CASE WHEN status NOT IN ('Собрано', 'Подтвержден', 'Отсутствует') THEN 1 END),
        min(created_at),
        max(created_at)
    FROM public.sgt
    WHERE employee != 'Не указан' AND employee != ''
    GROUP BY employee
    ORDER BY coalesce(sum(quantity), 0) DESC;
    """)

def do_full_sync():
    if not HAS_PG:
        print("psycopg2 not installed")
        return
    try:
        conn = psycopg2.connect(NEON_URL)
        cur = conn.cursor()
        sync_izlishka(cur)
        sync_sgt(cur)
        conn.commit()
        conn.close()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ✅ Full Sync Complete for both Излишка & СГТ!")
    except Exception as e:
        print(f"Sync error: {e}")

if __name__ == '__main__':
    interval = 60
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
        except:
            pass
    print(f"Starting Multi-Sheet Auto-Sync Daemon every {interval}s...")
    while True:
        do_full_sync()
        time.sleep(interval)
