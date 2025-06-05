# Hermes — Fast & Precise Order Execution Tool for Binance Futures

**Hermes** is a minimalistic, high-performance desktop tool designed for lightning-fast order placement on **Binance Futures**.
Built as a companion app—not a replacement—for trading and charting platforms like TradingView, ATAS, Quantower, or even Binance itself,
Hermes delivers a frictionless way to execute trades in real time, with precision and speed that far surpass standard trading terminals.

---

## Purpose

Hermes is engineered as an **always-on, low-latency trading assistant** with a highly compact interface (just **180 pixels wide**) that sits on your screen alongside your primary charting platform.

Its core purpose is to:
- Enable **instant market order execution** with one click.
- Automatically place **stop-loss and take-profit** orders based on user-defined percentages — **immediately after the entry**, with no delay.
- Operate with a **real-time WebSocket price feed**, so the freshest price is always ready in memory — no waiting for price fetch during order placement.
- Maintain a **persistent API connection** to Binance to avoid latency caused by reconnection delays.
- Function exclusively with **Binance Futures pairs** for now, with plans to expand to spot trading.
- Provide a **clean, focused experience** for scalpers and high-frequency traders who need speed and minimal screen clutter.

In short, Hermes helps you **keep up with the market** — when every seconds matters.

---

## ⚙️ Features

- **Fast order execution** via Binance Futures API.
- **Automatic SL/TP placement** immediately after order fill, using percentage-based input.
- **Asynchronous WebSocket listener** for live price tracking in the background.
- **Persistent connection warm-up** to keep the Binance client always ready.
- **Symbol validation** ensures only valid trading pairs are accepted.
- **Auto-save of user preferences**, including SL/TP and symbol input — restored automatically on next launch.
- **Compact UI (180px width)** to overlay seamlessly with any trading screen.
- **Protection against accidental clicks** on critical actions like Buy, Sell, and Close Position.
- 🔐Secure API key handling** using `.env` environment variables.
- **Modular backend architecture**, designed for upcoming features such as:
  - Real-time price display within the UI
  - Active position indicator and trade history summary (Buy/Sell log)
  - User-defined alerts (e.g., price thresholds, signal triggers)
