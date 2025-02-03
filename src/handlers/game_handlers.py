from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, error as telegram
from telegram.ext import ContextTypes, ConversationHandler
from ..models.leverage_game import LeverageGame
from ..models.leaderboard import Leaderboard

import logging
import asyncio
import urllib.parse  # Add this line at the beginning of the file

# States für den ConversationHandler
LEVERAGE, POSITION_SIZE, TRADING = range(3)

# Konfigurationswerte
MAX_LEVERAGE = 125
MIN_POSITION = 100
MAX_POSITION = 10000

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the leverage simulator."""
    logging.info("Start command triggered")
    
    # Clean up previous game state
    if 'game' in context.user_data:
        old_game = context.user_data.pop('game')
        del old_game  # Proper cleanup
    
    # Initialize new game
    game = LeverageGame()
    context.user_data['game'] = game
    
    start_message = (
        "🎰 YO DEGEN, READY TO LOSE SOME MONEY? 🎰\n"
        "───────────────\n"
        "🤡 Welcome to the UDEGEN Casino!\n"
        "Where Lambos turn into bus tickets...\n\n"
        "⚡ Choose your leverage (1-125x):\n"
        "The more leverage, the more fun! 🫡\n"
        "(or a faster total wipeout, lol)\n\n"
        "Send a number between 1-125..."
    )
    
    if update.callback_query:
        logging.info("Start triggered by callback")
        await update.callback_query.answer()  # Acknowledge callback
        await update.callback_query.edit_message_text(start_message)
    else:
        logging.info("Start triggered by command")
        await update.message.reply_text(start_message)
    
    return LEVERAGE


async def set_leverage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sets the leverage for trading."""
    try:
        leverage = int(update.message.text)
        if 1 <= leverage <= MAX_LEVERAGE:
            context.user_data['game'].leverage = leverage
            
            # Fun comments based on chosen leverage
            leverage_comment = (
                "🐔 A bit conservative... but okay!" if leverage < 10 else
                "😎 Solid Degen Move!" if leverage < 30 else
                "🔥 ABSOLUTE CHAD ENERGY!" if leverage < 50 else
                "💀 RIP BOZO! Get ready for loss porn!"
            )
            
            await update.message.reply_text(
                f"{leverage_comment}\n\n"
                f"⚡ {leverage}x leverage activated!\n\n"
                "💰 Now, enter your bet (100-10000 $):\n"
                "Remember: Only true degens go all-in! 🎰"
            )
            return POSITION_SIZE
        else:
            await update.message.reply_text(
                "❌ Bruh... 1-125x or are you too high to read? 🥴"
            )
            return LEVERAGE
    except ValueError:
        await update.message.reply_text("❌ Dude, that's not a number! 🤦‍♂️")
        return LEVERAGE


async def set_position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sets the bet size for trading."""
    try:
        position = int(update.message.text)
        if MIN_POSITION <= position <= MAX_POSITION:
            game = context.user_data['game']
            game.position_size = position
            
            # Bet size comments
            size_comment = (
                "🐜 Ant bet... but okay!" if position < 1000 else
                "🦊 Fox energy!" if position < 5000 else
                "🦍 GORILLA SIZED BET! LFG!!!"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("🎰 YOLO IT!", callback_data='trade'),
                    InlineKeyboardButton("🐔 Exit", callback_data='quit')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"🎰 SETUP READY TO DEGEN 🎰\n"
                "═══════════════════\n"
                f"{size_comment}\n"
                f"💼 Bags: ${position:,.2f}\n"
                f"⚡ Leverage: {game.leverage}x\n"
                f"📈 Entry: ${game.initial_price:,.2f}\n"
                f"💀 Liquidation Price: ${game.calculate_liquidation_price():,.2f}\n"
                "───────────────\n"
                "🚀 Ready to get rekt? 🚀",
                reply_markup=reply_markup
            )
            return TRADING
        else:
            await update.message.reply_text(
                f"⚠️ Please choose a bet between ${MIN_POSITION} and ${MAX_POSITION}!"
            )
            return POSITION_SIZE
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number!")
        return POSITION_SIZE


async def trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Führt einen Handelszug aus."""
    query = update.callback_query

    try:
        logging.info(f"Trade callback received: {query.data}")
        await query.answer()

        # Validate game state...
        if not context.user_data.get('game'):
            logging.warning("Kein aktives Spiel gefunden")
            await query.edit_message_text(
                "⚠️ Fehler: Kein aktives Spiel.\nBitte starte ein neues Spiel"
            )
            context.user_data.pop('game', None)
            return ConversationHandler.END

        game = context.user_data['game']
        logging.info(f"Game state: leverage={game.leverage}, position_size={game.position_size}, current_price={game.current_price}, is_liquidated={game.is_liquidated}")

        # --- SELL (PANIC SELL) FLOW: Full results with leaderboard and Twitter share ---
        if query.data == 'quit':
            logging.info("Spiel wird beendet (Sell) – finalisiere Ergebnisse")
            stats = game.get_stats()

            # Leaderboard updaten
            from ..models.leaderboard import Leaderboard
            leaderboard = Leaderboard()
            user = query.from_user
            user_name = f"@{user.username}" if user.username else "Anonym"
            leaderboard.add_score(user_name, stats['score'], game.leverage, stats['profit_loss'], game.ticks)

            # ------------------------------
            # Erstelle Top 3 Text für den Twitter-Share
            top_three = leaderboard.get_top_10()[:3]
            prizes = ["100$ in $UDEGEN", "50$ in $UDEGEN", "25$ in $UDEGEN"]
            top_text_lines = []
            for i, entry in enumerate(top_three):
                username_entry = entry['username']
                # Sicherstellen, dass der Username mit @ beginnt
                if not username_entry.startswith('@'):
                    username_entry = f"@{username_entry}"
                top_text_lines.append(f"{i+1}. {username_entry} – {prizes[i]}")
            top_three_text = "\n".join(top_text_lines)

            # Hole das variable Auszahlungsdatum (z.B. letzter Tag des Monats)
            prize_date = leaderboard.get_prize_date()

            # ------------------------------
            # Erstelle den ultra-crazy Twitter-Share Text im UDEGEN Meme Style
            tweet_text = (
                f"🚀 YO, I just went FULL DEGEN in LeverageBot!\n"
                f"🏆 Final Score: {stats['score']:,.1f} DEGEN Points\n"
                f"🎲 Survived: {stats['ticks']} ticks at {game.leverage}x!\n"
                f"💰 P&L: ${stats['profit_loss']:,.2f} – Straight-up wild gains!\n\n"
                f"🔥 TOP DEGENS 🔥\n{top_three_text}\n\n"
                f"📆 Prizes drop on {prize_date}!\n"
                f"👉 JOIN US, get in the game & WIN\n"
        
            )

            # Erstelle die Twitter Share URL
            tweet_url = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(tweet_text)}"

            # Erstelle die finale Quit-Nachricht inklusive Leaderboard-Text
            leaderboard_text = leaderboard.format_leaderboard()
            message = (
                f"🏁 Your mum came in... trading closed!\n"
                "═══════════════════\n"
                f"👤 Trader: {user_name}\n"
                f"💰 Finaler P&L: ${stats['profit_loss']:,.2f} ({stats['profit_loss_percent']:.1f}%)\n"
                f"🎲 Ticks überlebt: {stats['ticks']}\n"
                f"🏆 Final Score: {stats['score']:,.1f}\n"
                "═══════════════════\n\n"
                f"{leaderboard_text}"
            )

            keyboard = [
                [
                    InlineKeyboardButton("🎮 Ape in again", callback_data='getrekt'),
                    InlineKeyboardButton("🐦 Share on Twitter", url=tweet_url)
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(message, reply_markup=reply_markup)
            logging.info("Sell complete – cleaning up game state")
            context.user_data.pop('game', None)
            return LEVERAGE  # Zurück zum Start für ein neues Spiel

        # --- CONTINUE (TRADE) FLOW: Run animation for price movement ---
        game.price_steps = []
        game.generate_price_movement()
        ANIMATION_DELAY = 0.5  # Konsistente Verzögerung zwischen Preisupdates

        for current_price in game.price_steps:
            try:
                game.current_price = current_price
                logging.info(f"Price step: current_price={current_price}, liq_price={game.calculate_liquidation_price()}")

                # Berechne temporären P&L für diesen Schritt
                temp_pl = game.position_size * ((current_price - game.initial_price) / game.initial_price) * game.leverage
                price_change = ((current_price - game.initial_price) / game.initial_price) * 100

                # Prüfe auf Liquidation während der Animation
                if current_price <= game.calculate_liquidation_price():
                    logging.info("Liquidation während Animation erkannt")
                    game.is_liquidated = True
                    game.profit_loss = -game.position_size
                    game.increment_tick()
                    stats = game.get_stats()

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
                    keyboard = [[InlineKeyboardButton("🎮 Ape in again", callback_data='getrekt')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.edit_message_text(message, reply_markup=reply_markup)
                    logging.info("Liquidation complete – cleaning up game state")
                    context.user_data.pop('game', None)
                    return LEVERAGE

                # Dynamische Updates während der Animation
                trend_emoji = "📈" if price_change > 0 else "📉"
                move_emoji = "🚀" if price_change > 5 else "📈" if price_change > 0 else "📉" if price_change > -5 else "💥"
                status_msg = "PUMP IT! 🚀" if price_change > 5 else "Number go up! 📈" if price_change > 0 else "Dip buying time! 🎯" if price_change > -5 else "DAMP IT! 📉"

                portfolio_value = game.calculate_portfolio_value()
                portfolio_change = ((portfolio_value / game.position_size) - 1) * 100
                portfolio_emoji = "🐋" if portfolio_change > 50 else "🦍" if portfolio_change > 20 else "🐂" if portfolio_change > 0 else "🐻" if portfolio_change > -10 else "💀"
                pl_emoji = "🤑" if temp_pl > 0 else "🤡"

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
                    await query.edit_message_text(message, reply_markup=None)
                except telegram.BadRequest as e:
                    if "message is not modified" not in str(e).lower():
                        raise

                await asyncio.sleep(ANIMATION_DELAY)
            except telegram.BadRequest as e:
                if "message is not modified" not in str(e).lower():
                    raise
                await asyncio.sleep(0.2)
                continue

        # Finaler Update nach der Animation (falls nicht liquidiert)
        if game.update_price():  # Gibt True zurück, falls nach der Animation liquidiert wird
            logging.info("Liquidation nach Animation erkannt")
            stats = game.get_stats()
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
            keyboard = [[InlineKeyboardButton("🎮 Neues Spiel", callback_data='getrekt')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(message, reply_markup=reply_markup)
            logging.info("Game ended by liquidation after animation – cleaning up state")
            context.user_data.pop('game', None)
            return LEVERAGE

        # Falls nicht liquidiert, zeige die aktualisierte Performance mit Optionen "Weiter" oder "Verkaufen"
        stats = game.get_stats()
        logging.info(f"Finale Stats: {stats}")
        result_msg = (
            "GIGACHAD MOVE! 🐋" if stats['profit_loss'] > game.position_size else
            "NICE GAINS BRO! 🦍" if stats['profit_loss'] > 0 else
            "NGMI BRUH... 🤡"
        )
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
        keyboard = [
            [
                InlineKeyboardButton("🎲 Diamond Hands", callback_data='trade'),
                InlineKeyboardButton("💰 Panic Sell", callback_data='quit')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.edit_message_text(message, reply_markup=reply_markup)
        except telegram.BadRequest as e:
            if "message is not modified" not in str(e).lower():
                logging.error(f"Fehler beim Update der Nachricht: {str(e)}")
                await query.edit_message_text("⚠️ There was an error\nTry to start again")
                context.user_data.pop('game', None)
                return ConversationHandler.END

        return TRADING

    except Exception as e:
        logging.error(f"Fehler im Trade Handler: {str(e)}")
        try:
            await query.edit_message_text("⚠️ There was an error\nTry to start again")
            context.user_data.pop('game', None)
        except Exception:
            pass
        return ConversationHandler.END
