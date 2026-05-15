"""Alert System - Sends notifications"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from datetime import datetime
from typing import Dict
import config


class AlertSystem:
    """Sends alerts via Email/Telegram"""

    def __init__(self):
        self.telegram_token = config.TELEGRAM_BOT_TOKEN
        self.telegram_chat = config.TELEGRAM_CHAT_ID
        self.email_sender = config.EMAIL_SENDER
        self.email_pass = config.EMAIL_PASSWORD
        self.email_receiver = config.EMAIL_RECEIVER

    def send_telegram(self, message: str) -> bool:
        """Send Telegram message"""
        if not self.telegram_token:
            self._print(message)
            return False

        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            r = requests.post(url, data={"chat_id": self.telegram_chat, "text": message}, timeout=10)
            return r.status_code == 200
        except:
            return False

    def send_email(self, subject: str, body: str) -> bool:
        """Send email"""
        if not self.email_sender:
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_sender
            msg["To"] = self.email_receiver
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
                server.starttls()
                server.login(self.email_sender, self.email_pass)
                server.send_message(msg)
            return True
        except:
            return False

    def send_signal(self, signal: Dict):
        """Send signal alert"""
        msg = f"""
🎯 SIGNAL: {signal.get('signal_status')}

{signal.get('symbol')} - {signal.get('name', '')}
Setup: {signal.get('setup_type')}
Score: {signal.get('signal_score')}/100

Entry: ${signal.get('ideal_entry', 0):.2f}
Stop: ${signal.get('stop_loss', 0):.2f}
Target: ${signal.get('target_1', 0):.2f}

R:R: {signal.get('risk_reward', 0):.2f}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        self.send_telegram(msg)
        self.send_email(f"Signal: {signal.get('symbol')}", msg)
        self._print(msg)

    def _print(self, msg: str):
        """Print to console"""
        print("=" * 50)
        print(msg)
        print("=" * 50)


if __name__ == "__main__":
    alerts = AlertSystem()
    alerts.send_signal({
        "symbol": "NVDA",
        "name": "NVIDIA",
        "signal_status": "STRONG BUY",
        "signal_score": 85,
        "setup_type": "PULLBACK",
        "ideal_entry": 872.50,
        "stop_loss": 842.00,
        "target_1": 920.00,
        "risk_reward": 2.1,
    })
