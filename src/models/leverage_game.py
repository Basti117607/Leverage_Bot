import random
import numpy as np
from datetime import datetime

class LeverageGame:
    def __init__(self):
        self._leverage = 1
        self.position_size = 1000
        self._initial_price = 100
        self.current_price = 100
        self.is_liquidated = False
        self.profit_loss = 0
        self.history = []
        self.price_steps = []  # Für die Animation
        self.ticks = 0
        self.start_time = datetime.now()  # Initialize start_time
        self.alpha = 0.5  # Hebelgewichtung für Score-Berechnung
        self._calculate_liquidation_price()  # Einmalige Berechnung
    
    @property
    def leverage(self):
        return self._leverage
    
    @leverage.setter
    def leverage(self, value):
        # Setze den Hebel, aber berechne den Liquidierungspreis nicht neu,
        # wenn das Spiel bereits gestartet wurde (ticks > 0).
        if self.ticks == 0:
            self._leverage = value
            self._calculate_liquidation_price()
        else:
            self._leverage = value  # Falls sich der Hebel ändert, bleibt der alte Liquidierungspreis erhalten.
    
    @property
    def initial_price(self):
        return self._initial_price
    
    @initial_price.setter
    def initial_price(self, value):
        # Ähnlich: Beim Setzen des Initialpreises den Liquidierungspreis nur aktualisieren, wenn das Spiel noch nicht gestartet wurde.
        if self.ticks == 0:
            self._initial_price = value
            self._calculate_liquidation_price()
        else:
            self._initial_price = value

    def _calculate_liquidation_price(self):
        """Interne Methode zur Berechnung des Liquidationspreises basierend auf initialem Hebel und Initialpreis"""
        if self._leverage <= 1:
            self.liquidation_price = 0
        else:
            liquidation_threshold = 1 / self._leverage
            self.liquidation_price = self._initial_price * (1 - liquidation_threshold)

    
    def increment_tick(self):
        """Erhöht den Tick-Counter"""
        self.ticks += 1
    
    def reset_time(self):
        """Setzt die Startzeit zurück"""
        self.start_time = datetime.now()
    
    def get_elapsed_time(self):
        """Gibt die verstrichene Zeit in Sekunden zurück"""
        return round((datetime.now() - self.start_time).total_seconds(), 1)
    
    def calculate_liquidation_price(self):
        """Gibt den Liquidationspreis zurück"""
        return self.liquidation_price
    
    def generate_price_movement(self):
        """Generiert eine Reihe von Preisbewegungen für die Animation"""
        # Basisvolatilität plus Hebel-Einfluss (reduziert)
        volatility = 0.002 * (1 + self.leverage/20)  # Reduzierte Basisvolatilität und Hebelwirkung
        steps = 3  # Reduziert auf 3 Schritte
        base_price = self.current_price  # Use base_price for continuous movement
        self.price_steps = []
        
        # Bestimme Trend (60% Chance für Aufwärtstrend bei niedrigem Hebel)
        trend_chance = max(0.4, 0.6 - (self.leverage/100))  # Hebel reduziert Chance auf Aufwärtstrend
        is_uptrend = random.random() < trend_chance
        
        for _ in range(steps):
            # Mehr Wahrscheinlichkeit für Bewegung in Trendrichtung
            if len(self.price_steps) > 0 and random.random() < 0.8:  # 80% Chance für Trendbewegung
                if is_uptrend:
                    change = random.uniform(0, volatility)
                else:
                    change = random.uniform(-volatility, 0)
            else:
                change = random.uniform(-volatility, volatility)
            
            new_price = base_price * (1 + change)
            
            # Verhindere zu große Preissprünge
            max_change = 0.05  # Maximale Änderung von 5%
            if abs(new_price - base_price) / base_price > max_change:
                if new_price > base_price:
                    new_price = base_price * (1 + max_change)
                else:
                    new_price = base_price * (1 - max_change)
            
            self.price_steps.append(new_price)
            base_price = new_price  # Update base_price for next step
        
        return self.price_steps
    
    def update_price(self):
        """Aktualisiert den Preis und berechnet P&L"""
        if not self.price_steps:
            self.generate_price_movement()
        
        # Verwende den letzten generierten Preis
        self.current_price = self.price_steps[-1]
        
        # Berechne P&L
        price_change_percent = (self.current_price - self.initial_price) / self.initial_price
        self.profit_loss = self.position_size * price_change_percent * self.leverage
        
        # Prüfe auf Liquidation
        if self.current_price <= self.calculate_liquidation_price():
            self.is_liquidated = True
            self.profit_loss = -self.position_size
            
        self.history.append(self.current_price)
        self.increment_tick()  # Erhöhe den Tick-Counter
        return self.is_liquidated
    
    def get_next_price_step(self):
        """Gibt den nächsten Preis für die Animation zurück"""
        if not self.price_steps:
            self.generate_price_movement()
            return self.price_steps[0]
        
        if len(self.price_steps) > 1:
            return self.price_steps.pop(0)
        else:
            # Generiere neue Schritte wenn alle verbraucht sind
            self.generate_price_movement()
            return self.price_steps[0]
    
    def calculate_score(self):
        """
        Berechnet den Score basierend auf dem Gewinn, der Positionsgröße, den überlebten Ticks und dem gewählten Hebel.
        Score = Profit% * Ticks * Hebel^alpha
        """
        if self.is_liquidated:
            return 0
        
        # Berechne den Profit-Prozentsatz
        profit_percent = (self.profit_loss / self.position_size) * 100
        # Berechne den Score: Profit% * Ticks * Hebel^alpha
        score = profit_percent * self.ticks * (self.leverage ** self.alpha)
        return score
    
    def calculate_portfolio_value(self):
        """Berechnet den aktuellen Portfoliowert inkl. Gewinn/Verlust"""
        return self.position_size + self.profit_loss

    def get_stats(self):
        """Gibt aktuelle Spielstatistiken zurück"""
        portfolio_value = self.calculate_portfolio_value()
        portfolio_change = ((portfolio_value / self.position_size) - 1) * 100
        
        return {
            'current_price': self.current_price,
            'initial_price': self.initial_price,
            'profit_loss': self.profit_loss,
            'profit_loss_percent': (self.profit_loss/self.position_size*100),
            'portfolio_value': portfolio_value,
            'portfolio_change': portfolio_change,
            'leverage': self.leverage,
            'position_size': self.position_size,
            'liquidation_price': self.calculate_liquidation_price(),
            'ticks': self.ticks,
            'duration': self.get_elapsed_time(),
            'price_trend': "📈" if self.current_price > self.initial_price else "📉",
            'score': self.calculate_score()
        }
