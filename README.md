# Подключение Google Таблицы к Grafana (Складской Учет)

Данный проект настраивает полную интеграцию между **Google Таблицей** и **Grafana** для интерактивной визуализации складского учета и отслеживания статусов размещения товаров.

## 🔗 Источник данных (Google Sheet)
* **Ссылка на Google Таблицу:** [Складской Учет](https://docs.google.com/spreadsheets/d/1vRYsfBey2qTmLf9iCkxSU4tb85e6nhYZzwaQ7DrMkII/edit?gid=1220218080#gid=1220218080)
* **ID таблицы:** `1vRYsfBey2qTmLf9iCkxSU4tb85e6nhYZzwaQ7DrMkII`
* **GID листа:** `1220218080`
* **Объем данных:** ~24 573 записи (186 517+ товаров)

---

## 🚀 Настроенные решения подключения

### 1. Высокопроизводительная синхронизация с SQLite (Рекомендуется)
Автоматический Python-скрипт скачивает данные из Google Sheets, парсит поля, приводит типы данных и обновляет базу данных SQLite с индексами для мгновенного выполнения SQL-запросов в Grafana.

* **Файл скрипта:** `sync_sheet.py`
* **Файл базы данных:** `warehouse.sqlite`
* **Плагин Grafana:** `frser-sqlite-datasource` (Уже установлен и настроен)

#### Запуск разовой синхронизации:
```bash
python3 sync_sheet.py
```

#### Запуск фонового демона автообновления (каждые 60 секунд):
```bash
python3 sync_sheet.py --loop 60
```

---

### 2. Прямое подключение без API ключей (Infinity Plugin)
Grafana обращается напрямую к публичному CSV-экспорту Google Sheets в реальном времени.

* **Плагин Grafana:** `yesoreyeram-infinity-datasource` (Уже установлен и настроен)
* **URL подгрузки:** `https://docs.google.com/spreadsheets/d/1vRYsfBey2qTmLf9iCkxSU4tb85e6nhYZzwaQ7DrMkII/export?format=csv&gid=1220218080`

---

### 3. Официальный плагин Google Sheets API
* **Плагин Grafana:** `grafana-googlesheets-datasource` (Уже установлен)

---

## 📊 Доступные Дашборды в Grafana (`http://localhost:3000`)

1. **[Складской Учет - Google Sheets (SQLite Data)](http://localhost:3000/d/warehouse_sqlite_dash)**
   - **Всего позиций:** 24 573
   - **Общее количество (шт):** 186 517
   - **Подтверждено:** 406
   - **Отсутствует:** 20
   - **Ошибок размещения:** 1
   - **Диаграмма статусов размещения** (Donut chart)
   - **Диаграмма ТОП категорий** (Pie chart)
   - **Нагрузка сотрудников (ФИО)** (Bar chart)
   - **Интерактивная таблица операций с пагинацией**

2. **[Складской Учет - Google Sheets (Прямой CSV)](http://localhost:3000/d/warehouse_infinity_dash)**
   - Прямой живой вывод таблицы данных из Google Sheets.

---

## 📁 Структура проекта
* `sync_sheet.py` — Скрипт синхронизации Google Sheets → SQLite.
* `create_dashboards.py` — Скрипт автоматического импорта и обновления дашбордов Grafana.
* `warehouse.sqlite` — База данных SQLite с загруженными записями.
* `README.md` — Документация и инструкция.
