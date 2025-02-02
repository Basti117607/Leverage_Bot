from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

HELP_SECTIONS = {
    'main': """📈 *UDEGEN Leverage Trading Simulator*

Willkommen beim UDEGEN Trading Simulator! 

*Verfügbare Befehle:*
/start - Starte ein neues Trading-Spiel
/help - Zeige diese Hilfe
/basics - Grundlagen des Leverage Trading
/interface - Erkläre das Trading Interface
/liquidation - Erkläre Liquidation
/tips - Trading Tipps

_Wähle einen Befehl für mehr Informationen_""",

    'basics': """🎮 *Trading Grundlagen*

*Hebel (Leverage):*
• Wählbar: 1x bis 125x
• Höherer Hebel bedeutet:
  📈 Größere Gewinne möglich
  📉 Höheres Risiko
  ⚡ Mehr Volatilität
  💀 Schnellere Liquidation

*Position Size:*
• Handelbar: $100 - $10,000
• Bestimmt max. Verlust
• Beispiel: $1,000 Position = max. $1,000 Verlust

/help - Zurück zur Haupthilfe""",

    'interface': """📊 *Trading Interface*

*Preisinformationen:*
💹 *Aktueller Preis:* Momentaner Handelspreis
📊 *P&L (Profit/Loss):*
  • Dollar: Aktueller Gewinn/Verlust
  • Prozent: Rendite auf Position

*Indikatoren:*
⚡ *Hebel:* Dein aktiver Hebelfaktor
💀 *Liquidationspreis:* Preis bei Totalverlust
⏱️ *Laufzeit:* Aktive Handelsdauer

*Buttons:*
🎲 *Weiter:* Nächster Preisschritt
💰 *Verkaufen:* Position schließen
❌ *Beenden:* Spiel beenden

/help - Zurück zur Haupthilfe""",

    'liquidation': """💀 *Liquidation verstehen*

*Berechnung:*
• 1x Hebel: Keine Liquidation
• Formel: Einstieg × (1 - 1/Hebel)

*Beispiele:*
• 10x: Liquidation bei -10%
• 50x: Liquidation bei -2%
• 100x: Liquidation bei -1%

Je höher der Hebel, desto näher der
Liquidationspreis am Einstiegspreis!

/help - Zurück zur Haupthilfe""",

    'tips': """💡 *Trading Tipps*

1. *Start klein:*
   • Beginne mit 2-5x Hebel
   • Lerne die Bewegungen kennen

2. *Risikomanagement:*
   • Beachte den Liquidationspreis
   • Nutze angemessene Position Size

3. *Strategie:*
   • Sei geduldig
   • Beobachte Preisbewegungen
   • Übe verschiedene Hebelgrößen

⚠️ *Wichtig:*
• Nur ein Simulator!
• Nie mit echtem Geld handeln!
• Echtes Trading hat zusätzliche
  Faktoren wie Gebühren & Slippage

/help - Zurück zur Haupthilfe"""
}

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Zeigt die Haupthilfe an."""
    await update.message.reply_text(
        HELP_SECTIONS['main'],
        parse_mode='Markdown'
    )

async def basics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Zeigt Grundlagen an."""
    await update.message.reply_text(
        HELP_SECTIONS['basics'],
        parse_mode='Markdown'
    )

async def interface_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Zeigt Interface-Hilfe an."""
    await update.message.reply_text(
        HELP_SECTIONS['interface'],
        parse_mode='Markdown'
    )

async def liquidation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Zeigt Liquidations-Hilfe an."""
    await update.message.reply_text(
        HELP_SECTIONS['liquidation'],
        parse_mode='Markdown'
    )

async def tips_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Zeigt Trading-Tipps an."""
    await update.message.reply_text(
        HELP_SECTIONS['tips'],
        parse_mode='Markdown'
    )
