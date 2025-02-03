# File: src/models/leaderboard.py

import json
import os
from datetime import datetime, date
import calendar
from typing import List, Dict

class Leaderboard:
    def __init__(self, file_path: str = "data/leaderboard.json"):
        # Stelle sicher, dass der data-Ordner existiert
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        self.file_path = file_path
        self.scores: List[Dict] = []
        self.load()
    
    def load(self):
        """Lädt die Bestenliste aus der JSON-Datei"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    self.scores = json.load(f)
            except json.JSONDecodeError:
                self.scores = []
        else:
            self.scores = []
    
    def save(self):
        """Speichert die Bestenliste in die JSON-Datei"""
        with open(self.file_path, 'w') as f:
            json.dump(self.scores, f, indent=2)
    
    def add_score(self, username: str, score: float, leverage: int, pnl: float, ticks: int):
        """
        Fügt einen Score zur Bestenliste hinzu. 
        Wenn ein Eintrag vom gleichen User existiert und der neue Score besser ist, wird der alte Eintrag gelöscht.
        """
        # Überprüfe, ob es bereits einen Eintrag für den User gibt
        existing_entry = None
        for entry in self.scores:
            if entry['username'] == username:
                existing_entry = entry
                break
        
        # Falls ein Eintrag existiert und der neue Score besser ist, entferne ihn
        if existing_entry:
            if score > existing_entry['score']:
                self.scores.remove(existing_entry)
            else:
                # Neuer Score ist nicht besser – nix ändern
                return
        
        # Neuer Eintrag
        new_entry = {
            'username': username,
            'score': score,
            'leverage': leverage,
            'pnl': pnl,
            'ticks': ticks,
            'timestamp': datetime.now().isoformat()
        }
        self.scores.append(new_entry)
        
        # Sortiere die Scores in absteigender Reihenfolge und behalte nur die Top 10
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        self.scores = self.scores[:10]
        
        self.save()
    
    def get_top_10(self) -> List[Dict]:
        """Gibt die Top 10 Scores zurück"""
        return self.scores[:10]
    
    def clear(self):
        """Löscht die Bestenliste"""
        self.scores = []
        self.save()
    
    def get_prize_date(self) -> str:
        """
        Berechnet das variable Datum, an dem die Preise ausgezahlt werden.
        Hier: Letzter Tag des aktuellen Monats im Format DD.MM.YYYY.
        """
        today = date.today()
        last_day = calendar.monthrange(today.year, today.month)[1]
        prize_date = date(today.year, today.month, last_day)
        return prize_date.strftime("%d.%m.%Y")
    
    def format_leaderboard(self) -> str:
        """
        Formatiert die Bestenliste als ansprechende Nachricht mit UDEGEN-Slang, Icons und Preisinformationen.
        """
        if not self.scores:
            leaderboard_text = (
                "🏆 DEGEN LEADERBOARD 🏆\n"
                "═══════════════════\n"
                "No trades yet... be the first degen!\n"
                "═══════════════════"
            )
        else:
            leaderboard_text = "🏆 DEGEN LEADERBOARD 🏆\n═══════════════════\n"
            for i, entry in enumerate(self.scores[:10]):
                # Medal emojis for the top spots
                position_emoji = {0: "🥇", 1: "🥈", 2: "🥉"}.get(i, "🎖️")
                username = entry['username']
                if not username.startswith('@'):
                    username = f"@{username}"
                leaderboard_text += f"{position_emoji} {i+1}. {username}\n"
                leaderboard_text += f"   💰 Score: {entry['score']:.1f}\n"
                leaderboard_text += f"   ⚡ {entry['leverage']}x | 💵 ${entry['pnl']:,.2f} | 🎲 {entry['ticks']} ticks\n"
                # Add prizes for the Top 3 with a savage degen twist
                if i == 0:
                    leaderboard_text += "   🎉 Prize: $100 in $UDEGEN – Top Degen Alert!\n"
                elif i == 1:
                    leaderboard_text += "   🎉 Prize: $50 in $UDEGEN – Solid Degen Move!\n"
                elif i == 2:
                    leaderboard_text += "   🎉 Prize: $25 in $UDEGEN – Rookie Reward!\n"
                leaderboard_text += "\n"
            leaderboard_text += "═══════════════════\n"

        # Append dynamic prize payout date
        prize_date = self.get_prize_date()
        leaderboard_text += f"🗓️ Prizes drop on {prize_date} – Mark your calendar, degen!\n"
        leaderboard_text += "🚀 Keep hustlin' and trade like a true degen, or get rekt trying!\n"
            
        # Append the Twitter share link
        
        return leaderboard_text
