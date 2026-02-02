/**
 * Локальный тест: вызывает обработчик api/rating.js напрямую.
 * Баллы только из "Сумма баллов за марафон". Кадочкин Максим = 12.
 */

const handler = require('./api/rating.js');

const req = {
  method: 'GET',
  url: '/api/rating'
};

const res = {
  _status: 200,
  _body: null,
  setHeader() {},
  status(code) {
    this._status = code;
    return this;
  },
  json(data) {
    this._body = data;
    return this;
  },
  end() {}
};

handler(req, res)
  .then(() => {
    if (res._status !== 200) throw new Error(`status ${res._status}`);
    const body = res._body;
    if (!body || !body.success) throw new Error(body?.error || 'success: false');
    const data = body.data || [];
    const kad = data.find((r) => (r.fio || '').includes('Кадочкин') && (r.fio || '').includes('Максим'));
    if (!kad) throw new Error('В рейтинге не найден Кадочкин Максим');
    const score = Number(kad.score);
    if (score !== 12) throw new Error(`Ожидалось 12 баллов у Кадочкин Максим, получено: ${kad.score}`);
    console.log('OK: API рейтинг (локально), записей:', data.length);
    console.log('OK: Кадочкин Максим найден, баллы (Сумма баллов за марафон):', kad.score);
    process.exit(0);
  })
  .catch((err) => {
    console.error('ТЕСТ НЕ ПРОЙДЕН:', err.message);
    process.exit(1);
  });
