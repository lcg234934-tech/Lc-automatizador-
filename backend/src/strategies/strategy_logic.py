import json

class StrategyLogic:
    def __init__(self):
        pass

    def _check_pattern(self, history, pattern):
        """Checks if a given pattern exists in the history."""
        if len(history) < len(pattern):
            return False
        
        # Simple check for consecutive pattern
        if len(pattern) == 3 and pattern[0] == 1 and pattern[1] == 6 and pattern[2] == 8:
            for i in range(len(history) - 2):
                if history[i] == 1 and history[i+1] == 6 and history[i+2] == 8:
                    return True
        
        # More complex pattern matching with intervals would go here
        # For now, let's assume a simplified check for demonstration
        
        return False

    def execute_strategy_terminal_8(self, history, config):
        """Executes Strategy 1: Buscar Terminal (8) pelo padrão 1→6.
        history: list of numbers that came out in the roulette (most recent first)
        config: dictionary with strategy configuration (e.g., chip_value, max_entries)
        """
        bets = []
        trigger_found = False

        # Gatilhos válidos (4 formas):
        # 1. Consecutivo: 1 → 6 → 8
        # 2. Intervalo 1 casa: 1 [x] 6 [x] 8
        # 3. Intervalo 2 casas: 1 [xx] 6 [xx] 8
        # 4. Intervalo 3 casas: 1 [xxx] 6 [xxx] 8

        # Simplified check for 1 -> 6 -> 8 consecutive for now
        if self._check_pattern(history, [1, 6, 8]):
            trigger_found = True

        if trigger_found:
            # Apostas:
            # 1 ficha em: 12, 28, 7, 29, 18, 22, 8, 11, 14
            # 2 fichas no: 30
            chip_value = config.get("chip_value", 1.0)
            bets.append({"number": 12, "amount": chip_value})
            bets.append({"number": 28, "amount": chip_value})
            bets.append({"number": 7, "amount": chip_value})
            bets.append({"number": 29, "amount": chip_value})
            bets.append({"number": 18, "amount": chip_value})
            bets.append({"number": 22, "amount": chip_value})
            bets.append({"number": 8, "amount": chip_value})
            bets.append({"number": 11, "amount": chip_value})
            bets.append({"number": 14, "amount": chip_value})
            bets.append({"number": 30, "amount": chip_value * 2})

        return bets

    def execute_strategy_3x3_pattern(self, history, config):
        """Executes Strategy 2: Padrão 3x3.
        history: list of numbers that came out in the roulette (most recent first)
        config: dictionary with strategy configuration
        """
        bets = []
        trigger_found = False
        
        list_numbers = [0, 3, 4, 12, 15, 19, 21, 26, 28, 32, 35]

        # Gatilho: Se 3 números consecutivos da lista saírem
        if len(history) >= 3:
            consecutive_in_list = 0
            for i in range(3):
                if history[i] in list_numbers:
                    consecutive_in_list += 1
                else:
                    consecutive_in_list = 0 # Reset if not consecutive
                    break
            if consecutive_in_list == 3:
                trigger_found = True

        if trigger_found:
            # Apostas:
            # 1 ficha em cada número da lista.
            # 2 fichas no 0.
            chip_value = config.get("chip_value", 1.0)
            for num in list_numbers:
                if num == 0:
                    bets.append({"number": num, "amount": chip_value * 2})
                else:
                    bets.append({"number": num, "amount": chip_value})

        return bets

    def execute_strategy_2x7_pattern(self, history, config):
        """Executes Strategy 3: Padrão 2x7.
        history: list of numbers that came out in the roulette (most recent first)
        config: dictionary with strategy configuration
        """
        bets = []
        trigger_found = False

        list_numbers = [2, 4, 7, 12, 17, 18, 19, 21, 22, 25, 28, 29, 34, 35]

        # Gatilho: Se 3 números consecutivos da lista saírem
        if len(history) >= 3:
            consecutive_in_list = 0
            for i in range(3):
                if history[i] in list_numbers:
                    consecutive_in_list += 1
                else:
                    consecutive_in_list = 0 # Reset if not consecutive
                    break
            if consecutive_in_list == 3:
                trigger_found = True

        if trigger_found:
            # Apostas:
            # 1 ficha em cada número da lista.
            chip_value = config.get("chip_value", 1.0)
            for num in list_numbers:
                bets.append({"number": num, "amount": chip_value})

        return bets


# Example Usage (for testing)
if __name__ == "__main__":
    strategy_logic = StrategyLogic()

    # Test Strategy 1
    history1 = [8, 6, 1, 20, 5] # Example history (most recent first)
    config1 = {"chip_value": 1.0, "max_entries": 2}
    bets1 = strategy_logic.execute_strategy_terminal_8(history1, config1)
    print(f"Strategy 1 Bets: {bets1}")

    # Test Strategy 2
    history2 = [3, 4, 12, 1, 2] # Example history
    config2 = {"chip_value": 1.0, "max_entries": 2}
    bets2 = strategy_logic.execute_strategy_3x3_pattern(history2, config2)
    print(f"Strategy 2 Bets: {bets2}")

    # Test Strategy 3
    history3 = [2, 4, 7, 10, 11] # Example history
    config3 = {"chip_value": 1.0, "max_entries": 2}
    bets3 = strategy_logic.execute_strategy_2x7_pattern(history3, config3)
    print(f"Strategy 3 Bets: {bets3}")




def should_execute_strategy(strategy, current_time=None):
    """
    Check if a strategy should be executed based on its schedule
    
    Args:
        strategy: Strategy object
        current_time: Optional datetime object for testing
    
    Returns:
        bool: True if strategy should be executed
    """
    if not strategy.is_active:
        return False
    
    # Use the strategy's built-in method to check if it's active now
    return strategy.is_active_now()

def get_active_strategies(user_id):
    """
    Get all strategies that should be active right now for a user
    
    Args:
        user_id: User ID
        
    Returns:
        List of active Strategy objects
    """
    from src.models.strategy import Strategy
    
    # Get all strategies for the user
    all_strategies = Strategy.query.filter_by(user_id=user_id).all()
    
    # Filter to only those that should be active now
    active_strategies = []
    for strategy in all_strategies:
        if should_execute_strategy(strategy):
            active_strategies.append(strategy)
    
    return active_strategies

def check_strategy_schedule_status(user_id):
    """
    Check the schedule status of all strategies for a user
    
    Args:
        user_id: User ID
        
    Returns:
        Dict with strategy status information
    """
    from src.models.strategy import Strategy
    
    strategies = Strategy.query.filter_by(user_id=user_id).all()
    
    status = {
        'total_strategies': len(strategies),
        'active_strategies': 0,
        'scheduled_strategies': 0,
        'currently_running': 0,
        'strategies': []
    }
    
    for strategy in strategies:
        strategy_info = {
            'id': strategy.id,
            'name': strategy.name,
            'is_active': strategy.is_active,
            'schedule_enabled': strategy.schedule_enabled,
            'is_active_now': strategy.is_active_now(),
            'start_time': strategy.start_time.strftime('%H:%M') if strategy.start_time else None,
            'end_time': strategy.end_time.strftime('%H:%M') if strategy.end_time else None,
            'days_of_week': strategy.get_days_of_week()
        }
        
        status['strategies'].append(strategy_info)
        
        if strategy.is_active:
            status['active_strategies'] += 1
        
        if strategy.schedule_enabled:
            status['scheduled_strategies'] += 1
        
        if strategy.is_active_now():
            status['currently_running'] += 1
    
    return status

