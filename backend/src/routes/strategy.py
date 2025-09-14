from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.strategy import Strategy
import json

strategy_bp = Blueprint('strategy', __name__)

@strategy_bp.route('/strategies', methods=['GET'])
def get_strategies():
    """Get all strategies for a user"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    try:
        strategies = Strategy.query.filter_by(user_id=user_id).all()
        return jsonify([strategy.to_dict() for strategy in strategies])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@strategy_bp.route('/strategies', methods=['POST'])
def create_strategy():
    """Create a new strategy"""
    data = request.get_json()
    
    required_fields = ['user_id', 'name', 'strategy_type']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    try:
        # Parse time strings if provided
        start_time_obj = None
        end_time_obj = None
        
        if data.get('start_time'):
            from datetime import datetime
            start_time_obj = datetime.strptime(data['start_time'], '%H:%M').time()
        
        if data.get('end_time'):
            from datetime import datetime
            end_time_obj = datetime.strptime(data['end_time'], '%H:%M').time()
        
        strategy = Strategy(
            user_id=data['user_id'],
            name=data['name'],
            strategy_type=data['strategy_type'],
            is_active=data.get('is_active', False),
            schedule_enabled=data.get('schedule_enabled', False),
            start_time=start_time_obj,
            end_time=end_time_obj,
            timezone=data.get('timezone', 'America/Sao_Paulo')
        )
        
        if 'config' in data:
            strategy.set_config(data['config'])
        
        if 'days_of_week' in data:
            strategy.set_days_of_week(data['days_of_week'])
        
        db.session.add(strategy)
        db.session.commit()
        
        return jsonify(strategy.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@strategy_bp.route('/strategies/<int:strategy_id>', methods=['GET'])
def get_strategy(strategy_id):
    """Get a specific strategy"""
    try:
        strategy = Strategy.query.get_or_404(strategy_id)
        return jsonify(strategy.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@strategy_bp.route('/strategies/<int:strategy_id>', methods=['PUT'])
def update_strategy(strategy_id):
    """Update a strategy"""
    data = request.get_json()
    
    try:
        strategy = Strategy.query.get_or_404(strategy_id)
        
        if 'name' in data:
            strategy.name = data['name']
        if 'is_active' in data:
            strategy.is_active = data['is_active']
        if 'config' in data:
            strategy.set_config(data['config'])
        
        # Update scheduling fields
        if 'schedule_enabled' in data:
            strategy.schedule_enabled = data['schedule_enabled']
        
        if 'start_time' in data:
            if data['start_time']:
                from datetime import datetime
                strategy.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
            else:
                strategy.start_time = None
        
        if 'end_time' in data:
            if data['end_time']:
                from datetime import datetime
                strategy.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
            else:
                strategy.end_time = None
        
        if 'days_of_week' in data:
            strategy.set_days_of_week(data['days_of_week'])
        
        if 'timezone' in data:
            strategy.timezone = data['timezone']
        
        db.session.commit()
        return jsonify(strategy.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@strategy_bp.route('/strategies/<int:strategy_id>', methods=['DELETE'])
def delete_strategy(strategy_id):
    """Delete a strategy"""
    try:
        strategy = Strategy.query.get_or_404(strategy_id)
        db.session.delete(strategy)
        db.session.commit()
        return jsonify({'message': 'Strategy deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@strategy_bp.route('/strategies/<int:strategy_id>/toggle', methods=['POST'])
def toggle_strategy(strategy_id):
    """Toggle strategy active status"""
    try:
        strategy = Strategy.query.get_or_404(strategy_id)
        strategy.is_active = not strategy.is_active
        db.session.commit()
        return jsonify({
            'message': f'Strategy {"activated" if strategy.is_active else "deactivated"}',
            'is_active': strategy.is_active
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

