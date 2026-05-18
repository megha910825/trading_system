#!/usr/bin/env python3
"""
Alert System - Sends trading alerts via Telegram and Email
Handles missing configuration gracefully
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Optional
import requests

try:
    import config
except ImportError:
    config = None


class AlertSystem:
    """
    Sends trading alerts via multiple channels
    - Telegram
    - Email
    - Console (always)
    """

    def __init__(self):
        # Telegram config (with safe defaults)
        self.telegram_token = getattr(config, 'TELEGRAM_BOT_TOKEN', '') if config else ''
        self.telegram_chat_id = getattr(config, 'TELEGRAM_CHAT_ID', '') if config else ''
        self.telegram_enabled = bool(self.telegram_token and self.telegram_chat_id)

        # Email config (with safe defaults)
        self.email_sender = getattr(config, 'EMAIL_SENDER', '') if config else ''
        self.email_password = getattr(config, 'EMAIL_PASSWORD', '') if config else ''
        self.email_receiver = getattr(config, 'EMAIL_RECEIVER', '') if config else ''
        self.smtp_server = getattr(config, 'SMTP_SERVER', 'smtp.gmail.com') if config else 'smtp.gmail.com'
        self.smtp_port = getattr(config, 'SMTP_PORT', 587) if config else 587
        self.email_enabled = bool(self.email_sender and self.email_password and self.email_receiver)

        # Status
        if self.telegram_enabled:
            print("✓ Telegram alerts enabled")
        if self.email_enabled:
            print("✓ Email alerts enabled")
        if not self.telegram_enabled and not self.email_enabled:
            print("ℹ️ No alert channels configured (console only)")

    def send_telegram(self, message: str) -> bool:
        """Send Telegram message"""
        if not self.telegram_enabled:
            return False

        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                print("✓ Telegram alert sent")
                return True
            else:
                print(f"✗ Telegram error: {response.status_code}")
                return False

        except Exception as e:
            print(f"✗ Telegram error: {e}")
            return False

    def send_email(self, subject: str, body: str) -> bool:
        """Send email alert"""
        if not self.email_enabled:
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_sender
            msg['To'] = self.email_receiver
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_sender, self.email_password)
                server.send_message(msg)

            print("✓ Email alert sent")
            return True

        except Exception as e:
            print(f"✗ Email error: {e}")
            return False

    def send_signal(self, signal: Dict) -> bool:
        """Send trading signal alert"""
        # Format message
        message = self._format_signal_message(signal)

        # Always print to console
        print("\n" + "=" * 50)
        print("📢 ALERT SENT")
        print("=" * 50)
        print(message)

        # Send to configured channels
        telegram_sent = self.send_telegram(message)

        email_subject = f"🎯 {signal.get('signal_status', 'SIGNAL')}: {signal.get('symbol', 'N/A')}"
        email_sent = self.send_email(email_subject, message)

        return telegram_sent or email_sent

    def _format_signal_message(self, signal: Dict) -> str:
        """Format signal as alert message"""
        # Get market info
        market = signal.get('market', 'US')
        currency = signal.get('currency', 'USD')
        curr_symbol = {"USD": "$", "EUR": "€", "INR": "₹"}.get(currency, "$")
        flag = {"US": "🇺🇸", "DE": "🇩🇪", "IN": "🇮🇳"}.get(market, "🌐")

        return f"""
{flag} {signal.get('market_name', market)} | 🎯 {signal.get('signal_status', 'SIGNAL')}

📊 {signal.get('symbol', 'N/A')} - {signal.get('name', '')[:30]}
Sector: {signal.get('sector', 'N/A')}
Setup: {signal.get('setup_type', 'N/A')}
Score: {signal.get('signal_score', 0)}/100

💰 TRADE SETUP ({currency}):
   Entry: {curr_symbol}{signal.get('ideal_entry', 0):,.2f}
   Stop: {curr_symbol}{signal.get('stop_loss', 0):,.2f}
   Target 1: {curr_symbol}{signal.get('target_1', 0):,.2f}
   Target 2: {curr_symbol}{signal.get('target_2', 0):,.2f}

📈 R:R: {signal.get('risk_reward', 0):.2f}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

    def send_daily_summary(self, signals: Dict) -> bool:
        """Send daily summary of all signals"""
        total = sum(len(s) for s in signals.values())

        if total == 0:
            message = "📊 Daily Summary: No signals today"
        else:
            lines = ["📊 DAILY TRADING SUMMARY", "=" * 30, ""]

            for market, market_signals in signals.items():
                if not market_signals:
                    continue

                flag = {"US": "🇺🇸", "DE": "🇩🇪", "IN": "🇮🇳"}.get(market, "🌐")
                lines.append(f"{flag} {market}: {len(market_signals)} signals")

                for sig in market_signals[:3]:
                    lines.append(f"  • {sig['symbol']} - {sig['signal_status']} (Score: {sig['signal_score']})")

            lines.append("")
            lines.append(f"Total: {total} signals")
            lines.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

            message = "\n".join(lines)

        print(message)
        self.send_telegram(message)
        self.send_email("📊 Daily Trading Summary", message)

        return True

    def send_test(self) -> bool:
        """Send test alert to verify configuration"""
        message = f"""
🧪 TEST ALERT

This is a test message from your Trading System.

✅ If you received this, alerts are working!

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        print(message)

        telegram_ok = self.send_telegram(message)
        email_ok = self.send_email("🧪 Trading System Test Alert", message)

        if telegram_ok:
            print("✓ Telegram test successful")
        else:
            print("✗ Telegram test failed (check TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)")

        if email_ok:
            print("✓ Email test successful")
        else:
            print("✗ Email test failed (check EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER)")

        return telegram_ok or email_ok


# ============================================================
# MAIN / TEST
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Alert System")
    parser.add_argument("command", nargs="?", default="status",
                       choices=["status", "test"],
                       help="Command: status or test")

    args = parser.parse_args()

    alerts = AlertSystem()

    if args.command == "status":
        print("\n" + "=" * 50)
        print("ALERT SYSTEM STATUS")
        print("=" * 50)
        print(f"\nTelegram: {'✓ Enabled' if alerts.telegram_enabled else '✗ Disabled'}")
        print(f"Email: {'✓ Enabled' if alerts.email_enabled else '✗ Disabled'}")

        if not alerts.telegram_enabled and not alerts.email_enabled:
            print("\n⚠️ No alert channels configured!")
            print("To enable alerts, create a .env file with:")
            print("  TELEGRAM_BOT_TOKEN=your_token")
            print("  TELEGRAM_CHAT_ID=your_chat_id")
            print("  EMAIL_SENDER=your_email")
            print("  EMAIL_PASSWORD=your_password")
            print("  EMAIL_RECEIVER=your_email")

    elif args.command == "test":
        print("\n" + "=" * 50)
        print("TESTING ALERT SYSTEM")
        print("=" * 50)
        alerts.send_test()
