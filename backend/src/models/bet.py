from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Bet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategy.id'), nullable=False)
    betting_house = db.Column(db.String(50), nullable=False)  # 'betfair', '1pra1bet', 'sportingbet'
    roulette_type = db.Column(db.String(50), nullable=False)  # 'evolution', 'playtech'
    bet_time = db.Column(db.DateTime, default=datetime.utcnow)
    bet_amount = db.Column(db.Float, nullable=False)
    bet_numbers = db.Column(db.Text, nullable=False)  # JSON string with bet details
    outcome_number = db.Column(db.Integer, nullable=True)  # The winning number
    profit_loss = db.Column(db.Float, default=0.0)  # Positive for profit, negative for loss
    status = db.Column(db.String(20), default='pending')  # 'pending', 'won', 'lost'

    def __repr__(self):
        return f'<Bet {self.id} - {self.status}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'strategy_id': self.strategy_id,
            'betting_house': self.betting_house,
            'roulette_type': self.roulette_type,
            'bet_time': self.bet_time.isoformat() if self.bet_time else None,
            'bet_amount': self.bet_amount,
            'bet_numbers': self.bet_numbers,
            'outcome_number': self.outcome_number,
            'profit_loss': self.profit_loss,
            'status': self.status
        }

