from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, error as telegram
from telegram.ext import ContextTypes, ConversationHandler
from ..models.leverage_game import LeverageGame
import logging
import asyncio
import urllib.parse

# States für den ConversationHandler
LEVERAGE, POSITION_SIZE, TRADING = range(3)

# Konfigurationswerte
MAX_LEVERAGE = 125
MIN_POSITION = 100
MAX_POSITION = 10000

class GameHandler:
    def __init__(self, leaderboard=None):
        self.leaderboard = leaderboard

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Startet den Leverage-Simulator."""
    logging.info("Start command triggered")
    
    # Clean up previous game state
    if 'game' in context.user_data:
        old_game = context.user_data.pop('game')
        del old_game  # Ensure proper cleanup
    
    # Initialize new game
    game = LeverageGame()
    context.user_data['game'] = game
    
    start_message = (
        "🎰 WELCOME TO THE CASINO OF PAIN 🎰\n"
        "───────────────\n"
        "🤡 Ready to turn your Lambo dreams into bus tickets?\n"
        "Where millionaires become McDonald's employees...\n\n"
        "⚡ Choose your financial death multiplier (1-125x):\n"
        "More leverage = faster loss porn! 📸\n"
        "(or instant liquidation if you're speedrunning)\n\n"
        "Send a number 1-125 and let's get rekt..."
    )
    
    if update.callback_query:
        logging.info("Start triggered by callback")
        await update.callback_query.answer()  # Acknowledge the callback
        await update.callback_query.edit_message_text(start_message)
    else:
        logging.info("Start triggered by command")
        await update.message.reply_text(start_message)
    
    return LEVERAGE

async def set_leverage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Setzt den Hebel für das Trading."""
    try:
        # Handle both callback query and text message
        if update.callback_query:
            query = update.callback_query
            leverage = int(query.data.split('_')[1])  # leverage_X -> X
            await query.answer()  # Acknowledge the button click
        else:
            leverage = int(update.message.text)
        
        if 1 <= leverage <= MAX_LEVERAGE:
            game = context.user_data.get('game')
            if not game:
                game = LeverageGame()
                context.user_data['game'] = game
            
            game.leverage = leverage
            
            # Leverage comments based on size
            leverage_comment = "🐔 Playing it safe? What a coward..." if leverage < 10 else \
                             "😎 Now we're talking! Still a bit soft tho" if leverage < 30 else \
                             "🔥 ABSOLUTE DEGEN ENERGY! LFG!" if leverage < 50 else \
                             "💀 RIP BOZO! Time to update that LinkedIn!"
            
            message = (
                f"{leverage_comment}\n\n"
                f"⚡ {leverage}x leverage activated! NGMI\n\n"
                "💰 Now your position size (100-10000 $):\n"
                "Remember: Real degens go all-in with rent money! 🎰"
            )
            
            if update.callback_query:
                await query.edit_message_text(message)
            else:
                await update.message.reply_text(message)
            
            return POSITION_SIZE
        else:
            error_message = "❌ Bruh... can you even read? 1-125x or go back to school! 🥴"
            if update.callback_query:
                await query.edit_message_text(error_message)
            else:
                await update.message.reply_text(error_message)
            return LEVERAGE
    except (ValueError, IndexError):
        error_message = "❌ That's not a number, that's your IQ! 🤦‍♂️"
        if update.callback_query:
            await update.callback_query.edit_message_text(error_message)
        else:
            await update.message.reply_text(error_message)
        return LEVERAGE

async def set_position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Setzt die Position Size für das Trading."""
    try:
        position = int(update.message.text)
        if MIN_POSITION <= position <= MAX_POSITION:
            game = context.user_data['game']
            game.position_size = position
            
            # Size comments
            size_comment = "🐜 Ant-sized bet... do you even degen?" if position < 1000 else \
                          "🦊 Starting to look serious!" if position < 5000 else \
                          "🦍 GORILLA BALLS ENERGY! THIS IS THE WAY!"
            
            keyboard = [
                [
                    InlineKeyboardButton("🎰 SEND IT!", callback_data='trade'),
                    InlineKeyboardButton("🐔 Run away", callback_data='quit')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"🎰 READY TO GET REKT 🎰\n"
                "═══════════════════\n"
                f"{size_comment}\n"
                f"💼 Your future debt: ${position:,.2f}\n"
                f"⚡ Pain multiplier: {game.leverage}x\n"
                f"📈 Entry to hell: ${game.initial_price:,.2f}\n"
                f"💀 Liquidation imminent: ${game.calculate_liquidation_price():,.2f}\n"
                "───────────────\n"
                "🚀 Ready to update that resume? 🚀",
                reply_markup=reply_markup
            )
            return TRADING
        else:
            await update.message.reply_text(
                f"⚠️ Pick a number between ${MIN_POSITION} and ${MAX_POSITION}!\n"
                "Even degens can count, right? 🤔"
            )
            return POSITION_SIZE
    except ValueError:
        await update.message.reply_text("❌ That's a number like LUNA is a stablecoin! Try again!")
        return POSITION_SIZE

async def trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Führt einen Handelszug aus."""
    query = update.callback_query
    
    try:
        logging.info(f"Trade callback erhalten: {query.data}")
        await query.answer()
        
        if not context.user_data.get('game'):
            logging.warning("Kein aktives Spiel gefunden")
            await query.edit_message_text(
                "⚠️ Error: No active game.\n"
                "Start a new one and lose money properly! 🎰"
            )
            context.user_data.pop('game', None)  # Clean up any invalid game state
            return ConversationHandler.END
        
        game = context.user_data['game']
        logging.info(f"Game state: leverage={game.leverage}, position_size={game.position_size}, current_price={game.current_price}, is_liquidated={game.is_liquidated}")
        
        if query.data == 'quit':
            logging.info("Spiel wird beendet")
            stats = game.get_stats()
            
            # Get username for final results
            user = query.from_user
            user_name = f"@{user.username}" if user.username else "Anonym"
            
            # Add score to leaderboard if available
            game_handler = context.bot_data.get('game_handler')
            if game_handler and game_handler.leaderboard:
                game_handler.leaderboard.add_score(
                    username=user_name,
                    score=stats['score'],
                    leverage=stats['leverage'],
                    pnl=stats['profit_loss'],
                    ticks=stats['ticks']
                )
                # Get leaderboard text
                leaderboard_text = game_handler.leaderboard.format_leaderboard()
            else:
                leaderboard_text = ""
            
            # Create tweet text
            tweet_text = (
                f"🎮 Just got REKT on LeverageBot!\n"
                f"💰 Damage Report: ${stats['profit_loss']:,.2f} ({stats['profit_loss_percent']:+.1f}%)\n"
                f"⚡ {stats['leverage']}x leverage because I hate money\n"
                f"🎲 Survived: {stats['ticks']} ticks before liquidation\n"
                f"🏆 Score: {stats['score']:,.1f}\n"
                f"\n🤖 @UDEGENBot - Where dreams become nightmares"
            )
            
            # Create the Twitter Share URL
            tweet_url = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(tweet_text)}"
            
            keyboard = [
                [
                    InlineKeyboardButton("🎮 Neues Spiel", callback_data='start'),
                    InlineKeyboardButton("🐦 Share on Twitter", url=tweet_url)
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = (
                f"🏁 Trading beendet!\n"
                "═══════════════════\n"
                f"👤 Trader: {user_name}\n"
                f"💰 Finaler P&L: ${stats['profit_loss']:,.2f} ({stats['profit_loss_percent']:.1f}%)\n"
                f"🎲 Ticks überlebt: {stats['ticks']}\n"
                f"🏆 Final Score: {stats['score']:,.1f}\n"
                "═══════════════════\n\n"
                f"{leaderboard_text}"
            )
            await query.edit_message_text(
                message,
                reply_markup=reply_markup
            )
            logging.info("Game ended by selling, cleaning up state")
            context.user_data.pop('game', None)  # Clean up game state
            return LEVERAGE  # Return to leverage state for new game
        
        # Clear existing price steps and generate new ones
        game.price_steps = []
        game.generate_price_movement()
        is_liquidated = False
        
        # Animation delay configuration
        ANIMATION_DELAY = 0.5  # Consistent delay between price updates
        
        # Zeige die Preisbewegung in Schritten an
        for current_price in game.price_steps:
            try:
                game.current_price = current_price
                logging.info(f"Price step: current_price={current_price}, liq_price={game.calculate_liquidation_price()}")
                
                # Berechne temporären P&L für diesen Schritt
                temp_pl = game.position_size * ((current_price - game.initial_price) / game.initial_price) * game.leverage
                price_change = ((current_price - game.initial_price) / game.initial_price) * 100
                
                # Prüfe auf Liquidation
                if current_price <= game.calculate_liquidation_price():
                    is_liquidated = True
                    logging.info("Liquidation während Animation erkannt")
                    game.is_liquidated = True
                    game.profit_loss = -game.position_size
                    game.increment_tick()
                    
                    stats = game.get_stats()
                    keyboard = [
                        [
                            InlineKeyboardButton("🎮 Neues Spiel", callback_data='start')
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    message = (
                        "☠️ GET REKT LMAO! ☠️\n"
                        "═══════════════════\n"
                        "🤡 Congratulations!\n"
                        "You played yourself!\n"
                        "───────────────\n"
                        f"💸 Lost: ${abs(stats['profit_loss']):,.2f}\n"
                        f"🪦 Survived: {stats['ticks']} ticks\n"
                        "───────────────\n"
                        "🏆 GAME OVER!\n"
                        "Score: 0 (bruh...)\n"
                        "═══════════════════"
                    )
                    
                    await query.edit_message_text(
                        message,
                        reply_markup=reply_markup
                    )
                    logging.info("Game ended by liquidation, cleaning up state")
                    context.user_data.pop('game', None)  # Clean up game state
                    return LEVERAGE
                # Bestimme Emojis und Messages
                trend_emoji = "📈" if price_change > 0 else "📉"
                move_emoji = "🚀" if price_change > 5 else \
                           "📈" if price_change > 0 else \
                           "📉" if price_change > -5 else \
                           "💥"
                
                status_msg = "PUMP IT! 🚀" if price_change > 5 else \
                           "Number go up! 📈" if price_change > 0 else \
                           "Dip buying time! 🎯" if price_change > -5 else \
                           "DAMP IT! 📉"
                
                # Calculate portfolio values
                portfolio_value = game.calculate_portfolio_value()
                portfolio_change = ((portfolio_value / game.position_size) - 1) * 100
                
                # Determine emojis
                portfolio_emoji = "🐋" if portfolio_change > 50 else \
                               "🦍" if portfolio_change > 20 else \
                               "🐂" if portfolio_change > 0 else \
                               "🐻" if portfolio_change > -10 else \
                               "💀"
                
                pl_emoji = "🤑" if temp_pl > 0 else "🤡"
                
                # Update message during animation
                message = (
                    f"{move_emoji} {status_msg} {trend_emoji}\n"
                    "═══════════════════\n"
                    f"💹 Price: ${current_price:,.2f} ({price_change:+.2f}%)\n"
                    f"📈 Entry: ${game.initial_price:,.2f}\n"
                    "───────────────\n"
                    f"💼 Bags: ${portfolio_value:,.2f} {portfolio_emoji}\n"
                    f"📊 Gainz: {portfolio_change:+.1f}%\n"
                    f"{pl_emoji} PNL: ${temp_pl:,.2f}\n"
                    "───────────────\n"
                    f"⚡ Degen Mode: {game.leverage}x\n"
                    f"💀 Liq Price: ${game.calculate_liquidation_price():,.2f}\n"
                    "───────────────\n"
                    f"🎲 Survivability: {game.ticks} ticks\n"
                    f"🏆 DEGEN Score: {game.calculate_score():,.1f}\n"
                    "═══════════════════"
                )
                
                try:
                    await query.edit_message_text(
                        message,
                        reply_markup=None  # No buttons during animation
                    )
                except telegram.BadRequest as e:
                    if "message is not modified" not in str(e).lower():
                        raise
                
                await asyncio.sleep(ANIMATION_DELAY)  # Consistent animation delay
                
            except telegram.BadRequest as e:
                if "message is not modified" not in str(e).lower():
                    raise
                await asyncio.sleep(0.2)
                continue
        
        # Finaler Update nach der Animation
        if game.update_price():  # Returns True if liquidated
            logging.info("Liquidation nach Animation erkannt")
            try:
                stats = game.get_stats()  # Get final stats before cleanup
                logging.info(f"Finale Liquidation stats: {stats}")
                keyboard = [
                    [
                        InlineKeyboardButton("🎮 Neues Spiel", callback_data='start')
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message = (
                    "☠️ GET REKT LMAO! ☠️\n"
                    "═══════════════════\n"
                    "🤡 Congratulations!\n"
                    "You played yourself!\n"
                    "───────────────\n"
                    f"💸 Verloren: ${abs(stats['profit_loss']):,.2f}\n"
                    f"🪦 Überlebt: {stats['ticks']} ticks\n"
                    "───────────────\n"
                    "🏆 GAME OVER!\n"
                    "Score: 0 (bruh...)\n"
                    "═══════════════════"
                )
                await query.answer()  # Acknowledge the callback
                await query.edit_message_text(
                    message,
                    reply_markup=reply_markup
                )
                logging.info("Game ended by liquidation, cleaning up state")
                context.user_data.pop('game', None)  # Clean up game state
                return LEVERAGE  # Return to leverage state for new game
            except telegram.BadRequest as e:
                if "message is not modified" not in str(e).lower():
                    raise   
        stats = game.get_stats()
        logging.info(f"Finale Stats: {stats}")
            
        # DEGEN Performance Messages
        result_msg = "GIGACHAD MOVE! 🐋" if stats['profit_loss'] > stats['position_size'] else \
                   "NICE GAINS BRO! 🦍" if stats['profit_loss'] > 0 else \
                   "NGMI BRUH... 🤡"
        
        pl_emoji = "🤑" if stats['profit_loss'] > 0 else "🤡"
        portfolio_emoji = "🦍" if stats['portfolio_change'] > 0 else "💀"
        
        message = (
            f"{result_msg}\n"
            "═══════════════════\n"
            f"💼 Final Bags: ${stats['portfolio_value']:,.2f} {portfolio_emoji}\n"
            f"📊 Gainz: {stats['portfolio_change']:+.1f}%\n"
            f"{pl_emoji} PNL: ${stats['profit_loss']:,.2f}\n"
            "───────────────\n"
            f"📈 Entry: ${stats['initial_price']:,.2f}\n"
            f"💹 Exit: ${stats['current_price']:,.2f}\n"
            f"💀 Liquidation Price: ${stats['liquidation_price']:,.2f}\n"
            "───────────────\n"
            f"⚡ Degen Level: {stats['leverage']}x\n"
            f"🎲 Survived: {stats['ticks']} ticks\n"
            f"⏱️ Time: {stats['duration']}s\n"
            "───────────────\n"
            "🏆 FINAL SCORE\n"
            f"{stats['score']:,.1f} DEGEN Points!\n"
            "═══════════════════"
        )
        
        # After animation completes - show Weiter/Verkaufen buttons
        keyboard = [
            [
                InlineKeyboardButton("🎲 Weiter", callback_data='trade'),
                InlineKeyboardButton("💰 Verkaufen", callback_data='quit')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(
                message,
                reply_markup=reply_markup
            )
        except telegram.BadRequest as e:
            if "message is not modified" not in str(e).lower():
                logging.error(f"Fehler beim Update der Nachricht: {str(e)}")
                await query.edit_message_text(
                    "⚠️ Ein Fehler ist aufgetreten.\nBitte starte ein neues Spiel"
                )
                context.user_data.pop('game', None)  # Clean up game state
                return ConversationHandler.END
        
        return TRADING                
    except Exception as e:
        logging.error(f"Fehler im Trade Handler: {str(e)}")
        try:
            await query.edit_message_text(
                "⚠️ Ein Fehler ist aufgetreten.\nBitte starte ein neues Spiel"
            )
            context.user_data.pop('game', None)  # Clean up game state
        except:
            pass
        return ConversationHandler.END

async def show_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Zeigt die Bestenliste an"""
    query = update.callback_query
    if not query:
        return
            
    await query.answer()
    
    if not hasattr(context, 'handler') or not context.handler.leaderboard:
        await query.edit_message_text(
            "⚠️ Bestenliste ist nicht verfügbar!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🎮 Neues Spiel", callback_data='start')
            ]])
        )
        return
            
    leaderboard_text = context.handler.leaderboard.format_leaderboard()
        
    await query.edit_message_text(
        leaderboard_text,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🎮 Neues Spiel", callback_data='start')
        ]])
    )
