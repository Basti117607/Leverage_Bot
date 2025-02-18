from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler, ContextTypes
import os
import logging
from dotenv import load_dotenv
from src.handlers.game_handlers import (
    LEVERAGE, POSITION_SIZE, TRADING,
    start_command,
    set_leverage,
    set_position,
    trade,
    GameHandler
)
from src.handlers.help_handlers import (
    help_command,
    basics_command,
    interface_command,
    liquidation_command,
    tips_command
)
from src.handlers.admin_handlers import AdminHandler
from src.models.leaderboard import Leaderboard
from src.utils.process_lock import SingleInstanceLock

async def post_init(application: Application) -> None:
    """Post-initialization hook for the bot."""
    await setup_commands(application)
    logging.info("Bot commands have been set up")

async def setup_commands(application: Application):
    """Set up bot commands to show in the command menu."""
    commands = [
        BotCommand("getrekt", "🎰 Start das UDEGEN Leverage Trading Game"),
        BotCommand("help", "❓ Zeigt die Hilfe an"),
        BotCommand("basics", "📚 Erklärt die Grundlagen"),
        BotCommand("interface", "🖥️ Erklärt die Benutzeroberfläche"),
        BotCommand("liquidation", "💀 Erklärt die Liquidation"),
        BotCommand("tips", "💡 Zeigt Trading-Tipps")
    ]
    await application.bot.set_my_commands(commands)

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get the bot token
        token = os.getenv('BOT_TOKEN')
        if not token:
            raise ValueError("No BOT_TOKEN found in .env file, degen! Get your act together!")

        # Logging message
        logger.info("Bot is launching... Let's lose some cash, degen style!")
        
        # Create data directory
        os.makedirs("data", exist_ok=True)
        
        # Initialize the lock
        lock = SingleInstanceLock("data/bot.lock")
        if not lock.acquire():
            logger.error("Bot läuft bereits! Beende diese Instanz.")
            return
        
        # Initialize leaderboard
        leaderboard = Leaderboard("data/leaderboard.json")
        
        # Initialize handlers
        game_handler = GameHandler(leaderboard)
        admin_ids = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]
        admin_handler = AdminHandler(leaderboard=leaderboard, admin_ids=admin_ids, lock=lock)
        
        # Create application instance with post_init
        application = (
            Application.builder()
            .token(token)
            .post_init(post_init)
            .build()
        )
        
        # Add game handler to context
        application.bot_data['game_handler'] = game_handler
        
        # Add conversation handler first (higher priority)
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler('getrekt', start_command, filters=filters.COMMAND)
            ],
            states={
                LEVERAGE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, set_leverage),
                    CallbackQueryHandler(set_leverage, pattern='^leverage_')
                ],
                POSITION_SIZE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, set_position),
                ],
                TRADING: [
                    CallbackQueryHandler(trade, pattern='^(up|down|quit|trade)$')
                ],
            },
            fallbacks=[]  # Wir brauchen keine fallbacks, da wir quit über den Button handeln
        )
        
        application.add_handler(conv_handler)
        
        # Add admin command handlers (higher priority than other commands)
        application.add_handler(CommandHandler('clearleaderboard', admin_handler.clear_leaderboard, filters=filters.COMMAND), group=1)
        application.add_handler(CommandHandler('restart', admin_handler.restart_bot, filters=filters.COMMAND), group=1)
        application.add_handler(CommandHandler('stop', admin_handler.stop_bot, filters=filters.COMMAND), group=1)
        
        # Add global callback handler for start button
        application.add_handler(CallbackQueryHandler(start_command, pattern='^getrekt$'))
        
        # Add other command handlers (lower priority)
        application.add_handler(CommandHandler('help', help_command, filters=filters.COMMAND))
        application.add_handler(CommandHandler('basics', basics_command, filters=filters.COMMAND))
        application.add_handler(CommandHandler('interface', interface_command, filters=filters.COMMAND))
        application.add_handler(CommandHandler('liquidation', liquidation_command, filters=filters.COMMAND))
        application.add_handler(CommandHandler('tips', tips_command, filters=filters.COMMAND))
        
        # Start the bot
        logger.info("Bot wird gestartet...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Fehler beim Starten des Bots: {e}")
        raise

if __name__ == '__main__':
    main()
