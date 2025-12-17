"""
Скрипт для получения информации о правильном API endpoint из NocoDB
"""
import requests

NOCODB_URL = "https://nocodb.puzzlebot.top"
API_TOKEN = "avKy8Ov_rNMIRMf-hgneulQKWsrXMhqmdqfc6uR1"

print("Проверка различных вариантов API endpoints...\n")

# Варианты заголовков
headers_variants = [
    {"xc-token": API_TOKEN},
    {"xc-auth": API_TOKEN},
    {"Authorization": f"Bearer {API_TOKEN}"},
]

# Пробуем получить информацию о проектах
print("1. Попытка получить список проектов:")
for headers in headers_variants:
    try:
        url = f"{NOCODB_URL}/api/v1/db/meta/projects"
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   URL: {url}")
        print(f"   Заголовки: {list(headers.keys())}")
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Успешно! Данные: {data}")
            break
        else:
            print(f"   Ответ: {response.text[:200]}")
    except Exception as e:
        print(f"   Ошибка: {e}")

print("\n2. Попытка получить информацию о workspace:")
for headers in headers_variants:
    try:
        url = f"{NOCODB_URL}/api/v1/db/meta/workspaces"
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   URL: {url}")
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Успешно! Данные: {data}")
            break
    except Exception as e:
        print(f"   Ошибка: {e}")

print("\n3. Попытка использовать токен как публичный API ключ:")
# В NocoDB публичные API ключи могут работать через специальный endpoint
try:
    # Пробуем получить данные через публичный API
    url = f"{NOCODB_URL}/api/v1/db/data/noco/public/День 1"
    params = {"token": API_TOKEN}
    response = requests.get(url, params=params, timeout=10)
    print(f"   URL: {url}")
    print(f"   Статус: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✓ Успешно!")
    else:
        print(f"   Ответ: {response.text[:200]}")
except Exception as e:
    print(f"   Ошибка: {e}")

print("\n" + "="*60)
print("ИНСТРУКЦИЯ:")
print("="*60)
print("""
Для получения правильного API endpoint:

1. Откройте NocoDB в браузере
2. Перейдите в настройки таблицы "День 1"
3. Найдите раздел "API" или "Share" (Поделиться)
4. Скопируйте API endpoint или публичный URL
5. Проверьте формат токена - возможно это публичный API ключ

Альтернативно:
- Проверьте документацию NocoDB для вашей версии
- Используйте браузерную консоль (F12) для просмотра сетевых запросов
  при открытии таблицы в NocoDB
""")

