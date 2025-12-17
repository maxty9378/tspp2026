// API endpoint для получения данных рейтинга из NocoDB
const NOCODB_URL = process.env.NOCODB_URL || "https://nocodb.puzzlebot.top";
const API_TOKEN = process.env.NOCODB_API_TOKEN || "avKy8Ov_rNMIRMf-hgneulQKWsrXMhqmdqfc6uR1";
const TABLE_NAME = "День 1";

// Функция для извлечения ФИО из записи
function getFioFromRecord(record) {
  const excludedKeywords = ["тренер", "trainer", "coach", "наставник", "преподаватель"];
  
  // Сначала пробуем точные совпадения
  let fio = record["ФИО сотрудника"] || record["ФИО сотрудника"];
  
  // Если не нашли, ищем по ключам
  if (!fio) {
    for (const [key, value] of Object.entries(record)) {
      const keyLower = key.toLowerCase();
      const isExcluded = excludedKeywords.some(excluded => keyLower.includes(excluded));
      
      if (!isExcluded && (keyLower.includes("фио") || keyLower.includes("fio"))) {
        if (keyLower.includes("сотрудник") || keyLower.includes("employee") || 
            keyLower === "фио" || keyLower === "fio") {
          fio = value || fio;
          if (fio) break;
        }
      }
    }
  }
  
  return fio ? String(fio).trim() : "";
}

// Функция для фильтрации и сортировки записей
function filterAndSortRecords(records) {
  const filtered = records
    .map(record => {
      const fio = getFioFromRecord(record);
      let score = record["Оценка"] || record["оценка"] || record["score"] || "";
      
      if (!score) {
        for (const [key, value] of Object.entries(record)) {
          const keyLower = key.toLowerCase();
          if (keyLower.includes("оценка") || keyLower.includes("score") || keyLower.includes("rating")) {
            score = value || score;
            if (score) break;
          }
        }
      }
      
      return { fio, score: String(score || "0").trim(), original: record };
    })
    .filter(item => item.fio)
    .sort((a, b) => {
      const scoreA = parseFloat(a.score) || 0;
      const scoreB = parseFloat(b.score) || 0;
      return scoreB - scoreA;
    });
  
  return filtered;
}

export default async function handler(req, res) {
  try {
    // CORS headers для Telegram Mini App
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Content-Type', 'application/json');
    
    if (req.method === 'OPTIONS') {
      return res.status(200).end();
    }
    
    if (req.method !== 'GET') {
      return res.status(405).json({ 
        success: false,
        error: 'Method not allowed',
        timestamp: new Date().toISOString()
      });
    }
    
    const headers = {
      "xc-token": API_TOKEN,
      "Content-Type": "application/json"
    };
    
    // Получаем список проектов
    const projectsUrl = `${NOCODB_URL}/api/v1/db/meta/projects`;
    const projectsResponse = await fetch(projectsUrl, { headers });
    
    if (!projectsResponse.ok) {
      throw new Error(`Failed to fetch projects: ${projectsResponse.status}`);
    }
    
    const projectsData = await projectsResponse.json();
    const projects = projectsData.list || [];
    
    // Ищем проект "Телеграм приложение"
    let projectId = null;
    for (const proj of projects) {
      const title = (proj.title || "").toLowerCase();
      if (title.includes("телеграм") || title.includes("telegram")) {
        projectId = proj.id;
        break;
      }
    }
    
    if (!projectId && projects.length > 0) {
      projectId = projects[0].id;
    }
    
    if (!projectId) {
      throw new Error("Project not found");
    }
    
    // Получаем список таблиц
    const tablesUrl = `${NOCODB_URL}/api/v1/db/meta/projects/${projectId}/tables`;
    const tablesResponse = await fetch(tablesUrl, { headers });
    
    if (!tablesResponse.ok) {
      throw new Error(`Failed to fetch tables: ${tablesResponse.status}`);
    }
    
    const tablesData = await tablesResponse.json();
    const tables = tablesData.list || [];
    
    // Ищем таблицу "День 1"
    let tableId = null;
    for (const table of tables) {
      if (table.title === TABLE_NAME) {
        tableId = table.id;
        break;
      }
    }
    
    if (!tableId) {
      throw new Error(`Table "${TABLE_NAME}" not found`);
    }
    
    // Получаем данные из таблицы
    const dataUrl = `${NOCODB_URL}/api/v1/db/data/noco/${projectId}/${tableId}?sort=-Оценка`;
    const dataResponse = await fetch(dataUrl, { headers });
    
    if (!dataResponse.ok) {
      throw new Error(`Failed to fetch data: ${dataResponse.status}`);
    }
    
    const data = await dataResponse.json();
    const records = data.list || [];
    
    // Фильтруем и сортируем
    const processedData = filterAndSortRecords(records);
    
    return res.status(200).json({
      success: true,
      data: processedData,
      count: processedData.length,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('Error:', error);
    return res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
}
