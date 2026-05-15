#!/data/data/com.termux/files/usr/bin/bash

echo "=============================="
echo " Delta AI Agent - Termux Setup"
echo "=============================="

echo "[1/6] Updating packages..."
pkg update -y && pkg upgrade -y

echo "[2/6] Installing Python & dependencies..."
pkg install -y python python-pip git clang libxml2 libxslt cmake

echo "[3/6] Installing pip packages..."
pip install --upgrade pip setuptools wheel
pip install pandas yfinance numpy delta-rest-client python-dotenv requests

echo "[4/6] Cloning agent files..."
cd ~
mkdir -p delta-agent
cd delta-agent

cat > delta_connector.py << 'PYEOF'
import os
class DeltaConnector:
    def __init__(self, api_key="", api_secret=""):
        self.api_key = api_key or os.getenv("DELTA_API_KEY", "")
        self.api_secret = api_secret or os.getenv("DELTA_API_SECRET", "")
        self.client = None
        self.base_url = "https://api.india.delta.exchange"
        if self.api_key and self.api_secret:
            try:
                from delta_rest_client import DeltaRestClient, OrderType
                self.client = DeltaRestClient(base_url=self.base_url, api_key=self.api_key, api_secret=self.api_secret)
                self.OrderType = OrderType
            except ImportError:
                pass
    def place_order(self, product_id, size, side, order_type="market_order", limit_price=None, leverage=20):
        if not self.client:
            print(f"MOCK: {side} {size} of {product_id}")
            return {"status": "mock"}
        ot = self.OrderType.MARKET
        if order_type == "limit_order":
            ot = self.OrderType.LIMIT
        try:
            self.client.set_leverage(product_id, leverage)
        except: pass
        params = {"product_id": product_id, "size": size, "side": side, "order_type": ot}
        if limit_price:
            params["limit_price"] = limit_price
        return self.client.place_order(**params)
PYEOF

cat > agent.py << 'PYEOF'
import os, time, json, sys
import pandas as pd
import yfinance as yf
from delta_connector import DeltaConnector

API_KEY = os.getenv("DELTA_API_KEY", "")
API_SECRET = os.getenv("DELTA_API_SECRET", "")
LEVERAGE = int(os.getenv("LEVERAGE", "20"))

connector = DeltaConnector(api_key=API_KEY, api_secret=API_SECRET) if API_KEY and API_SECRET else None
top_coins = ["BTC-USD", "ETH-USD", "SOL-USD"]

def compute_rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - 100 / (1 + rs)

def run_cycle():
    for symbol in top_coins:
        try:
            df = yf.download(symbol, period="1d", interval="15m", progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            close = df["Close"]
            ema_20 = close.ewm(span=20, adjust=False).mean().iloc[-1]
            price = float(close.iloc[-1])
            rsi = compute_rsi(close).iloc[-1]

            signal = "NONE"
            if price > ema_20 * 1.005:
                signal = "LONG"
            elif price < ema_20 * 0.995:
                signal = "SHORT"

            ts = time.strftime("%H:%M:%S")
            print(f"[{ts}] {symbol}: ${price:.2f} | RSI: {rsi:.1f} | {signal}")

            if signal != "NONE" and connector:
                side = "buy" if signal == "LONG" else "sell"
                connector.place_order(product_id=1, size=0.001, side=side, leverage=LEVERAGE)
                print(f">>> ORDER: {signal} {symbol}")
        except Exception as e:
            print(f"Error {symbol}: {e}")

if __name__ == "__main__":
    print("Delta AI Agent started (press Ctrl+C to stop)")
    print(f"Leverage: {LEVERAGE}x | Live: {connector is not None}")
    while True:
        run_cycle()
        time.sleep(300)
PYEOF

cat > .env << 'ENVEOF'
DELTA_API_KEY=your_api_key_here
DELTA_API_SECRET=your_api_secret_here
LEVERAGE=20
ENVEOF

echo "[5/6] Creating run script..."
cat > run.sh << 'SHEOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/delta-agent
echo "Starting Delta AI Agent..."
python agent.py
SHEOF
chmod +x run.sh

echo "[6/6] Setup complete!"
echo ""
echo "=============================="
echo " NEXT STEPS:"
echo "=============================="
echo "1. Edit API keys: nano ~/delta-agent/.env"
echo "2. Run agent:     bash ~/delta-agent/run.sh"
echo "3. Keep alive:    termux-wake-lock"
echo ""
echo "For 24/7 running:"
echo "  pkg install termux-services"
echo "  pkg install termux-api"
echo "  termux-wake-lock"
echo "  cd ~/delta-agent && nohup python agent.py &"
echo "=============================="
