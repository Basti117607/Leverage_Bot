# UDEGEN Leverage Trading Simulator Bot

Ein Telegram Bot, der einen interaktiven Leverage-Trading-Simulator implementiert.

## Features

- Hebel von 1x bis 125x
- Konfigurierbare Position Size
- Realistische Preissimulation
- Liquidationsberechnung
- P&L-Tracking
- Interaktive Buttons
- Emoji-basierte Benutzeroberfläche

## Installation

1. Python-Pakete installieren:
```bash
pip install -r requirements.txt
```

2. Bot Token in `.env` Datei konfigurieren:
```
BOT_TOKEN=dein_bot_token
```

## Starten

Bot starten:
```bash
python main.py
```

## Verwendung

1. Starte den Bot mit `/start`
2. Wähle deinen Hebel (1-125x)
3. Setze deine Position Size ($100-$10000)
4. Trade mit den interaktiven Buttons
5. Verkaufe oder werde liquidiert!

## Projektstruktur

```
TGLevBot/
├── src/
│   ├── models/
│   │   └── leverage_game.py    # Spiellogik
│   └── handlers/
│       └── game_handlers.py    # Telegram Handler
├── main.py                     # Bot Hauptdatei
├── requirements.txt            # Python Abhängigkeiten
└── .env                        # Umgebungsvariablen
```

## Warnung

Dies ist nur ein Simulator! Handel niemals mit echtem Geld basierend auf diesem Bot!
