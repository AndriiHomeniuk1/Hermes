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

---

## 🎥 Demo

Watch Hermes in action:

[![Watch the demo](https://img.youtube.com/vi/ROIUU0BaaCA/0.jpg)](https://youtu.be/ROIUU0BaaCA)

---

## 📁 Project Structure  
```text  
Hermes/  
├── main.py                 # Entry point of the application  
├── requirements.txt        # Python dependencies  
├── .env.example            # Template for environment variables (API keys)  
├── .gitignore              # Git ignore rules  
├── .python-version         # Python version specification  
├── README.md               # Project documentation  
│  
├── config/                 # Configuration and path definitions  
│   ├──  config_paths.py    # Paths to settings, styles, and .env files  
│   └──  settings.json      # Stores persistent user settings: trading symbol, SL/TP percentages  
│  
├── core/                   # Core application logic and Binance integration  
│   ├── binance_utils.py        # Utility functions for Binance (e.g., symbol validation)  
│   ├── client_binance.py       # Binance API client (key management, connectivity)  
│   ├── client_warmup.py        # Keeps the Binance connection alive  
│   ├── hermesMainWindow.py     # Main application window and UI logic  
│   ├── place_order.py          # Market, SL, TP order execution logic  
│   └── websockets_listener.py  # Real-time price listener via WebSocket  
│  
├── ui/                     # User interface components  
│   ├── customTitleBar.py   # Custom window title bar with drag/close functionality  
│   ├── hermes_ui.py        # PyQt5 UI layout (auto-generated)  
│   └── ui_helpers.py       # UI utilities (e.g., input validation, error highlighting)  
│  
├── resources/              # Visual assets and styling  
│   ├── style.qss           # QSS stylesheet for UI theming  
│   └── resources.qrc       # Qt resource collection (icons, etc.)
```
---
<img width="198" height="694" alt="hermes_1 (1)" src="https://github.com/user-attachments/assets/1f7878dd-27a6-4eff-95d7-ba53bcab568d" />
<img width="750" height="408" alt="Hermes_2" src="https://github.com/user-attachments/assets/4c7bd406-94bc-42e5-b4bc-d659a9c6e388" />
