from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from src.models.leaderboard import Leaderboard
import os
import logging
import sys
import subprocess

class AdminHandler:
    def __init__(self, leaderboard: Leaderboard, admin_ids=None, lock=None):
        self.leaderboard = leaderboard
        self.admin_ids = admin_ids or []
        self.lock = lock
        
    def is_admin(self, user_id: int) -> bool:
        """Überprüft, ob ein User Admin ist"""
        return user_id in self.admin_ids
    
    async def clear_leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler für das Löschen der Bestenliste"""
        if not update.message:
            return ConversationHandler.END
            
        user_id = update.message.from_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("⛔ Only admins can use this command!")
            return ConversationHandler.END
            
        try:
            self.leaderboard.clear()
            await update.message.reply_text(
                "✅ Leaderboard has been cleared!\n"
                "───────────────\n"
                "🧹 All scores deleted\n"
                "🎮 Ready for new highscores!"
            )
            logging.info(f"Leaderboard cleared by admin {user_id}")
        except Exception as e:
            logging.error(f"Error clearing leaderboard: {e}")
            await update.message.reply_text("❌ Error clearing leaderboard!")
        
        return ConversationHandler.END
        
    async def stop_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler to stop the bot"""
        if not update.message:
            return
            
        user_id = update.message.from_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("⛔ Only admins can use this command!")
            return
            
        try:
            await update.message.reply_text("🛑 Stopping bot... Goodbye!")
            logging.info(f"Bot stop initiated by admin {user_id}")
            if self.lock:
                self.lock.release()
            # Give message time to send before exit
            await context.application.stop()
            sys.exit(0)
        except Exception as e:
            logging.error(f"Error stopping bot: {e}")
            await update.message.reply_text("❌ Error stopping bot!")
            
    async def restart_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler to restart the bot"""
        if not update.message:
            return
            
        user_id = update.message.from_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("⛔ Only admins can use this command!")
            return
            
        try:
            await update.message.reply_text("🔄 Restarting bot... See you in a sec!")
            logging.info(f"Bot restart initiated by admin {user_id}")
            if self.lock:
                self.lock.release()
            # Start new process
            subprocess.Popen([sys.executable, sys.argv[0]])
            # Give message time to send before exit
            await context.application.stop()
            sys.exit(0)
        except Exception as e:
            logging.error(f"Error restarting bot: {e}")
            await update.message.reply_text("❌ Error restarting bot!")

    async def clean_leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Cleans the leaderboard."""
        self.leaderboard.clear()
        await update.message.reply_text("Leaderboard has been cleared!")

    async def show_leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Shows the current leaderboard."""
        leaderboard_text = self.leaderboard.format_leaderboard()
        await update.message.reply_text(leaderboard_text)
