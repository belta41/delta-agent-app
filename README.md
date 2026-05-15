# Delta Exchange AI Agent - Android App

Run your Delta Exchange trading agent 24/7 on Android.

## Option 1: APK (Recommended)

### Build via GitHub Actions (Automated)
1. Push this repo to GitHub
2. Go to Actions tab → "Build APK" → Run workflow
3. Download APK from Artifacts
4. Install on Android & enter your Delta API keys

### Build Locally (Linux/Mac)
```bash
pip install buildozer
cd android-app
buildozer android debug
```
APK will be at `bin/deltaagent-*.apk`

## Option 2: Termux (Simpler, No APK build needed)

1. Install [Termux from F-Droid](https://f-droid.org/en/packages/com.termux/)
2. Install Termux:API: `pkg install termux-api`
3. Run setup:
```bash
cd Termux-Setup
bash setup.sh
```
4. Edit `~/delta-agent/.env` with your API keys
5. Run: `bash ~/delta-agent/run.sh`

For 24/7 running:
```bash
termux-wake-lock
cd ~/delta-agent && nohup python agent.py &
```

## Configuration
- **API Key**: From Delta Exchange dashboard
- **API Secret**: From Delta Exchange dashboard (enable Trading permission)
- **Leverage**: Default 20x (adjustable in app)
- **Coins**: BTC-USD, ETH-USD, SOL-USD

## Strategy
- Entry: Price crosses EMA-20 by 0.5%
- TP: 0.19% | SL: 1% (75% win rate on 60d backtest)
- 15m candles, 20x leverage
