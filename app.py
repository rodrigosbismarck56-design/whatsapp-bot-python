import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Récupération des variables d'environnement
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "mon_secret_123")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "1193134093891632")

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # 1. Validation du Webhook par Meta (GET)
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return str(challenge), 200
        return "Échec de vérification", 403

    # 2. Réception des messages WhatsApp (POST)
    elif request.method == 'POST':
        data = request.get_json()
        try:
            entries = data.get('entry', [])
            for entry in entries:
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    messages = value.get('messages', [])
                    if messages:
                        msg = messages[0]
                        sender_id = msg.get('from')
                        if msg.get('type') == 'text':
                            text = msg.get('text', {}).get('body', '')
                            reply = generate_response(text)
                            send_whatsapp_message(sender_id, reply)
        except Exception as e:
            print(f"Erreur : {e}")

        return jsonify({"status": "success"}), 200

def generate_response(user_text):
    t = user_text.lower().strip()
    if "bonjour" in t or "salut" in t:
        return "Bonjour ! Comment puis-je vous aider aujourd'hui ?"
    elif "tarif" in t or "prix" in t:
        return "Nos services commencent à partir de $50."
    return f"Merci ! Message reçu : '{user_text}'."

def send_whatsapp_message(recipient_id, text):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, json=payload, headers=headers)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
