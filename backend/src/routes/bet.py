from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.bet import Bet
from datetime import datetime, date
import json

bet_bp = Blueprint('bet', __name__)

@bet_bp.route('/bets', methods=['GET'])
def get_bets():
    """Get bets for a user with optional filters"""
    user_id = request.args.get('user_id')
    strategy_id = request.args.get('strategy_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    try:
        query = Bet.query.filter_by(user_id=user_id)
        
        if strategy_id:
            query = query.filter_by(strategy_id=strategy_id)
        
        if start_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Bet.bet_time >= start_date_obj)
        
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Bet.bet_time <= end_date_obj)
        
        bets = query.order_by(Bet.bet_time.desc()).all()
        return jsonify([bet.to_dict() for bet in bets])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bet_bp.route('/bets', methods=['POST'])
def create_bet():
    """Create a new bet record"""
    data = request.get_json()
    
    required_fields = ['user_id', 'strategy_id', 'betting_house', 'roulette_type', 'bet_amount', 'bet_numbers']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    try:
        bet = Bet(
            user_id=data['user_id'],
            strategy_id=data['strategy_id'],
            betting_house=data['betting_house'],
            roulette_type=data['roulette_type'],
            bet_amount=data['bet_amount'],
            bet_numbers=json.dumps(data['bet_numbers']) if isinstance(data['bet_numbers'], (dict, list)) else data['bet_numbers'],
            outcome_number=data.get('outcome_number'),
            profit_loss=data.get('profit_loss', 0.0),
            status=data.get('status', 'pending')
        )
        
        db.session.add(bet)
        db.session.commit()
        
        return jsonify(bet.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bet_bp.route('/bets/<int:bet_id>', methods=['PUT'])
def update_bet(bet_id):
    """Update bet outcome and profit/loss"""
    data = request.get_json()
    
    try:
        bet = Bet.query.get_or_404(bet_id)
        
        if 'outcome_number' in data:
            bet.outcome_number = data['outcome_number']
        if 'profit_loss' in data:
            bet.profit_loss = data['profit_loss']
        if 'status' in data:
            bet.status = data['status']
        
        db.session.commit()
        return jsonify(bet.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bet_bp.route('/bets/stats', methods=['GET'])
def get_bet_stats():
    """Get betting statistics for a user"""
    user_id = request.args.get('user_id')
    period = request.args.get('period', 'all')  # 'day', 'week', 'month', 'all'
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    try:
        query = Bet.query.filter_by(user_id=user_id)
        
        # Filter by period
        if period == 'day':
            today = date.today()
            query = query.filter(Bet.bet_time >= today)
        elif period == 'week':
            from datetime import timedelta
            week_ago = date.today() - timedelta(days=7)
            query = query.filter(Bet.bet_time >= week_ago)
        elif period == 'month':
            from datetime import timedelta
            month_ago = date.today() - timedelta(days=30)
            query = query.filter(Bet.bet_time >= month_ago)
        
        bets = query.all()
        
        total_bets = len(bets)
        total_profit = sum(bet.profit_loss for bet in bets)
        winning_bets = len([bet for bet in bets if bet.profit_loss > 0])
        losing_bets = len([bet for bet in bets if bet.profit_loss < 0])
        win_rate = (winning_bets / total_bets * 100) if total_bets > 0 else 0
        
        return jsonify({
            'period': period,
            'total_bets': total_bets,
            'total_profit': total_profit,
            'winning_bets': winning_bets,
            'losing_bets': losing_bets,
            'win_rate': win_rate
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

