# Деплой на Vercel

## Быстрый старт

1. **Установите Vercel CLI** (если еще не установлен):
   ```bash
   npm i -g vercel
   ```

2. **Войдите в Vercel**:
   ```bash
   vercel login
   ```

3. **Настройте переменные окружения**:
   - Перейдите в настройки проекта на Vercel
   - Добавьте переменные:
     - `NOCODB_URL` = `https://nocodb.puzzlebot.top`
     - `NOCODB_API_TOKEN` = `avKy8Ov_rNMIRMf-hgneulQKWsrXMhqmdqfc6uR1`

4. **Деплой**:
   ```bash
   vercel
   ```

   Или для production:
   ```bash
   vercel --prod
   ```

## Через GitHub

1. **Создайте репозиторий на GitHub** и загрузите код

2. **Подключите к Vercel**:
   - Зайдите на [vercel.com](https://vercel.com)
   - Нажмите "New Project"
   - Импортируйте ваш GitHub репозиторий
   - Добавьте переменные окружения в настройках проекта
   - Нажмите "Deploy"

## Структура проекта

```
├── api/
│   └── rating.js          # Serverless function для получения данных
├── index.html             # Главная страница
├── vercel.json            # Конфигурация Vercel
├── package.json           # Зависимости проекта
└── .env.example           # Пример переменных окружения
```

## API Endpoint

После деплоя будет доступен endpoint:
- `https://your-project.vercel.app/api/rating`

## Переменные окружения

В настройках проекта Vercel добавьте:
- `NOCODB_URL` - URL вашего NocoDB
- `NOCODB_API_TOKEN` - API токен для доступа к NocoDB

## Обновление

После каждого push в GitHub, Vercel автоматически пересоберёт и задеплоит проект.

