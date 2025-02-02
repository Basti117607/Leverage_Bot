import logging
import os
import sys
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from src.handlers.game_handlers import (
    start_command,
    set_leverage,
    set_position,
    trade,
    LEVERAGE,
    POSITION_SIZE,
    TRADING
)
from src.handlers.help_handlers import (
    help_command,
    basics_command,
    interface_command,
    liquidation_command,
    tips_command
)

# Logging konfigurieren
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Startet den Bot."""
    try:
        # Lade Umgebungsvariablen
        load_dotenv()
        
        # Bot Token aus Umgebungsvariablen laden
        token = os.getenv('BOT_TOKEN')
        if not token:
            raise ValueError("Kein BOT_TOKEN in .env Datei gefunden!")
        
        # Application erstellen
        application = Application.builder().token(token).build()
        
        # Conversation Handler für das Trading-Spiel
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler('start', start_command),
            ],
            states={
                LEVERAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_leverage)],
                POSITION_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_position)],
                TRADING: [CallbackQueryHandler(trade)]
            },
            fallbacks=[CommandHandler('start', start_command)]
        )
        
        # Handler hinzufügen
        application.add_handler(conv_handler)
        application.add_handler(CallbackQueryHandler(start_command, pattern='^start$'))  # Handle "Neues Spiel" button
        
        # Help Handler hinzufügen
        application.add_handler(CommandHandler('help', help_command))
        application.add_handler(CommandHandler('basics', basics_command))
        application.add_handler(CommandHandler('interface', interface_command))
        application.add_handler(CommandHandler('liquidation', liquidation_command))
        application.add_handler(CommandHandler('tips', tips_command))
        
        # Bot starten
        logger.info("Bot wird gestartet...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Kritischer Fehler: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
