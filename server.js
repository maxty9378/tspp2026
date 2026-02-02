const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 8080;
const mime = {
  html: 'text/html',
  js: 'text/javascript',
  json: 'application/json',
  png: 'image/png',
  jpg: 'image/jpeg',
  gif: 'image/gif',
  ico: 'image/x-icon',
  css: 'text/css',
  svg: 'image/svg+xml',
  tgs: 'application/octet-stream',
  otf: 'font/otf'
};

const ratingHandler = require('./api/rating.js');

const server = http.createServer(async (req, res) => {
  const urlPath = req.url.replace(/\?.*$/, '');

  // Локальный API рейтинга (тот же код, что на Vercel)
  if (urlPath === '/api/rating' && req.method === 'GET') {
    const mockReq = { method: 'GET', url: req.url };
    const mockRes = {
      _headers: {},
      _status: 200,
      _body: null,
      setHeader(k, v) { this._headers[k] = v; },
      status(code) { this._status = code; return this; },
      json(data) { this._body = data; return this; },
      end() {}
    };
    try {
      await ratingHandler(mockReq, mockRes);
      res.writeHead(mockRes._status, { ...mockRes._headers, 'Content-Type': 'application/json' });
      res.end(JSON.stringify(mockRes._body));
    } catch (e) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: e.message }));
    }
    return;
  }

  let filePath = req.url === '/' ? '/index.html' : req.url;
  filePath = path.join(__dirname, filePath.replace(/^\//, '').replace(/\?.*$/, ''));

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end('Not found');
      return;
    }
    const ext = path.extname(filePath).slice(1);
    res.writeHead(200, { 'Content-Type': mime[ext] || 'application/octet-stream' });
    res.end(data);
  });
});

server.listen(PORT, () => {
  console.log('Сервер: http://localhost:' + PORT);
  console.log('Рейтинг: http://localhost:' + PORT + '/rating_puzzlebot.html');
});
