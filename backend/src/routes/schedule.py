from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.strategy import Strategy
from src.strategies.strategy_logic import check_strategy_schedule_status
import json

schedule_bp = Blueprint('schedule', __name__)

@schedule_bp.route('/schedule/status/<int:user_id>', methods=['GET'])
def get_schedule_status(user_id):
    """Get schedule status for all strategies of a user"""
    try:
        status = check_strategy_schedule_status(user_id)
        return jsonify(status), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@schedule_bp.route('/schedule/strategy/<int:strategy_id>', methods=['PUT'])
def update_strategy_schedule(strategy_id):
    """Update schedule settings for a specific strategy"""
    data = request.get_json()
    
    try:
        strategy = Strategy.query.get_or_404(strategy_id)
        
        # Update schedule fields
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
        
        return jsonify({
            'message': 'Schedule updated successfully',
            'strategy': strategy.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@schedule_bp.route('/schedule/bulk-update', methods=['PUT'])
def bulk_update_schedules():
    """Update schedule settings for multiple strategies"""
    data = request.get_json()
    user_id = data.get('user_id')
    schedule_settings = data.get('schedule_settings', {})
    strategy_ids = data.get('strategy_ids', [])
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    try:
        # Get strategies to update
        if strategy_ids:
            strategies = Strategy.query.filter(
                Strategy.id.in_(strategy_ids),
                Strategy.user_id == user_id
            ).all()
        else:
            strategies = Strategy.query.filter_by(user_id=user_id).all()
        
        updated_count = 0
        
        for strategy in strategies:
            # Apply schedule settings
            if 'schedule_enabled' in schedule_settings:
                strategy.schedule_enabled = schedule_settings['schedule_enabled']
            
            if 'start_time' in schedule_settings:
                if schedule_settings['start_time']:
                    from datetime import datetime
                    strategy.start_time = datetime.strptime(schedule_settings['start_time'], '%H:%M').time()
                else:
                    strategy.start_time = None
            
            if 'end_time' in schedule_settings:
                if schedule_settings['end_time']:
                    from datetime import datetime
                    strategy.end_time = datetime.strptime(schedule_settings['end_time'], '%H:%M').time()
                else:
                    strategy.end_time = None
            
            if 'days_of_week' in schedule_settings:
                strategy.set_days_of_week(schedule_settings['days_of_week'])
            
            if 'timezone' in schedule_settings:
                strategy.timezone = schedule_settings['timezone']
            
            updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'Updated schedule for {updated_count} strategies',
            'updated_count': updated_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@schedule_bp.route('/schedule/presets', methods=['GET'])
def get_schedule_presets():
    """Get predefined schedule presets"""
    presets = {
        'business_hours': {
            'name': 'Horário Comercial',
            'description': 'Segunda a sexta, 9h às 18h',
            'schedule_enabled': True,
            'start_time': '09:00',
            'end_time': '18:00',
            'days_of_week': [1, 2, 3, 4, 5],  # Mon-Fri
            'timezone': 'America/Sao_Paulo'
        },
        'evening_only': {
            'name': 'Apenas Noite',
            'description': 'Todos os dias, 19h às 23h',
            'schedule_enabled': True,
            'start_time': '19:00',
            'end_time': '23:00',
            'days_of_week': [1, 2, 3, 4, 5, 6, 7],  # All days
            'timezone': 'America/Sao_Paulo'
        },
        'weekends_only': {
            'name': 'Apenas Fins de Semana',
            'description': 'Sábado e domingo, 24h',
            'schedule_enabled': True,
            'start_time': '00:00',
            'end_time': '23:59',
            'days_of_week': [6, 7],  # Sat-Sun
            'timezone': 'America/Sao_Paulo'
        },
        'always_active': {
            'name': 'Sempre Ativo',
            'description': 'Sem restrições de horário',
            'schedule_enabled': False,
            'start_time': None,
            'end_time': None,
            'days_of_week': [],
            'timezone': 'America/Sao_Paulo'
        },
        'custom_morning': {
            'name': 'Manhã Personalizada',
            'description': 'Segunda a sexta, 6h às 12h',
            'schedule_enabled': True,
            'start_time': '06:00',
            'end_time': '12:00',
            'days_of_week': [1, 2, 3, 4, 5],  # Mon-Fri
            'timezone': 'America/Sao_Paulo'
        },
        'night_shift': {
            'name': 'Turno da Noite',
            'description': 'Todos os dias, 22h às 6h',
            'schedule_enabled': True,
            'start_time': '22:00',
            'end_time': '06:00',
            'days_of_week': [1, 2, 3, 4, 5, 6, 7],  # All days
            'timezone': 'America/Sao_Paulo'
        }
    }
    
    return jsonify(presets), 200

@schedule_bp.route('/schedule/apply-preset', methods=['POST'])
def apply_schedule_preset():
    """Apply a schedule preset to strategies"""
    data = request.get_json()
    user_id = data.get('user_id')
    preset_name = data.get('preset_name')
    strategy_ids = data.get('strategy_ids', [])
    
    if not all([user_id, preset_name]):
        return jsonify({'error': 'user_id and preset_name are required'}), 400
    
    try:
        # Get preset settings
        presets_response = get_schedule_presets()
        presets = presets_response[0].get_json()
        
        if preset_name not in presets:
            return jsonify({'error': 'Invalid preset name'}), 400
        
        preset_settings = presets[preset_name]
        
        # Get strategies to update
        if strategy_ids:
            strategies = Strategy.query.filter(
                Strategy.id.in_(strategy_ids),
                Strategy.user_id == user_id
            ).all()
        else:
            strategies = Strategy.query.filter_by(user_id=user_id).all()
        
        updated_count = 0
        
        for strategy in strategies:
            strategy.schedule_enabled = preset_settings['schedule_enabled']
            
            if preset_settings['start_time']:
                from datetime import datetime
                strategy.start_time = datetime.strptime(preset_settings['start_time'], '%H:%M').time()
            else:
                strategy.start_time = None
            
            if preset_settings['end_time']:
                from datetime import datetime
                strategy.end_time = datetime.strptime(preset_settings['end_time'], '%H:%M').time()
            else:
                strategy.end_time = None
            
            strategy.set_days_of_week(preset_settings['days_of_week'])
            strategy.timezone = preset_settings['timezone']
            
            updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'Applied preset "{preset_settings["name"]}" to {updated_count} strategies',
            'preset_applied': preset_settings['name'],
            'updated_count': updated_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

