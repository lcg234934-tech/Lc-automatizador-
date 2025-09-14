import random

class RouletteSimulator:
    def __init__(self, numbers=None):
        # Standard European Roulette numbers
        self.numbers = numbers if numbers is not None else list(range(37)) # 0-36

    def spin(self):
        """Simulates a spin of the roulette wheel and returns the winning number."""
        return random.choice(self.numbers)

    def calculate_payout(self, bet_number, bet_amount, winning_number):
        """Calculates the payout for a single number bet.
        This is a simplified payout for a straight-up bet (35:1).
        """
        if bet_number == winning_number:
            return bet_amount * 36  # Original bet + 35x profit
        else:
            return -bet_amount # Lose the bet amount

# Example Usage (for testing)
if __name__ == "__main__":
    simulator = RouletteSimulator()
    print("Simulating 10 spins:")
    for _ in range(10):
        winning_number = simulator.spin()
        print(f"Winning number: {winning_number}")

    # Example of calculating payout
    bet_amount = 10
    bet_on = 17
    winning_num = simulator.spin()
    payout = simulator.calculate_payout(bet_on, bet_amount, winning_num)
    print(f"\nBetting {bet_amount} on {bet_on}. Winning number: {winning_num}. Payout: {payout}")


