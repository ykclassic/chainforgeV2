# 🛡️ AEGIS: Nexus Intelligence Suite

**AEGIS** is a professional-grade quantitative market intelligence engine built for **TechSolute**. It transcends standard technical analysis by merging high-fidelity signal generation with real-time sentiment analysis and order book imbalance checks.

## 🚀 Core Features
* **Triple-Convergence Strategy:** Combines RSI, MACD, and Aroon Oscillator for high-probability entries.
* **Realism Layer:** Built-in accounting for **0.1% Taker Fees** and **0.05% Slippage** to ensure "paper profits" match reality.
* **Intelligence Overlay:** Live news sentiment filtering via **CryptoPanic** and L2 Order Book Imbalance (OBI) tracking.
* **Institutional Metrics:** Automated calculation of Sharpe Ratio, Sortino Ratio, and Maximum Drawdown.
* **Serverless Automation:** Fully integrated with **GitHub Actions** for hourly autonomous scanning.

## 📁 Project Structure
```text
├── .github/workflows/   # CI/CD Automation
├── core/
│   ├── engine.py       # Signal & Risk Logic
│   ├── metrics.py      # Performance Math
│   └── intelligence.py # Sentiment & Liquidity
├── scripts/
│   └── run_backtest.py # Main Orchestrator
└── requirements.txt    # Dependencies
