# 🚀 Деплой на Vercel

## Вариант 1: Через Vercel CLI

```bash
# 1. Установите Vercel CLI
npm i -g vercel

# 2. Войдите в аккаунт
vercel login

# 3. Деплой
vercel

# 4. Для production
vercel --prod
```

## Вариант 2: Через GitHub (Рекомендуется)

1. **Создайте репозиторий на GitHub**
2. **Загрузите код:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-username/your-repo.git
   git push -u origin main
   ```

3. **Подключите к Vercel:**
   - Зайдите на [vercel.com](https://vercel.com)
   - Нажмите **"New Project"**
   - Импортируйте ваш GitHub репозиторий
   - В настройках проекта добавьте **Environment Variables**:
     ```
     NOCODB_URL = https://nocodb.puzzlebot.top
     NOCODB_API_TOKEN = avKy8Ov_rNMIRMf-hgneulQKWsrXMhqmdqfc6uR1
     ```
   - Нажмите **"Deploy"**

## 📝 Важные файлы

- `index.html` - главная страница (динамически загружает данные)
- `api/rating.js` - serverless function для получения данных из NocoDB
- `vercel.json` - конфигурация Vercel

## 🔗 После деплоя

Ваш сайт будет доступен по адресу:
- `https://your-project.vercel.app`

API endpoint:
- `https://your-project.vercel.app/api/rating`

## 🔄 Автообновление

После каждого push в GitHub, Vercel автоматически пересоберёт проект.

## ⚙️ Переменные окружения

Убедитесь, что в настройках проекта Vercel добавлены:
- `NOCODB_URL`
- `NOCODB_API_TOKEN`

