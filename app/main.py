import os
import sys
import time
import threading
import json
import urllib.request
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.utils import platform

if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.INTERNET, Permission.WRITE_EXTERNAL_STORAGE])

from delta_connector import DeltaConnector


class EliteAgent:
    def __init__(self, api_key="", api_secret="", leverage=20, capital=100):
        self.api_key = api_key
        self.api_secret = api_secret
        self.leverage = leverage
        self.capital = capital
        self.risk_pct = 0.05
        self.running = False
        self.connector = None
        self.logs = []
        self.top_coins = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        self.price_history = {s: [] for s in self.top_coins}

    def fetch_klines(self, symbol, limit=30):
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit={limit}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        closes = [float(k[4]) for k in data]
        return closes

    def compute_rsi(self, closes, period=14):
        if len(closes) < period + 1:
            return 50
        gains, losses = 0, 0
        for i in range(len(closes) - period, len(closes) - 1):
            diff = closes[i+1] - closes[i]
            if diff > 0: gains += diff
            else: losses -= diff
        avg_gain = gains / period
        avg_loss = losses / period
        if avg_loss == 0: return 100
        rs = avg_gain / avg_loss
        return 100 - 100 / (1 + rs)

    def compute_ema(self, closes, period=20):
        if len(closes) < period:
            return closes[-1] if closes else 0
        multiplier = 2 / (period + 1)
        ema = sum(closes[:period]) / period
        for price in closes[period:]:
            ema = (price - ema) * multiplier + ema
        return ema

    def run_cycle(self):
        if not self.running:
            return

        for symbol in self.top_coins:
            try:
                closes = self.fetch_klines(symbol)
                price = closes[-1]
                ema_20 = self.compute_ema(closes)
                rsi = self.compute_rsi(closes)

                signal = "NONE"
                if price > ema_20 * 1.005:
                    signal = "LONG"
                elif price < ema_20 * 0.995:
                    signal = "SHORT"

                msg = f"{symbol}: ${price:.2f} | RSI: {rsi:.1f} | {signal}"
                self.logs.append(msg)

                if signal != "NONE" and self.connector:
                    side = "buy" if signal == "LONG" else "sell"
                    self.connector.place_order(
                        product_id=1, size=0.001, side=side, leverage=self.leverage
                    )
                    self.logs.append(f"ORDER PLACED: {signal} {symbol}")
            except Exception as e:
                self.logs.append(f"Error {symbol}: {e}")

        if len(self.logs) > 100:
            self.logs = self.logs[-50:]


class DeltaAgentApp(App):
    def __init__(self):
        super().__init__()
        self.icon = "icon.png"
        self.agent = EliteAgent()

    def build(self):
        root = BoxLayout(orientation="vertical", spacing=5, padding=10)

        title = Label(
            text="DELTA EXCHANGE AI AGENT",
            size_hint_y=0.08,
            font_size="18sp",
            bold=True,
        )
        root.add_widget(title)

        config = BoxLayout(orientation="vertical", size_hint_y=0.25, spacing=3)
        self.api_key_input = TextInput(
            hint_text="Delta API Key", multiline=False, password=True
        )
        self.api_secret_input = TextInput(
            hint_text="Delta API Secret", multiline=False, password=True
        )
        self.leverage_input = TextInput(
            hint_text="Leverage (default: 20)", multiline=False, text="20"
        )
        config.add_widget(self.api_key_input)
        config.add_widget(self.api_secret_input)
        config.add_widget(self.leverage_input)
        root.add_widget(config)

        buttons = BoxLayout(orientation="horizontal", size_hint_y=0.08, spacing=10)
        self.start_btn = Button(text="START AGENT", background_color=(0, 1, 0, 1))
        self.start_btn.bind(on_press=self.toggle_agent)
        self.status_label = Label(text="STOPPED", color=(1, 0, 0, 1))
        buttons.add_widget(self.start_btn)
        buttons.add_widget(self.status_label)
        root.add_widget(buttons)

        log_box = BoxLayout(orientation="vertical", size_hint_y=0.1)
        log_box.add_widget(Label(text="TRADE LOG", size_hint_y=0.3, font_size="14sp"))
        root.add_widget(log_box)

        self.log_area = TextInput(
            readonly=True,
            multiline=True,
            text="Ready. Configure API keys and press START.\n",
            font_size="10sp",
            background_color=(0.05, 0.05, 0.05, 1),
            foreground_color=(0, 1, 0, 1),
        )
        scroll = ScrollView(size_hint=(1, 0.45))
        scroll.add_widget(self.log_area)
        root.add_widget(scroll)

        Clock.schedule_interval(self.update_logs, 1)
        return root

    def toggle_agent(self, instance):
        if not self.agent.running:
            api_key = self.api_key_input.text.strip()
            api_secret = self.api_secret_input.text.strip()
            lev = int(self.leverage_input.text.strip() or "20")

            if api_key and api_secret:
                self.agent.connector = DeltaConnector(
                    api_key=api_key, api_secret=api_secret
                )

            self.agent.leverage = lev
            self.agent.running = True
            self.start_btn.text = "STOP AGENT"
            self.start_btn.background_color = (1, 0, 0, 1)
            self.status_label.text = "RUNNING"
            self.status_label.color = (0, 1, 0, 1)
            self.log_area.text += "Agent started.\n"

            thread = threading.Thread(target=self.run_agent_loop, daemon=True)
            thread.start()
        else:
            self.agent.running = False
            self.start_btn.text = "START AGENT"
            self.start_btn.background_color = (0, 1, 0, 1)
            self.status_label.text = "STOPPED"
            self.status_label.color = (1, 0, 0, 1)
            self.log_area.text += "Agent stopped.\n"

    def run_agent_loop(self):
        while self.agent.running:
            self.agent.run_cycle()
            for _ in range(60):
                if not self.agent.running:
                    break
                time.sleep(1)

    def update_logs(self, dt):
        if self.agent.logs:
            self.log_area.text = "\n".join(self.agent.logs[-30:])


if __name__ == "__main__":
    DeltaAgentApp().run()
