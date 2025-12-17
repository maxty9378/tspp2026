import requests
import json
import urllib.parse
from typing import List, Dict

# Конфигурация NocoDB
NOCODB_URL = "https://nocodb.puzzlebot.top"
API_TOKEN = "avKy8Ov_rNMIRMf-hgneulQKWsrXMhqmdqfc6uR1"
BASE_ID = "375e6d69-0d8d-43f0-9100-3c50e70f5364"  # Старый ID из URL
PROJECT_ID = "p85y5kjn8iv8p0c"  # ID проекта "Телеграм приложение" (будет определен автоматически)
TABLE_NAME = "День 1"

def get_fio_from_record(record: Dict) -> str:
    """
    Извлекает ФИО сотрудника из записи, строго используя только правильный столбец
    Исключает столбцы типа "Тренер" и другие похожие
    """
    # Список исключаемых ключевых слов для столбцов, которые НЕ должны использоваться
    excluded_keywords = ["тренер", "trainer", "coach", "наставник", "преподаватель"]
    
    # Сначала пробуем точные совпадения
    fio = record.get("ФИО сотрудника") or record.get("ФИО сотрудника")
    
    # Если не нашли, ищем по ключам, но исключаем столбцы с исключаемыми словами
    if not fio:
        for key, value in record.items():
            key_lower = key.lower()
            # Проверяем, что это не исключаемый столбец
            is_excluded = any(excluded in key_lower for excluded in excluded_keywords)
            
            # Ищем только столбцы с "фио" или "fio", но не исключаемые
            if not is_excluded and ("фио" in key_lower or "fio" in key_lower):
                # Дополнительная проверка: не должен содержать слова о тренере
                if "сотрудник" in key_lower or "employee" in key_lower or key_lower == "фио" or key_lower == "fio":
                    fio = value or fio
                    if fio:
                        break
    
    return str(fio).strip() if fio else ""

def filter_and_sort_records(records: List[Dict]) -> List[Dict]:
    """
    Фильтрует записи (оставляет только с ФИО сотрудника) и сортирует по оценке
    """
    filtered_records = []
    for record in records:
        fio = get_fio_from_record(record)
        
        # Оставляем только записи с ФИО сотрудника
        if fio:
            filtered_records.append(record)
    
    # Сортируем по оценке по убыванию
    try:
        filtered_records = sorted(
            filtered_records, 
            key=lambda x: float(x.get("Оценка", 0) or 0), 
            reverse=True
        )
    except (ValueError, TypeError):
        pass
    
    return filtered_records

def get_table_data() -> List[Dict]:
    """
    Получает данные из таблицы NocoDB
    """
    # Пробуем разные варианты заголовков авторизации
    headers_variants = [
        {
            "xc-token": API_TOKEN,
            "Content-Type": "application/json"
        },
        {
            "xc-auth": API_TOKEN,
            "Content-Type": "application/json"
        },
        {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        },
        {
            "xc-token": API_TOKEN,
        }
    ]
    
    # Пробуем получить данные напрямую по имени таблицы (URL-кодированное)
    encoded_table_name = urllib.parse.quote(TABLE_NAME)
    
    # Варианты URL для получения данных напрямую
    # Пробуем с токеном как параметром (публичный API)
    direct_data_urls = [
        f"{NOCODB_URL}/api/v1/db/data/noco/{BASE_ID}/{encoded_table_name}",
        f"{NOCODB_URL}/api/v2/tables/{encoded_table_name}/records",
        f"{NOCODB_URL}/api/v1/db/data/{BASE_ID}/{encoded_table_name}",
        f"{NOCODB_URL}/api/v1/db/data/noco/{BASE_ID}/{encoded_table_name}?where=(Оценка,gt,0)",
    ]
    
    # Сначала пробуем получить данные напрямую
    # Пробуем токен как параметр запроса
    params_with_token = {
        "sort": "-Оценка",  # Сортировка по убыванию
        "token": API_TOKEN
    }
    
    params = {
        "sort": "-Оценка"  # Сортировка по убыванию
    }
    
    # Получаем список проектов для определения правильного ID
    print("Получение списка проектов...")
    headers = {"xc-token": API_TOKEN}
    projects_url = f"{NOCODB_URL}/api/v1/db/meta/projects"
    try:
        response = requests.get(projects_url, headers=headers, timeout=30)
        if response.status_code == 200:
            projects_data = response.json()
            projects = projects_data.get("list", []) if isinstance(projects_data, dict) else projects_data
            
            # Ищем проект "Телеграм приложение" или используем первый
            project_id = None
            for proj in projects:
                title = proj.get("title", "")
                proj_id = proj.get("id")
                print(f"  Найден проект: {title} (ID: {proj_id})")
                if "телеграм" in title.lower() or "telegram" in title.lower():
                    project_id = proj_id
                    print(f"  ✓ Используем проект: {title}")
                    break
            
            if not project_id and projects:
                project_id = projects[0].get("id")
                print(f"  ✓ Используем первый проект: {projects[0].get('title', 'N/A')}")
            
            if project_id:
                # Получаем список таблиц для этого проекта
                tables_url = f"{NOCODB_URL}/api/v1/db/meta/projects/{project_id}/tables"
                print(f"\nПолучение списка таблиц для проекта {project_id}...")
                response = requests.get(tables_url, headers=headers, timeout=30)
                if response.status_code == 200:
                    tables_data = response.json()
                    tables = tables_data.get("list", []) if isinstance(tables_data, dict) else tables_data
                    
                    print(f"Найдено таблиц: {len(tables)}")
                    for table in tables:
                        print(f"  - {table.get('title', table.get('table_name', 'N/A'))}")
                    
                    # Ищем таблицу "День 1"
                    target_table = None
                    for table in tables:
                        title = table.get("title") or table.get("table_name") or ""
                        if title == TABLE_NAME:
                            target_table = table
                            break
                    
                    if target_table:
                        table_id = target_table.get("id") or target_table.get("table_id")
                        print(f"\n✓ Найдена таблица '{TABLE_NAME}' с ID: {table_id}")
                        
                        # Получаем данные из таблицы
                        data_url = f"{NOCODB_URL}/api/v1/db/data/noco/{project_id}/{table_id}"
                        params = {"sort": "-Оценка"}
                        
                        print(f"Получение данных: {data_url}")
                        response = requests.get(data_url, headers=headers, params=params, timeout=30)
                        if response.status_code == 200:
                            data = response.json()
                            if isinstance(data, list):
                                records = data
                            elif isinstance(data, dict):
                                records = data.get("list", data.get("records", data.get("data", [])))
                            else:
                                records = []
                            
                            if records:
                                print(f"✓ Успешно получено {len(records)} записей!")
                                # Фильтруем и сортируем
                                filtered = filter_and_sort_records(records)
                                print(f"После фильтрации (с ФИО): {len(filtered)} записей")
                                return filtered
                        else:
                            print(f"Ошибка получения данных: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        print(f"Ошибка при получении проектов: {e}")
    
    # Сначала пробуем с токеном как параметром запроса (публичный API)
    for data_url in direct_data_urls:
        try:
            print(f"Попытка получить данные с токеном в параметрах: {data_url}")
            response = requests.get(data_url, params=params_with_token, timeout=30)
            print(f"Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                # Обрабатываем разные форматы ответа
                if isinstance(data, list):
                    records = data
                elif isinstance(data, dict):
                    records = data.get("list", data.get("records", data.get("data", [])))
                else:
                    records = []
                
                if records:
                    print(f"✓ Успешно получено {len(records)} записей напрямую!")
                    # Фильтруем и сортируем
                    filtered = filter_and_sort_records(records)
                    return filtered
            else:
                print(f"Статус {response.status_code}: {response.text[:200]}")
        except Exception as e:
            print(f"Ошибка: {e}")
            continue
    
    # Пробуем с заголовками
    for headers in headers_variants:
        for data_url in direct_data_urls:
            try:
                print(f"Попытка получить данные: {data_url}")
                print(f"Заголовки: {list(headers.keys())}")
                response = requests.get(data_url, headers=headers, params=params, timeout=30)
                print(f"Статус ответа: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    # Обрабатываем разные форматы ответа
                    if isinstance(data, list):
                        records = data
                    elif isinstance(data, dict):
                        records = data.get("list", data.get("records", data.get("data", [])))
                    else:
                        records = []
                    
                    if records:
                        print(f"✓ Успешно получено {len(records)} записей напрямую!")
                        # Сортируем вручную
                        try:
                            records = sorted(records, key=lambda x: float(x.get("Оценка", 0) or 0), reverse=True)
                        except (ValueError, TypeError):
                            pass
                        return records
                else:
                    print(f"Статус {response.status_code}: {response.text[:200]}")
            except Exception as e:
                print(f"Ошибка: {e}")
                continue
    
    # Если прямой доступ не сработал, пробуем через список таблиц
    print("\nПопытка получить список таблиц...")
    for headers in headers_variants:
        try:
            tables_url = f"{NOCODB_URL}/api/v1/db/meta/projects/{BASE_ID}/tables"
            print(f"Запрос списка таблиц: {tables_url}")
            response = requests.get(tables_url, headers=headers, timeout=30)
            print(f"Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                tables_data = response.json()
                
                # Обрабатываем разные форматы ответа
                if isinstance(tables_data, list):
                    tables = tables_data
                elif isinstance(tables_data, dict):
                    tables = tables_data.get("list", tables_data.get("tables", []))
                else:
                    tables = []
                
                print(f"Найдено таблиц: {len(tables)}")
                for table in tables:
                    print(f"  - {table.get('title', table.get('table_name', 'N/A'))}")
                
                # Ищем таблицу "День 1"
                target_table = None
                for table in tables:
                    title = table.get("title") or table.get("table_name") or ""
                    if title == TABLE_NAME:
                        target_table = table
                        break
                
                if not target_table:
                    raise Exception(f"Таблица '{TABLE_NAME}' не найдена. Доступные таблицы: {[t.get('title', t.get('table_name', 'N/A')) for t in tables]}")
                
                table_id = target_table.get("id") or target_table.get("table_id")
                if not table_id:
                    raise Exception("Не удалось получить ID таблицы")
                
                print(f"Найдена таблица '{TABLE_NAME}' с ID: {table_id}")
                
                # Получаем данные из таблицы
                data_urls = [
                    f"{NOCODB_URL}/api/v1/db/data/noco/{BASE_ID}/{table_id}",
                    f"{NOCODB_URL}/api/v2/tables/{table_id}/records",
                    f"{NOCODB_URL}/api/v1/db/data/{BASE_ID}/{table_id}",
                ]
                
                for data_url in data_urls:
                    try:
                        print(f"Попытка получить данные: {data_url}")
                        response = requests.get(data_url, headers=headers, params=params, timeout=30)
                        if response.status_code == 200:
                            data = response.json()
                            if isinstance(data, list):
                                records = data
                            elif isinstance(data, dict):
                                records = data.get("list", data.get("records", data.get("data", [])))
                            else:
                                records = []
                            
                            if records:
                                print(f"✓ Успешно получено {len(records)} записей!")
                                # Сортируем вручную
                                try:
                                    records = sorted(records, key=lambda x: float(x.get("Оценка", 0) or 0), reverse=True)
                                except (ValueError, TypeError):
                                    pass
                                return records
                        else:
                            print(f"Статус {response.status_code}: {response.text[:200]}")
                    except Exception as e:
                        print(f"Ошибка: {e}")
                        continue
                        
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Ответ сервера: {e.response.text}")
            continue
    
    raise Exception("Не удалось получить данные. Проверьте API токен и права доступа.")

def generate_html_rating_simple(data: List[Dict]) -> str:
    """
    Генерирует HTML код для Telegram Mini App в стиле iOS Dark Mode 2025
    """
    html = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#000000">
    <title>Рейтинг - День 1</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        :root {
            --tg-theme-bg-color: #000000;
            --tg-theme-text-color: #FFFFFF;
            --tg-theme-hint-color: #8E8E93;
            --tg-theme-link-color: #007AFF;
            --tg-theme-button-color: #007AFF;
            --tg-theme-button-text-color: #FFFFFF;
            --tg-theme-secondary-bg-color: #1C1C1E;
            
            --ios-bg-primary: #000000;
            --ios-bg-secondary: #1C1C1E;
            --ios-bg-tertiary: #2C2C2E;
            --ios-bg-elevated: #1C1C1E;
            --ios-separator: rgba(84, 84, 88, 0.65);
            --ios-text-primary: #FFFFFF;
            --ios-text-secondary: #8E8E93;
            --ios-text-tertiary: #48484A;
            --ios-accent: #0A84FF;
            --ios-green: #30D158;
            --ios-gold: #FFD60A;
            --ios-silver: #98989D;
            --ios-bronze: #AC8E68;
            
            --safe-area-inset-top: env(safe-area-inset-top, 0px);
            --safe-area-inset-bottom: env(safe-area-inset-bottom, 0px);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
            -webkit-touch-callout: none;
            -webkit-user-select: none;
            user-select: none;
        }
        
        html, body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', system-ui, sans-serif;
            background: var(--ios-bg-primary);
            color: var(--ios-text-primary);
            min-height: 100vh;
            min-height: 100dvh;
            overflow-x: hidden;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        
        body {
            padding-top: var(--safe-area-inset-top);
            padding-bottom: var(--safe-area-inset-bottom);
            background: linear-gradient(180deg, #0A0A0A 0%, #000000 100%);
        }
        
        .app-container {
            max-width: 100%;
            min-height: 100vh;
            min-height: 100dvh;
            display: flex;
            flex-direction: column;
        }
        
        /* Header with blur effect */
        .header {
            position: sticky;
            top: 0;
            z-index: 100;
            padding: 20px 16px 24px;
            background: rgba(0, 0, 0, 0.72);
            backdrop-filter: saturate(180%) blur(20px);
            -webkit-backdrop-filter: saturate(180%) blur(20px);
            border-bottom: 0.5px solid var(--ios-separator);
        }
        
        .header-content {
            text-align: center;
        }
        
        .header-icon {
            font-size: 48px;
            margin-bottom: 12px;
            display: block;
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-6px); }
        }
        
        .header-title {
            font-size: 28px;
            font-weight: 700;
            color: var(--ios-text-primary);
            letter-spacing: -0.5px;
            margin-bottom: 4px;
        }
        
        .header-subtitle {
            font-size: 15px;
            font-weight: 500;
            color: var(--ios-text-secondary);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }
        
        .header-subtitle::before {
            content: '';
            width: 8px;
            height: 8px;
            background: var(--ios-green);
            border-radius: 50%;
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(0.8); }
        }
        
        /* Main content */
        .content {
            flex: 1;
            padding: 16px;
        }
        
        /* Top 3 podium */
        .podium {
            display: flex;
            justify-content: center;
            align-items: flex-end;
            gap: 8px;
            margin-bottom: 24px;
            padding: 20px 8px 0;
        }
        
        .podium-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            flex: 1;
            max-width: 120px;
        }
        
        .podium-avatar {
            width: 64px;
            height: 64px;
            border-radius: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            margin-bottom: 8px;
            position: relative;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        }
        
        .podium-avatar::after {
            content: '';
            position: absolute;
            inset: -3px;
            border-radius: 35px;
            padding: 3px;
            background: linear-gradient(135deg, var(--glow-color) 0%, transparent 60%);
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
        }
        
        .podium-1 .podium-avatar {
            width: 80px;
            height: 80px;
            border-radius: 40px;
            font-size: 36px;
            background: linear-gradient(135deg, #FFD60A 0%, #FF9F0A 100%);
            --glow-color: #FFD60A;
            animation: glow-gold 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow-gold {
            from { box-shadow: 0 8px 24px rgba(255, 214, 10, 0.3); }
            to { box-shadow: 0 8px 32px rgba(255, 214, 10, 0.5); }
        }
        
        .podium-2 .podium-avatar {
            background: linear-gradient(135deg, #98989D 0%, #636366 100%);
            --glow-color: #98989D;
        }
        
        .podium-3 .podium-avatar {
            background: linear-gradient(135deg, #AC8E68 0%, #8B7355 100%);
            --glow-color: #AC8E68;
        }
        
        .podium-name {
            font-size: 13px;
            font-weight: 600;
            color: var(--ios-text-primary);
            text-align: center;
            margin-bottom: 4px;
            max-width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .podium-score {
            font-size: 15px;
            font-weight: 700;
            padding: 4px 12px;
            border-radius: 12px;
            background: var(--ios-bg-tertiary);
            color: var(--ios-accent);
        }
        
        .podium-1 .podium-score {
            background: rgba(255, 214, 10, 0.15);
            color: var(--ios-gold);
        }
        
        .podium-pedestal {
            width: 100%;
            margin-top: 12px;
            border-radius: 12px 12px 0 0;
            background: var(--ios-bg-secondary);
        }
        
        .podium-1 .podium-pedestal { height: 80px; background: linear-gradient(180deg, #2C2C2E 0%, #1C1C1E 100%); }
        .podium-2 .podium-pedestal { height: 60px; }
        .podium-3 .podium-pedestal { height: 40px; }
        
        /* Rating list */
        .rating-section {
            margin-top: 8px;
        }
        
        .section-title {
            font-size: 13px;
            font-weight: 600;
            color: var(--ios-text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 0 16px;
            margin-bottom: 8px;
        }
        
        .rating-list {
            background: var(--ios-bg-elevated);
            border-radius: 16px;
            overflow: hidden;
        }
        
        .rating-item {
            display: flex;
            align-items: center;
            padding: 14px 16px;
            gap: 12px;
            border-bottom: 0.5px solid var(--ios-separator);
            transition: background-color 0.15s ease;
            animation: slideIn 0.4s ease-out backwards;
        }
        
        .rating-item:last-child {
            border-bottom: none;
        }
        
        .rating-item:active {
            background: var(--ios-bg-tertiary);
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .rank-number {
            width: 32px;
            height: 32px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 15px;
            font-weight: 600;
            background: var(--ios-bg-tertiary);
            color: var(--ios-text-secondary);
            flex-shrink: 0;
        }
        
        .user-info {
            flex: 1;
            min-width: 0;
        }
        
        .user-name {
            font-size: 17px;
            font-weight: 500;
            color: var(--ios-text-primary);
            line-height: 1.3;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .score-pill {
            display: flex;
            align-items: center;
            gap: 4px;
            padding: 6px 12px;
            border-radius: 20px;
            background: rgba(10, 132, 255, 0.15);
            flex-shrink: 0;
        }
        
        .score-value {
            font-size: 17px;
            font-weight: 700;
            color: var(--ios-accent);
        }
        
        .score-label {
            font-size: 13px;
            color: var(--ios-text-secondary);
        }
        
        .score-high .score-pill {
            background: rgba(48, 209, 88, 0.15);
        }
        .score-high .score-value {
            color: var(--ios-green);
        }
        
        .score-medium .score-pill {
            background: rgba(10, 132, 255, 0.15);
        }
        
        .score-low .score-pill {
            background: var(--ios-bg-tertiary);
        }
        .score-low .score-value {
            color: var(--ios-text-secondary);
        }
        
        /* Empty state */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: var(--ios-text-secondary);
        }
        
        .empty-state-icon {
            font-size: 64px;
            margin-bottom: 16px;
            opacity: 0.5;
        }
        
        /* Footer */
        .footer {
            padding: 24px 16px;
            text-align: center;
        }
        
        .footer-text {
            font-size: 13px;
            color: var(--ios-text-tertiary);
        }
        
        .update-time {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            background: var(--ios-bg-secondary);
            border-radius: 20px;
            font-size: 13px;
            color: var(--ios-text-secondary);
        }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="header">
            <div class="header-content">
                <span class="header-icon">🏆</span>
                <h1 class="header-title">Рейтинг</h1>
                <div class="header-subtitle">День 1 • Марафон</div>
            </div>
        </div>
        
        <div class="content">
"""
    
    # Подготавливаем данные
    processed_data = []
    for row in data:
        fio = get_fio_from_record(row)
        score = (row.get("Оценка") or row.get("оценка") or row.get("score") or "")
        if not score:
            for key, value in row.items():
                if "оценка" in key.lower() or "score" in key.lower():
                    score = value or score
                    if score:
                        break
        score = str(score).strip() if score else "0"
        if fio:
            processed_data.append({"fio": fio, "score": score})
    
    # Генерируем подиум для топ-3
    if len(processed_data) >= 3:
        # Порядок для подиума: 2, 1, 3 (серебро, золото, бронза)
        top3 = [processed_data[1], processed_data[0], processed_data[2]]  # 2nd, 1st, 3rd
        positions = [2, 1, 3]
        medals = ["🥈", "🥇", "🥉"]
        
        html += """
            <div class="podium">
"""
        for i, (item, pos, medal) in enumerate(zip(top3, positions, medals)):
            name_parts = item["fio"].split()
            short_name = name_parts[0] if name_parts else item["fio"]
            if len(name_parts) > 1:
                short_name += " " + name_parts[1][0] + "."
            
            html += f"""
                <div class="podium-item podium-{pos}" style="animation-delay: {0.1 * (i+1)}s;">
                    <div class="podium-avatar">{medal}</div>
                    <div class="podium-name">{short_name}</div>
                    <div class="podium-score">{item["score"]} ⭐</div>
                    <div class="podium-pedestal"></div>
                </div>
"""
        html += """
            </div>
"""
    
    # Генерируем остальной список (начиная с 4-го места)
    remaining_data = processed_data[3:] if len(processed_data) > 3 else processed_data
    start_index = 4 if len(processed_data) > 3 else 1
    
    if remaining_data:
        html += """
            <div class="rating-section">
                <div class="section-title">Остальные участники</div>
                <div class="rating-list">
"""
        
        for index, item in enumerate(remaining_data, start_index):
            try:
                score_num = float(item["score"])
                if score_num >= 4:
                    score_class = "score-high"
                elif score_num >= 2:
                    score_class = "score-medium"
                else:
                    score_class = "score-low"
            except:
                score_class = "score-low"
            
            html += f"""
                    <div class="rating-item {score_class}" style="animation-delay: {0.05 * index}s;">
                        <div class="rank-number">{index}</div>
                        <div class="user-info">
                            <div class="user-name">{item["fio"]}</div>
                        </div>
                        <div class="score-pill">
                            <span class="score-value">{item["score"]}</span>
                            <span class="score-label">баллов</span>
                        </div>
                    </div>
"""
        
        html += """
                </div>
            </div>
"""
    
    # Футер
    from datetime import datetime
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    html += f"""
        </div>
        
        <div class="footer">
            <div class="update-time">
                <span>🔄</span>
                <span>Обновлено: {now}</span>
            </div>
        </div>
    </div>
    
    <script>
        // Telegram WebApp integration
        if (window.Telegram && window.Telegram.WebApp) {{
            const tg = window.Telegram.WebApp;
            tg.ready();
            tg.expand();
            
            // Apply Telegram theme colors
            document.documentElement.style.setProperty('--tg-theme-bg-color', tg.themeParams.bg_color || '#000000');
            document.documentElement.style.setProperty('--tg-theme-text-color', tg.themeParams.text_color || '#FFFFFF');
            document.documentElement.style.setProperty('--tg-theme-hint-color', tg.themeParams.hint_color || '#8E8E93');
            document.documentElement.style.setProperty('--tg-theme-link-color', tg.themeParams.link_color || '#007AFF');
            document.documentElement.style.setProperty('--tg-theme-button-color', tg.themeParams.button_color || '#007AFF');
            document.documentElement.style.setProperty('--tg-theme-secondary-bg-color', tg.themeParams.secondary_bg_color || '#1C1C1E');
        }}
    </script>
</body>
</html>
"""
    
    return html

def generate_html_rating(data: List[Dict]) -> str:
    """
    Генерирует HTML код для рейтинга
    """
    html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Рейтинг сотрудников</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #06A478 0%, #048a63 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }
        .table-wrapper {
            padding: 20px;
            overflow-x: auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 0;
        }
        thead {
            background: #f8f9fa;
        }
        th {
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #06A478;
            font-size: 16px;
        }
        td {
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
            color: #495057;
        }
        tbody tr:hover {
            background: #f8f9fa;
            transition: background 0.2s;
        }
        tbody tr:last-child td {
            border-bottom: none;
        }
        .rank {
            font-weight: 600;
            color: #06A478;
            width: 50px;
            text-align: center;
        }
        .score {
            font-weight: 600;
            color: #667eea;
            text-align: center;
        }
        .medal {
            display: inline-block;
            margin-right: 8px;
        }
        .gold { color: #FFD700; }
        .silver { color: #C0C0C0; }
        .bronze { color: #CD7F32; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏆 Рейтинг сотрудников - День 1</h1>
        </div>
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th style="width: 60px;">Место</th>
                        <th>ФИО сотрудника</th>
                        <th style="width: 120px; text-align: center;">Оценка</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Добавляем строки с данными
    for index, row in enumerate(data, 1):
        # Используем функцию для извлечения ФИО (строго из правильного столбца)
        fio = get_fio_from_record(row)
        
        # Получаем оценку
        score = (row.get("Оценка") or 
                row.get("оценка") or 
                row.get("score") or 
                row.get("Score") or 
                row.get("rating") or 
                "")
        
        # Если оценка не найдена, ищем по ключам
        if not score:
            for key, value in row.items():
                key_lower = key.lower()
                if "оценка" in key_lower or "score" in key_lower or "rating" in key_lower:
                    score = value or score
                    if score:
                        break
        
        # Очищаем значения
        if score:
            score = str(score).strip()
        else:
            score = "0"
        
        # Определяем медаль для первых трёх мест
        medal_emoji = ""
        if index == 1:
            medal_emoji = '<span class="medal gold">🥇</span>'
        elif index == 2:
            medal_emoji = '<span class="medal silver">🥈</span>'
        elif index == 3:
            medal_emoji = '<span class="medal bronze">🥉</span>'
        
        html += f"""
                    <tr>
                        <td class="rank">{medal_emoji} {index}</td>
                        <td>{fio}</td>
                        <td class="score">{score}</td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main():
    """
    Основная функция
    """
    print("Получение данных из NocoDB...")
    try:
        data = get_table_data()
        print(f"Получено {len(data)} записей")
        
        if not data:
            print("Данные не найдены")
            return
        
        print("Генерация HTML...")
        html = generate_html_rating(data)
        html_simple = generate_html_rating_simple(data)
        
        # Сохраняем полный HTML файл
        output_file = "rating.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        
        # Сохраняем упрощённый HTML для PuzzleBot
        output_file_simple = "rating_puzzlebot.html"
        with open(output_file_simple, "w", encoding="utf-8") as f:
            f.write(html_simple)
        
        print(f"HTML файл сохранен: {output_file}")
        print(f"Упрощённый HTML для PuzzleBot сохранен: {output_file_simple}")
        print("\nДанные для проверки (первые 5 записей):")
        for i, row in enumerate(data[:5], 1):
            fio = row.get('ФИО сотрудника') or row.get('ФИО') or row.get('fio') or 'N/A'
            score = row.get('Оценка') or row.get('оценка') or row.get('score') or 'N/A'
            print(f"{i}. {fio} - {score}")
        
        print(f"\nВсего записей в рейтинге: {len(data)}")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

