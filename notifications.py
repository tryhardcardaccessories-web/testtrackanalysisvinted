"""Notifications Telegram optionnelles.

Configurer TELEGRAM_BOT_TOKEN et TELEGRAM_CHAT_ID dans les secrets Streamlit
ou les variables d'environnement. Aucun message n'est envoyé sans configuration.
"""
import os
import requests

def send_telegram(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False, "Telegram non configuré."
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={"chat_id": chat_id, "text": message},
        timeout=15
    )
    response.raise_for_status()
    return True, "Message envoyé."
