import time
import threading
import requests
import yaml
from flask import Flask
from mcstatus import JavaServer

# Создаем мини-сайт для обхода ограничений Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот мониторинга активен!", 200

CONFIG_PATH = 'config.yml'

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_server_data(ip):
    try:
        server = JavaServer.lookup(ip)
        status = server.status()
        return {
            'status': 'online',
            'online': str(status.players.online),
            'max': str(status.players.max),
            'players': ", ".join([p.name for p in status.players.sample]) if status.players.sample else "Никого нет"
        }
    except Exception:
        return {'status': 'offline'}

def update_telegram():
    config = load_config()
    token = config['token']
    monitoring = config['channel-monitoring']
    if not monitoring['enabled']: return

    chat_id = monitoring['chat-id']
    message_id = monitoring['message-id']
    ip = "vividness-stuff.gl.joinmc.link"

    data = get_server_data(ip)

    if data['status'] == 'online':
        text = config['messages']['online'].replace('%online%', data['online']).replace('%max%', data['max']).replace('%players%', data['players'])
    else:
        text = config['messages']['offline']

    url = f"https://telegram.org{token}/editMessageText"
    try:
        requests.post(url, json={"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Ошибка сети: {e}")

def run_monitoring():
    print("Цикл мониторинга запущен!")
    while True:
        try:
            config = load_config()
            update_telegram()
            time.sleep(config['channel-monitoring']['update-interval'])
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(10)

if __name__ == "__main__":
    # Запуск мониторинга в отдельном потоке
    threading.Thread(target=run_monitoring, daemon=True).start()
    # Запуск веб-сервера на порту, который требует Render
    app.run(host='0.0.0.0', port=10000)
