# 📈 UDEGEN Leverage Trading Simulator - Anleitung

## 🎮 Grundlagen

Der UDEGEN Leverage Trading Simulator ist ein Telegram Bot, der dir ermöglicht, Leverage Trading in einer sicheren Umgebung zu üben, ohne echtes Geld zu riskieren.

## 🚀 So startest du

1. Öffne den Bot auf Telegram: @UDEGEN_Leverage_Bot
2. Tippe `/start` um ein neues Spiel zu beginnen

## 📊 Die wichtigsten Begriffe

### Hebel (Leverage)
- Wählbar von 1x bis 125x
- Je höher der Hebel, desto:
  - 📈 Größer der potenzielle Gewinn
  - 📉 Größer das Verlustrisiko
  - ⚡ Höher die Volatilität
  - 💀 Näher der Liquidationspreis am Einstiegspreis

### Position Size
- Der Betrag, den du "investierst" ($100 - $10,000)
- Bestimmt zusammen mit dem Hebel deinen maximalen Verlust
- Beispiel: $1,000 Position = maximaler Verlust von $1,000

## 📈 Trading Interface

### Preisinformationen
- 💹 **Aktueller Preis**: Der momentane Handelspreis
- 📊 **P&L (Profit/Loss)**: 
  - In Dollar: Dein aktueller Gewinn/Verlust
  - In Prozent: Rendite bezogen auf deine Position Size

### Wichtige Indikatoren
- ⚡ **Hebel**: Dein gewählter Hebelfaktor
- 💀 **Liquidationspreis**: Bei diesem Preis verlierst du deine gesamte Position
- ⏱️ **Laufzeit**: Wie lange dein Trade schon aktiv ist

## 🎯 Liquidation verstehen

Der Liquidationspreis wird wie folgt berechnet:
- Bei 1x Hebel: Keine Liquidation möglich
- Bei höherem Hebel: `Liquidationspreis = Einstiegspreis * (1 - 1/Hebel)`

Beispiele:
- 10x Hebel: Liquidation bei -10% vom Einstiegspreis
- 50x Hebel: Liquidation bei -2% vom Einstiegspreis
- 100x Hebel: Liquidation bei -1% vom Einstiegspreis

## 🎲 Trading-Buttons

- 🎲 **Weiter**: Nächster Preisschritt
- 💰 **Verkaufen**: Position schließen und Gewinn/Verlust realisieren
- ❌ **Beenden**: Spiel vorzeitig beenden

## 💡 Trading-Tipps

1. **Starte klein**: Beginne mit niedrigem Hebel (2-5x) um ein Gefühl zu bekommen
2. **Beobachte die Volatilität**: Höherer Hebel = Stärkere Preisschwankungen
3. **Kenne dein Risiko**: Der Liquidationspreis zeigt dir, wie viel Spielraum du hast
4. **Übe Geduld**: Nicht jeder Trade muss ein Gewinner sein
5. **Position Sizing**: Versuche verschiedene Position Sizes mit verschiedenen Hebeln

## ⚠️ Wichtige Hinweise

1. Dies ist nur ein Simulator! Handel niemals mit echtem Geld basierend auf diesem Bot!
2. Die Preisbewegungen sind zufällig und simuliert
3. In der echten Welt gibt es zusätzliche Faktoren wie:
   - Handelsgebühren
   - Slippage
   - Liquiditätsprobleme
   - Technische Probleme

## 🆘 Befehle

- `/start`: Startet ein neues Spiel
- Weitere Befehle folgen in zukünftigen Updates
