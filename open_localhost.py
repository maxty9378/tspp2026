"""
Скрипт для открытия HTML файлов на localhost
"""
import webbrowser
import http.server
import socketserver
import threading
import os

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def start_server():
    """Запускает HTTP сервер"""
    handler = MyHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Сервер запущен на http://localhost:{PORT}")
        print(f"Откройте в браузере:")
        print(f"  - Полная версия: http://localhost:{PORT}/rating.html")
        print(f"  - Версия для PuzzleBot: http://localhost:{PORT}/rating_puzzlebot.html")
        print("\nНажмите Ctrl+C для остановки сервера")
        httpd.serve_forever()

if __name__ == "__main__":
    # Проверяем наличие HTML файлов
    if not os.path.exists("rating.html"):
        print("Ошибка: файл rating.html не найден!")
        print("Сначала запустите: python get_rating.py")
        exit(1)
    
    # Запускаем сервер в отдельном потоке
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Открываем браузер через 1 секунду
    import time
    time.sleep(1)
    
    print("\nОткрываю браузер...")
    webbrowser.open(f"http://localhost:{PORT}/rating_puzzlebot.html")
    
    # Ждём, пока пользователь не остановит сервер
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nСервер остановлен.")

