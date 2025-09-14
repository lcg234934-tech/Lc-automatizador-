from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, time
import json

db = SQLAlchemy()

class Strategy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    strategy_type = db.Column(db.String(50), nullable=False)  # 'terminal_8', '3x3_pattern', '2x7_pattern'
    is_active = db.Column(db.Boolean, default=False)
    config_json = db.Column(db.Text, nullable=True)  # JSON string with strategy-specific config
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Campos de agendamento
    schedule_enabled = db.Column(db.Boolean, default=False)
    start_time = db.Column(db.Time, nullable=True)  # Horário de início (ex: 09:00)
    end_time = db.Column(db.Time, nullable=True)    # Horário de fim (ex: 18:00)
    days_of_week = db.Column(db.String(20), nullable=True)  # JSON array: [1,2,3,4,5] (seg-sex)
    timezone = db.Column(db.String(50), default='America/Sao_Paulo')

    def __repr__(self):
        return f'<Strategy {self.name}>'
    
    def get_days_of_week(self):
        """Parse and return days of week as list"""
        try:
            return json.loads(self.days_of_week) if self.days_of_week else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_days_of_week(self, days_list):
        """Set days of week from list"""
        self.days_of_week = json.dumps(days_list) if days_list else None
    
    def is_active_now(self):
        """Check if strategy should be active based on current time and schedule"""
        if not self.is_active:
            return False
        
        if not self.schedule_enabled:
            return True  # Always active if no schedule is set
        
        try:
            # Get current time (using system timezone for simplicity)
            now = datetime.now()
            current_time = now.time()
            current_weekday = now.weekday() + 1  # Monday = 1, Sunday = 7
            
            # Check if current day is in allowed days
            allowed_days = self.get_days_of_week()
            if allowed_days and current_weekday not in allowed_days:
                return False
            
            # Check if current time is within allowed time range
            if self.start_time and self.end_time:
                if self.start_time <= self.end_time:
                    # Same day range (e.g., 09:00 to 18:00)
                    return self.start_time <= current_time <= self.end_time
                else:
                    # Overnight range (e.g., 22:00 to 06:00)
                    return current_time >= self.start_time or current_time <= self.end_time
            
            return True
            
        except Exception as e:
            # If there's any error with time calculation, default to active
            print(f"Error checking schedule for strategy {self.id}: {e}")
            return True

    def to_dict(self):
        config = {}
        if self.config_json:
            try:
                config = json.loads(self.config_json)
            except json.JSONDecodeError:
                config = {}
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'strategy_type': self.strategy_type,
            'is_active': self.is_active,
            'config': config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'schedule_enabled': self.schedule_enabled,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'days_of_week': self.get_days_of_week(),
            'timezone': self.timezone,
            'is_active_now': self.is_active_now()
        }

    def set_config(self, config_dict):
        """Set configuration as JSON string"""
        self.config_json = json.dumps(config_dict)

    def get_config(self):
        """Get configuration as dictionary"""
        if self.config_json:
            try:
                return json.loads(self.config_json)
            except json.JSONDecodeError:
                return {}
        return {}

