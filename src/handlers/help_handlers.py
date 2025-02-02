from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

HELP_SECTIONS = {
    'main': """🎰 *WELCOME TO THE UDEGEN CASINO* 🎰

Yo degens! Ready to turn your Lambo dreams into bus tickets? 🚀

*Commands for Maximum REKT:*
/start - YOLO your life savings
/help - How to lose money faster
/basics - Learn why you'll get rekt
/interface - Your path to liquidation
/liquidation - The art of going broke
/tips - Pro tips (still gonna lose tho)

_Pick your poison, anon!_ 💀""",

    'basics': """🎮 *DEGEN BASICS 101* 🎮

*Leverage (AKA Your Doom):*
• Choose 1x-125x
• Higher leverage means:
  📈 More hopium
  📉 Faster liquidations
  ⚡ Maximum heart attacks
  💀 Speedrun to zero

*Position Size (Your Future Debt):*
• YOLO range: $100 - $10,000
• Determines how much you'll cry
• Example: $1,000 position = 1 month of ramen 🍜

/help - Back to copium central""",

    'interface': """📊 *YOUR ROAD TO REKT* 📊

*Price Info (AKA Pain Metrics):*
💹 *Current Price:* Watch your money evaporate
📊 *P&L (Pain/Loss):*
  • USD: How much you're down bad
  • %: Your portfolio's funeral progress

*Pro Degen Stats:*
⚡ *Leverage:* Your financial death multiplier
💀 *Liquidation Price:* Your inevitable destiny
⏱️ *Duration:* Time spent malding

*YOLO Buttons:*
🎲 *Next:* Generate more loss porn
💰 *Sell:* Accept defeat
❌ *Exit:* Back to McDonald's job application

/help - Return to hopium central""",

    'liquidation': """💀 *THE ART OF GETTING REKT* 💀

*NGMI Math:*
• 1x: Too boring to get rekt
• Formula: Entry × (1 - 1/Leverage) = Pain

*Speedrun Guide:*
• 10x: Die in 10 minutes
• 50x: Die in 2 minutes
• 100x: Spawn kill enabled

Pro tip: Higher leverage = faster loss porn! 📸

/help - Back to copium dispensary""",

    'tips': """💡 *HOW TO LOSE MONEY FASTER* 💡

1. *Start Small (cringe):*
   • Use 2-5x like a coward
   • Learn how to lose slowly

2. *Risk Management (lol):*
   • Watch liquidation price approach
   • Size position for maximum pain

3. *"Strategy":*
   • FOMO in at the top
   • Panic sell the bottom
   • Repeat until broke

⚠️ *SUPER IMPORTANT:*
• This is just a simulator!
• Real trading has more ways to lose money
• Not financial advice (duh)
• Your wife's boyfriend will thank you

/help - Back to copium central"""
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
