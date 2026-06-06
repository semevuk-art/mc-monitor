import time
import requests
import yaml
from mcstatus import JavaServer

CONFIG_PATH = 'config.yml'

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_server_data(ip):
    try:
        server = JavaServer.lookup(ip)
        status = server.status()
        online = status.players.online
        maximum = status.players.max
        
        if status.players.sample:
            players_list = ", ".join([p.name for p in status.players.sample])
        else:
            players_list = "Никого нет"
            
        return {
            'status': 'online',
            'online': str(online),
            'max': str(maximum),
            'players': players_list
        }
    except Exception:
        return {'status': 'offline'}

def update_telegram():
    config = load_config()
    token = config['token']
    monitoring = config['channel-monitoring']
    
    if not monitoring['enabled']:
        return

    chat_id = monitoring['chat-id']
    message_id = monitoring['message-id']
    ip = "vividness-stuff.gl.joinmc.link"
    
    data = get_server_data(ip)
    
    if data['status'] == 'online':
        text = config['messages']['online']
        text = text.replace('%online%', data['online'])
        text = text.replace('%max%', data['max'])
        text = text.replace('%players%', data['players'])
    else:
        text = config['messages']['offline']
        
    url = f"https://telegram.org{token}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload).json()
        if not response.get("ok"):
            print(f"Ошибка Telegram API: {response.get('description')}")
    except Exception as e:
        print(f"Ошибка сети: {e}")

if __name__ == "__main__":
    print("Мониторинг успешно запущен на Render!")
    while True:
        try:
            config = load_config()
            interval = config['channel-monitoring']['update-interval']
            update_telegram()
            time.sleep(interval)
        except Exception as e:
            print(f"Критическая ошибка цикла: {e}")
            time.sleep(10)
