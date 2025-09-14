import random
from src.strategies.strategy_logic import StrategyLogic
from src.roulette_simulator import RouletteSimulator
import json

class StrategySimulation:
    def __init__(self):
        self.strategy_logic = StrategyLogic()
        self.roulette_simulator = RouletteSimulator()

    def run_simulation(self, strategy_type, config, num_spins=1000):
        """Runs a simulation for a given strategy over a specified number of spins."""
        history = []
        total_profit = 0
        total_bets = 0
        winning_bets = 0
        losing_bets = 0
        bet_history = []

        for spin in range(num_spins):
            # Simulate a spin
            winning_number = self.roulette_simulator.spin()
            history.insert(0, winning_number)  # Add to front (most recent first)
            
            # Keep history manageable (last 20 spins)
            if len(history) > 20:
                history = history[:20]

            # Execute strategy based on current history
            if strategy_type == "terminal_8":
                bets = self.strategy_logic.execute_strategy_terminal_8(history, config)
            elif strategy_type == "3x3_pattern":
                bets = self.strategy_logic.execute_strategy_3x3_pattern(history, config)
            elif strategy_type == "2x7_pattern":
                bets = self.strategy_logic.execute_strategy_2x7_pattern(history, config)
            else:
                bets = []

            # Process bets if any
            if bets:
                spin_profit = 0
                for bet in bets:
                    bet_number = bet["number"]
                    bet_amount = bet["amount"]
                    payout = self.roulette_simulator.calculate_payout(bet_number, bet_amount, winning_number)
                    spin_profit += payout
                    total_bets += 1
                    
                    if payout > 0:
                        winning_bets += 1
                    else:
                        losing_bets += 1

                total_profit += spin_profit
                bet_history.append({
                    "spin": spin + 1,
                    "winning_number": winning_number,
                    "bets": bets,
                    "profit": spin_profit,
                    "cumulative_profit": total_profit
                })

        # Calculate statistics
        win_rate = (winning_bets / total_bets * 100) if total_bets > 0 else 0
        avg_profit_per_bet = total_profit / total_bets if total_bets > 0 else 0

        return {
            "strategy_type": strategy_type,
            "config": config,
            "num_spins": num_spins,
            "total_profit": total_profit,
            "total_bets": total_bets,
            "winning_bets": winning_bets,
            "losing_bets": losing_bets,
            "win_rate": win_rate,
            "avg_profit_per_bet": avg_profit_per_bet,
            "bet_history": bet_history[-50:]  # Keep last 50 for analysis
        }

    def compare_strategies(self, num_spins=1000):
        """Compares all three strategies over the same number of spins."""
        strategies = [
            {"type": "terminal_8", "name": "Terminal 8 (1→6)"},
            {"type": "3x3_pattern", "name": "Padrão 3x3"},
            {"type": "2x7_pattern", "name": "Padrão 2x7"}
        ]
        
        config = {"chip_value": 1.0, "max_entries": 2}
        results = []

        for strategy in strategies:
            result = self.run_simulation(strategy["type"], config, num_spins)
            result["strategy_name"] = strategy["name"]
            results.append(result)

        return results

# Example Usage (for testing)
if __name__ == "__main__":
    simulation = StrategySimulation()
    
    # Test individual strategy
    print("Testing Terminal 8 strategy...")
    config = {"chip_value": 1.0, "max_entries": 2}
    result = simulation.run_simulation("terminal_8", config, 100)
    
    print(f"Strategy: {result['strategy_type']}")
    print(f"Total Profit: {result['total_profit']:.2f}")
    print(f"Total Bets: {result['total_bets']}")
    print(f"Win Rate: {result['win_rate']:.2f}%")
    print(f"Avg Profit per Bet: {result['avg_profit_per_bet']:.2f}")
    
    # Compare all strategies
    print("\n" + "="*50)
    print("Comparing all strategies...")
    comparison_results = simulation.compare_strategies(500)
    
    for result in comparison_results:
        print(f"\n{result['strategy_name']}:")
        print(f"  Total Profit: {result['total_profit']:.2f}")
        print(f"  Total Bets: {result['total_bets']}")
        print(f"  Win Rate: {result['win_rate']:.2f}%")
        print(f"  Avg Profit per Bet: {result['avg_profit_per_bet']:.2f}")

