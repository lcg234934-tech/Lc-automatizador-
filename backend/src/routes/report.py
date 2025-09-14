from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.bet import Bet
from src.models.profit_report import ProfitReport
from datetime import datetime, date, timedelta
from sqlalchemy import func

report_bp = Blueprint('report', __name__)

@report_bp.route('/reports/profit', methods=['GET'])
def get_profit_report():
    """Get profit report for a user"""
    user_id = request.args.get('user_id')
    period = request.args.get('period', 'month')  # 'day', 'week', 'month'
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    try:
        today = date.today()
        
        # Calculate date ranges
        if period == 'day':
            start_date = today
            end_date = today
        elif period == 'week':
            start_date = today - timedelta(days=today.weekday())  # Start of week (Monday)
            end_date = start_date + timedelta(days=6)  # End of week (Sunday)
        else:  # month
            start_date = today.replace(day=1)  # Start of month
            next_month = start_date.replace(month=start_date.month + 1) if start_date.month < 12 else start_date.replace(year=start_date.year + 1, month=1)
            end_date = next_month - timedelta(days=1)  # End of month
        
        # Query bets in the period
        bets = Bet.query.filter(
            Bet.user_id == user_id,
            Bet.bet_time >= start_date,
            Bet.bet_time <= end_date
        ).all()
        
        # Calculate statistics
        total_profit = sum(bet.profit_loss for bet in bets)
        total_bets = len(bets)
        winning_bets = len([bet for bet in bets if bet.profit_loss > 0])
        losing_bets = len([bet for bet in bets if bet.profit_loss < 0])
        win_rate = (winning_bets / total_bets * 100) if total_bets > 0 else 0
        
        # Group by strategy
        strategy_stats = {}
        for bet in bets:
            strategy_id = bet.strategy_id
            if strategy_id not in strategy_stats:
                strategy_stats[strategy_id] = {
                    'strategy_id': strategy_id,
                    'total_bets': 0,
                    'total_profit': 0,
                    'winning_bets': 0,
                    'losing_bets': 0
                }
            
            strategy_stats[strategy_id]['total_bets'] += 1
            strategy_stats[strategy_id]['total_profit'] += bet.profit_loss
            if bet.profit_loss > 0:
                strategy_stats[strategy_id]['winning_bets'] += 1
            elif bet.profit_loss < 0:
                strategy_stats[strategy_id]['losing_bets'] += 1
        
        # Calculate win rate for each strategy
        for strategy_id in strategy_stats:
            stats = strategy_stats[strategy_id]
            stats['win_rate'] = (stats['winning_bets'] / stats['total_bets'] * 100) if stats['total_bets'] > 0 else 0
        
        return jsonify({
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_profit': total_profit,
            'total_bets': total_bets,
            'winning_bets': winning_bets,
            'losing_bets': losing_bets,
            'win_rate': win_rate,
            'strategy_breakdown': list(strategy_stats.values())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/reports/daily-profit', methods=['GET'])
def get_daily_profit():
    """Get daily profit data for charts"""
    user_id = request.args.get('user_id')
    days = int(request.args.get('days', 30))  # Default to last 30 days
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Query bets grouped by date
        daily_profits = db.session.query(
            func.date(Bet.bet_time).label('bet_date'),
            func.sum(Bet.profit_loss).label('daily_profit'),
            func.count(Bet.id).label('bet_count')
        ).filter(
            Bet.user_id == user_id,
            Bet.bet_time >= start_date,
            Bet.bet_time <= end_date
        ).group_by(func.date(Bet.bet_time)).all()
        
        # Create a complete date range with zero profits for missing days
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date)
            current_date += timedelta(days=1)
        
        # Map query results to date range
        profit_dict = {row.bet_date: {'profit': float(row.daily_profit), 'bets': row.bet_count} for row in daily_profits}
        
        result = []
        cumulative_profit = 0
        for date_item in date_range:
            daily_data = profit_dict.get(date_item, {'profit': 0, 'bets': 0})
            cumulative_profit += daily_data['profit']
            
            result.append({
                'date': date_item.isoformat(),
                'daily_profit': daily_data['profit'],
                'cumulative_profit': cumulative_profit,
                'bet_count': daily_data['bets']
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/reports/strategy-performance', methods=['GET'])
def get_strategy_performance():
    """Get performance comparison between strategies"""
    user_id = request.args.get('user_id')
    days = int(request.args.get('days', 30))
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Query strategy performance
        strategy_performance = db.session.query(
            Bet.strategy_id,
            func.sum(Bet.profit_loss).label('total_profit'),
            func.count(Bet.id).label('total_bets'),
            func.sum(func.case([(Bet.profit_loss > 0, 1)], else_=0)).label('winning_bets'),
            func.sum(func.case([(Bet.profit_loss < 0, 1)], else_=0)).label('losing_bets')
        ).filter(
            Bet.user_id == user_id,
            Bet.bet_time >= start_date,
            Bet.bet_time <= end_date
        ).group_by(Bet.strategy_id).all()
        
        result = []
        for row in strategy_performance:
            win_rate = (row.winning_bets / row.total_bets * 100) if row.total_bets > 0 else 0
            result.append({
                'strategy_id': row.strategy_id,
                'total_profit': float(row.total_profit),
                'total_bets': row.total_bets,
                'winning_bets': row.winning_bets,
                'losing_bets': row.losing_bets,
                'win_rate': win_rate,
                'avg_profit_per_bet': float(row.total_profit) / row.total_bets if row.total_bets > 0 else 0
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

