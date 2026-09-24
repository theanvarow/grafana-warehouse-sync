import json

DS_UID = 'cfw8t11o8b6yoa'
DS_TYPE = 'grafana-postgresql-datasource'

izlishka_dash = {
  'annotations': {'list': []},
  'editable': True,
  'fiscalYearStartMonth': 0,
  'graphTooltip': 1,
  'id': None,
  'links': [],
  'liveNow': False,
  'refresh': '10s',
  'schemaVersion': 39,
  'tags': ['izlishka', 'warehouse', 'exact'],
  'templating': {
    'list': [
      {
        'current': {'selected': True, 'text': '2026-08-25', 'value': '2026-08-25'},
        'datasource': {'type': DS_TYPE, 'uid': DS_UID},
        'definition': 'SELECT DISTINCT date_day FROM public.izlishka_daily_summary WHERE date_day != \'\' ORDER BY date_day DESC;',
        'hide': 0,
        'label': '📅 Дата (Sana)',
        'name': 'selected_date',
        'query': 'SELECT DISTINCT date_day FROM public.izlishka_daily_summary WHERE date_day != \'\' ORDER BY date_day DESC;',
        'refresh': 1,
        'sort': 2,
        'type': 'query'
      }
    ]
  },
  'timezone': 'browser',
  'title': 'Излишка — Сводный отчет (Дефрагментация)',
  'version': 40,
  'panels': [
    {
      'id': 1, 'title': 'Собрано операций / строк (${selected_date})', 'type': 'stat',
      'gridPos': {'h': 4, 'w': 4, 'x': 0, 'y': 0},
      'datasource': {'type': DS_TYPE, 'uid': DS_UID},
      'targets': [{'refId': 'A', 'dataset': 'neondb', 'editorMode': 'code', 'format': 'table', 'rawQuery': True, 'rawSql': "SELECT count(*) as value FROM public.izlishka WHERE LEFT(created_at, 10) = '${selected_date}' AND status IN ('Собрано', 'Подтвержден');", 'datasource': {'type': DS_TYPE, 'uid': DS_UID}}],
      'options': {'reduceOptions': {'calcs': ['lastNotNull'], 'values': False}, 'colorMode': 'value', 'graphMode': 'none'},
      'fieldConfig': {'defaults': {'color': {'mode': 'thresholds'}, 'thresholds': {'mode': 'absolute', 'steps': [{'color': 'green', 'value': None}]}}}
    },
    {
      'id': 2, 'title': 'Собрано Кол-во (шт) (${selected_date})', 'type': 'stat',
      'gridPos': {'h': 4, 'w': 4, 'x': 4, 'y': 0},
      'datasource': {'type': DS_TYPE, 'uid': DS_UID},
      'targets': [{'refId': 'A', 'dataset': 'neondb', 'editorMode': 'code', 'format': 'table', 'rawQuery': True, 'rawSql': "SELECT coalesce(sum(CASE WHEN status IN ('Собрано', 'Подтвержден') THEN quantity ELSE 0 END), 0) as value FROM public.izlishka WHERE LEFT(created_at, 10) = '${selected_date}';", 'datasource': {'type': DS_TYPE, 'uid': DS_UID}}],
      'options': {'reduceOptions': {'calcs': ['lastNotNull'], 'values': False}, 'colorMode': 'value', 'graphMode': 'none'},
      'fieldConfig': {'defaults': {'color': {'mode': 'thresholds'}, 'thresholds': {'mode': 'absolute', 'steps': [{'color': 'purple', 'value': None}]}}}
    },
    {
      'id': 3, 'title': 'Отсутствует операций / строк (${selected_date})', 'type': 'stat',
      'gridPos': {'h': 4, 'w': 4, 'x': 8, 'y': 0},
      'datasource': {'type': DS_TYPE, 'uid': DS_UID},
      'targets': [{'refId': 'A', 'dataset': 'neondb', 'editorMode': 'code', 'format': 'table', 'rawQuery': True, 'rawSql': "SELECT count(*) as value FROM public.izlishka WHERE LEFT(created_at, 10) = '${selected_date}' AND status = 'Отсутствует';", 'datasource': {'type': DS_TYPE, 'uid': DS_UID}}],
      'options': {'reduceOptions': {'calcs': ['lastNotNull'], 'values': False}, 'colorMode': 'value', 'graphMode': 'none'},
      'fieldConfig': {'defaults': {'color': {'mode': 'thresholds'}, 'thresholds': {'mode': 'absolute', 'steps': [{'color': 'red', 'value': None}]}}}
    },
    {
      'id': 4, 'title': 'Отсутствует Кол-во (шт) (${selected_date})', 'type': 'stat',
      'gridPos': {'h': 4, 'w': 4, 'x': 12, 'y': 0},
      'datasource': {'type': DS_TYPE, 'uid': DS_UID},
      'targets': [{'refId': 'A', 'dataset': 'neondb', 'editorMode': 'code', 'format': 'table', 'rawQuery': True, 'rawSql': "SELECT coalesce(sum(CASE WHEN status = 'Отсутствует' THEN quantity ELSE 0 END), 0) as value FROM public.izlishka WHERE LEFT(created_at, 10) = '${selected_date}';", 'datasource': {'type': DS_TYPE, 'uid': DS_UID}}],
      'options': {'reduceOptions': {'calcs': ['lastNotNull'], 'values': False}, 'colorMode': 'value', 'graphMode': 'none'},
      'fieldConfig': {'defaults': {'color': {'mode': 'thresholds'}, 'thresholds': {'mode': 'absolute', 'steps': [{'color': 'orange', 'value': None}]}}}
    },
    {
      'id': 5, 'title': 'Всего операций / строк (${selected_date})', 'type': 'stat',
      'gridPos': {'h': 4, 'w': 4, 'x': 16, 'y': 0},
      'datasource': {'type': DS_TYPE, 'uid': DS_UID},
      'targets': [{'refId': 'A', 'dataset': 'neondb', 'editorMode': 'code', 'format': 'table', 'rawQuery': True, 'rawSql': "SELECT count(*) as value FROM public.izlishka WHERE LEFT(created_at, 10) = '${selected_date}';", 'datasource': {'type': DS_TYPE, 'uid': DS_UID}}],
      'options': {'reduceOptions': {'calcs': ['lastNotNull'], 'values': False}, 'colorMode': 'value', 'graphMode': 'none'},
      'fieldConfig': {'defaults': {'color': {'mode': 'thresholds'}, 'thresholds': {'mode': 'absolute', 'steps': [{'color': 'blue', 'value': None}]}}}
    },
    {
      'id': 6, 'title': 'Всего Кол-во (шт) (${selected_date})', 'type': 'stat',
      'gridPos': {'h': 4, 'w': 4, 'x': 20, 'y': 0},
      'datasource': {'type': DS_TYPE, 'uid': DS_UID},
      'targets': [{'refId': 'A', 'dataset': 'neondb', 'editorMode': 'code', 'format': 'table', 'rawQuery': True, 'rawSql': "SELECT coalesce(sum(quantity), 0) as value FROM public.izlishka WHERE LEFT(created_at, 10) = '${selected_date}';", 'datasource': {'type': DS_TYPE, 'uid': DS_UID}}],
      'options': {'reduceOptions': {'calcs': ['lastNotNull'], 'values': False}, 'colorMode': 'value', 'graphMode': 'none'},
      'fieldConfig': {'defaults': {'color': {'mode': 'thresholds'}, 'thresholds': {'mode': 'absolute', 'steps': [{'color': 'teal', 'value': None}]}}}
    },
    {
      'id': 7, 'title': 'Выработка по сотрудникам за дату (${selected_date})', 'type': 'table',
      'gridPos': {'h': 12, 'w': 24, 'x': 0, 'y': 4},
      'datasource': {'type': DS_TYPE, 'uid': DS_UID},
      'targets': [{'refId': 'A', 'dataset': 'neondb', 'editorMode': 'code', 'format': 'table', 'rawQuery': True, 'rawSql': 'SELECT date_day as "Дата", employee as "ФИО сотрудника", confirmed_rows as "Собрано (Строк)", confirmed_qty as "Собрано (шт)", confirmed_skus as "Собрано (SKU)", missing_rows as "Отсутствует (Строк)", missing_qty as "Отсутствует (шт)", missing_skus as "Отсутствует (SKU)", total_ops as "Всего операций (Строк)", total_qty as "Всего Кол-во (шт)" FROM public.izlishka_daily_employee_summary WHERE date_day = \'${selected_date}\' ORDER BY total_qty DESC;', 'datasource': {'type': DS_TYPE, 'uid': DS_UID}}],
      'options': {'cellHeight': 'sm', 'footer': {'show': True, 'enablePagination': True, 'fields': '', 'reducer': ['sum']}}
    },
    {
      'id': 8, 'title': 'Общий свод по дням (Вся история)', 'type': 'table',
      'gridPos': {'h': 9, 'w': 24, 'x': 0, 'y': 16},
      'datasource': {'type': DS_TYPE, 'uid': DS_UID},
      'targets': [{'refId': 'A', 'dataset': 'neondb', 'editorMode': 'code', 'format': 'table', 'rawQuery': True, 'rawSql': 'SELECT date_day as "Дата", confirmed_rows as "Собрано (Строк)", confirmed_qty as "Собрано (шт)", confirmed_skus as "Собрано (SKU)", missing_rows as "Отсутствует (Строк)", missing_qty as "Отсутствует (шт)", missing_skus as "Отсутствует (SKU)", total_ops as "Всего операций (Строк)", total_qty as "Всего Кол-во (шт)" FROM public.izlishka_daily_summary ORDER BY date_day DESC;', 'datasource': {'type': DS_TYPE, 'uid': DS_UID}}],
      'options': {'cellHeight': 'sm', 'footer': {'show': True, 'enablePagination': True, 'fields': '', 'reducer': ['sum']}}
    },
    {
      'id': 9, 'title': 'Динамика операций (Строк) по дням', 'type': 'bargauge',
      'gridPos': {'h': 7, 'w': 12, 'x': 0, 'y': 25},
      'datasource': {'type': DS_TYPE, 'uid': DS_UID},
      'targets': [{'refId': 'A', 'dataset': 'neondb', 'editorMode': 'code', 'format': 'table', 'rawQuery': True, 'rawSql': 'SELECT date_day as "Дата", total_ops as "Количество операций" FROM public.izlishka_daily_summary ORDER BY date_day ASC;', 'datasource': {'type': DS_TYPE, 'uid': DS_UID}}],
      'options': {'orientation': 'vertical', 'displayMode': 'gradient', 'showUnfilled': True, 'reduceOptions': {'values': True, 'calcs': [], 'fields': ''}}
    },
    {
      'id': 10, 'title': 'Топ сотрудников за (${selected_date})', 'type': 'bargauge',
      'gridPos': {'h': 7, 'w': 12, 'x': 12, 'y': 25},
      'datasource': {'type': DS_TYPE, 'uid': DS_UID},
      'targets': [{'refId': 'A', 'dataset': 'neondb', 'editorMode': 'code', 'format': 'table', 'rawQuery': True, 'rawSql': 'SELECT employee as "ФИО", total_qty as "Количество товара (шт)" FROM public.izlishka_daily_employee_summary WHERE date_day = \'${selected_date}\' ORDER BY total_qty DESC LIMIT 15;', 'datasource': {'type': DS_TYPE, 'uid': DS_UID}}],
      'options': {'orientation': 'horizontal', 'displayMode': 'gradient', 'showUnfilled': True, 'reduceOptions': {'values': True, 'calcs': [], 'fields': ''}}
    },
    {
      'id': 11, 'title': 'Сводная таблица по сотрудникам за весь период (Вся история)', 'type': 'table',
      'gridPos': {'h': 12, 'w': 24, 'x': 0, 'y': 32},
      'datasource': {'type': DS_TYPE, 'uid': DS_UID},
      'targets': [{'refId': 'A', 'dataset': 'neondb', 'editorMode': 'code', 'format': 'table', 'rawQuery': True, 'rawSql': 'SELECT employee as "ФИО сотрудника", unique_skus as "Уникальных SKU", total_quantity as "Количество (шт)", unique_cells as "Уникальных ячеек", total_operations as "Всего операций", confirmed_count as "Собрано (Подтверждено)", missing_count as "Отсутствует", first_operation as "Первая операция (Дата/Время)", last_operation as "Последняя операция (Дата/Время)" FROM public.izlishka_employee_summary WHERE employee != \'Не указан\' AND employee != \'\' ORDER BY total_quantity DESC;', 'datasource': {'type': DS_TYPE, 'uid': DS_UID}}],
      'options': {'cellHeight': 'sm', 'footer': {'show': True, 'enablePagination': True, 'fields': '', 'reducer': ['sum']}}
    }
  ]
}

with open('/Users/this/Desktop/Graffana conect with table/exported_dashboards/izlishka_standalone.json', 'w', encoding='utf-8') as f:
    json.dump(izlishka_dash, f, indent=2, ensure_ascii=False)

print('Generated izlishka_standalone.json with Panel 11 successfully!')
