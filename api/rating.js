const https = require('https');

const NOCODB_URL = process.env.NOCODB_URL || "https://nocodb.puzzlebot.top";
const API_TOKEN = process.env.NOCODB_API_TOKEN || "avKy8Ov_rNMIRMf-hgneulQKWsrXMhqmdqfc6uR1";

function httpsGet(url, headers) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const options = {
      hostname: urlObj.hostname,
      port: 443,
      path: urlObj.pathname + urlObj.search,
      method: 'GET',
      headers: headers
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve({ ok: res.statusCode < 400, status: res.statusCode, data: JSON.parse(data) });
        } catch (e) {
          resolve({ ok: false, status: res.statusCode, data: null, error: data });
        }
      });
    });

    req.on('error', reject);
    req.setTimeout(25000, () => { req.destroy(); reject(new Error('Timeout')); });
    req.end();
  });
}

module.exports = async (req, res) => {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Content-Type', 'application/json');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    const headers = { "xc-token": API_TOKEN };

    // 1. Получаем проекты
    const projRes = await httpsGet(`${NOCODB_URL}/api/v1/db/meta/projects`, headers);
    if (!projRes.ok) throw new Error(`Projects: ${projRes.status}`);
    
    const projects = projRes.data.list || [];
    let projectId = null;
    for (const p of projects) {
      if ((p.title || '').toLowerCase().includes('телеграм')) {
        projectId = p.id;
        break;
      }
    }
    if (!projectId && projects.length > 0) projectId = projects[0].id;
    if (!projectId) throw new Error('No project found');

    // 2. Получаем таблицы
    const tabRes = await httpsGet(`${NOCODB_URL}/api/v1/db/meta/projects/${projectId}/tables`, headers);
    if (!tabRes.ok) throw new Error(`Tables: ${tabRes.status}`);
    
    const tables = tabRes.data.list || [];
    let tableId = null;
    for (const t of tables) {
      if (t.title === 'День 1') {
        tableId = t.id;
        break;
      }
    }
    if (!tableId) throw new Error('Table "День 1" not found');

    // 3. Получаем данные из таблицы "Сотрудники" для филиалов
    const filialMap = {};
    let empTableId = null;
    for (const t of tables) {
      if (t.title === 'Сотрудники') {
        empTableId = t.id;
        break;
      }
    }
    
    if (empTableId) {
      try {
        const empRes = await httpsGet(`${NOCODB_URL}/api/v1/db/data/noco/${projectId}/${empTableId}`, headers);
        if (empRes.ok && empRes.data) {
          const employees = empRes.data.list || [];
          employees.forEach(emp => {
            const fio = emp['ФИО сотрудника'] || emp['ФИО'] || '';
            const filial = emp['Филиал сотрудника'] || emp['Филиал'] || '';
            if (fio && filial) {
              filialMap[String(fio).trim()] = String(filial).trim();
            }
          });
        }
      } catch (e) {
        console.warn('Не удалось загрузить филиалы:', e.message);
      }
    }

    // 4. Получаем данные
    const dataRes = await httpsGet(`${NOCODB_URL}/api/v1/db/data/noco/${projectId}/${tableId}`, headers);
    if (!dataRes.ok) throw new Error(`Data: ${dataRes.status}`);
    
    const records = dataRes.data.list || [];
    
    // 5. Обрабатываем данные
    const result = records
      .map(r => {
        let fio = r['ФИО сотрудника'] || '';
        if (!fio) {
          for (const k of Object.keys(r)) {
            if (k.toLowerCase().includes('фио') && !k.toLowerCase().includes('тренер')) {
              fio = r[k] || '';
              if (fio) break;
            }
          }
        }
        fio = String(fio).trim();
        const filial = filialMap[fio] || '';
        const score = parseFloat(r['Оценка'] || r['оценка'] || 0) || 0;
        // Табельный номер
        const tabNomer = r['Табельный номер (tab_nomer)'] || r['tab_nomer'] || r['Табельный номер'] || '';
        return { fio, filial, score, tabNomer: String(tabNomer).trim() };
      })
      .filter(x => x.fio)
      .sort((a, b) => b.score - a.score);

    return res.status(200).json({ success: true, data: result, count: result.length });

  } catch (error) {
    console.error('API Error:', error.message);
    return res.status(500).json({ success: false, error: error.message });
  }
};
