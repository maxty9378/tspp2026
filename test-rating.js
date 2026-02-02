/**
 * Тест API рейтинга: баллы только из "Сумма баллов за марафон".
 * Проверяет, что Кадочкин Максим имеет 12 баллов.
 */

const API_URL = process.env.API_URL || 'https://tspp2026.vercel.app/api/rating';

async function fetchRating() {
  const res = await fetch(API_URL);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function runTest() {
  return fetchRating().then((body) => {
    if (!body.success) throw new Error(body.error || 'API вернул success: false');
    const data = body.data || [];
    const kad = data.find((r) => (r.fio || '').includes('Кадочкин') && (r.fio || '').includes('Максим'));
    if (!kad) throw new Error('В рейтинге не найден Кадочкин Максим');
    if (Number(kad.score) !== 12) {
      throw new Error(`Ожидалось 12 баллов у Кадочкин Максим, получено: ${kad.score}`);
    }
    return { ok: true, data, kad };
  });
}

runTest()
  .then(({ ok, data, kad }) => {
    console.log('OK: API рейтинг загружен, записей:', data.length);
    console.log('OK: Кадочкин Максим найден, баллы (Сумма баллов за марафон):', kad.score);
    process.exit(0);
  })
  .catch((err) => {
    console.error('ТЕСТ НЕ ПРОЙДЕН:', err.message);
    process.exit(1);
  });
