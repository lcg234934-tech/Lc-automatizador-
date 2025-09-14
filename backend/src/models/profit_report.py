from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

class ProfitReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    report_date = db.Column(db.Date, default=date.today)
    daily_profit = db.Column(db.Float, default=0.0)
    weekly_profit = db.Column(db.Float, default=0.0)
    monthly_profit = db.Column(db.Float, default=0.0)
    total_bets = db.Column(db.Integer, default=0)
    winning_bets = db.Column(db.Integer, default=0)
    losing_bets = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ProfitReport {self.report_date} - User {self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'report_date': self.report_date.isoformat() if self.report_date else None,
            'daily_profit': self.daily_profit,
            'weekly_profit': self.weekly_profit,
            'monthly_profit': self.monthly_profit,
            'total_bets': self.total_bets,
            'winning_bets': self.winning_bets,
            'losing_bets': self.losing_bets,
            'win_rate': (self.winning_bets / self.total_bets * 100) if self.total_bets > 0 else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

