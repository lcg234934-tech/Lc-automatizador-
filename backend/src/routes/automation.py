from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.strategy import Strategy
from src.models.bet import Bet
from src.strategies.strategy_logic import StrategyLogic
from datetime import datetime
import json

automation_bp = Blueprint("automation", __name__)
strategy_logic = StrategyLogic()

@automation_bp.route("/automation/process_spin", methods=["POST"])
def process_spin():
    """Receives a roulette spin result and processes active strategies."""
    data = request.get_json()
    user_id = data.get("user_id")
    winning_number = data.get("winning_number")
    roulette_type = data.get("roulette_type") # e.g., 'evolution', 'playtech'
    betting_house = data.get("betting_house") # e.g., 'betfair', '1pra1bet', 'sportingbet'

    if not all([user_id, winning_number is not None, roulette_type, betting_house]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get active strategies for the user (considering schedule)
        from src.strategies.strategy_logic import get_active_strategies
        active_strategies = get_active_strategies(user_id)

        # Get recent history for strategy evaluation (e.g., last 10 spins)
        # This is a placeholder. In a real system, history would be managed more robustly.
        # For now, let's assume we get history from the client or a dedicated service.
        # For demonstration, we'll use a dummy history or fetch from recent bets.
        recent_bets = Bet.query.filter_by(user_id=user_id).order_by(Bet.bet_time.desc()).limit(10).all()
        history = [bet.outcome_number for bet in recent_bets if bet.outcome_number is not None]
        history.insert(0, winning_number) # Add current winning number to history

        bets_to_place = []

        for strategy in active_strategies:
            config = strategy.get_config()
            
            # Check if the strategy is configured for the current betting house
            if betting_house not in config.get("betting_houses", []):
                continue

            if strategy.strategy_type == "terminal_8":
                strategy_bets = strategy_logic.execute_strategy_terminal_8(history, config)
            elif strategy.strategy_type == "3x3_pattern":
                strategy_bets = strategy_logic.execute_strategy_3x3_pattern(history, config)
            elif strategy.strategy_type == "2x7_pattern":
                strategy_bets = strategy_logic.execute_strategy_2x7_pattern(history, config)
            else:
                strategy_bets = []

            if strategy_bets:
                for bet_detail in strategy_bets:
                    bets_to_place.append({
                        "user_id": user_id,
                        "strategy_id": strategy.id,
                        "betting_house": betting_house,
                        "roulette_type": roulette_type,
                        "bet_amount": bet_detail["amount"],
                        "bet_numbers": json.dumps([bet_detail["number"]]), # Assuming single number bets for now
                        "outcome_number": None, # Will be updated after actual bet placement
                        "profit_loss": 0.0,
                        "status": "pending_placement"
                    })
        
        # Here, you would typically send these bets to the actual betting house API/automation.
        # For now, we'll just save them as pending in our DB.
        placed_bets_records = []
        for bet_data in bets_to_place:
            new_bet = Bet(
                user_id=bet_data["user_id"],
                strategy_id=bet_data["strategy_id"],
                betting_house=bet_data["betting_house"],
                roulette_type=bet_data["roulette_type"],
                bet_amount=bet_data["bet_amount"],
                bet_numbers=bet_data["bet_numbers"],
                status=bet_data["status"]
            )
            db.session.add(new_bet)
            placed_bets_records.append(new_bet)
        db.session.commit()

        # After actual bet placement (simulated here), update status and profit/loss
        # This part would be handled by a separate process monitoring betting outcomes
        # For this endpoint, we just return the bets that would be placed.
        return jsonify({
            "message": "Spin processed and bets generated (if any)",
            "winning_number": winning_number,
            "bets_generated": [bet.to_dict() for bet in placed_bets_records]
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@automation_bp.route("/automation/update_bet_outcome", methods=["POST"])
def update_bet_outcome():
    """Updates the outcome of a placed bet and calculates profit/loss."""
    data = request.get_json()
    bet_id = data.get("bet_id")
    outcome_number = data.get("outcome_number")

    if not all([bet_id, outcome_number is not None]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        bet = Bet.query.get(bet_id)
        if not bet:
            return jsonify({"error": "Bet not found"}), 404

        bet.outcome_number = outcome_number
        
        # Calculate profit/loss (simplified for single number bets)
        bet_numbers_list = json.loads(bet.bet_numbers)
        profit_loss = -bet.bet_amount # Assume loss initially
        
        # For simplicity, if any of the bet numbers match the outcome, it's a win
        # In a real system, this would be more complex based on bet types (e.g., splits, corners)
        if outcome_number in bet_numbers_list:
            # Assuming 35:1 payout for straight-up number bets
            profit_loss = bet.bet_amount * 35 # Profit only, not including original stake
            bet.status = "won"
        else:
            bet.status = "lost"
        
        bet.profit_loss = profit_loss
        db.session.commit()

        return jsonify({"message": "Bet outcome updated", "bet": bet.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


