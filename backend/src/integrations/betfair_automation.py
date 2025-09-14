import asyncio
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional
import logging
from .betfair_client import BetfairClient

class BetfairAutomation:
    def __init__(self, betfair_config: Dict, lc_backend_url: str = "http://localhost:5000"):
        """
        Initialize Betfair automation system
        
        Args:
            betfair_config: Dictionary with Betfair credentials
            lc_backend_url: URL of LC Automatizador backend
        """
        self.betfair_client = BetfairClient(**betfair_config)
        self.lc_backend_url = lc_backend_url
        self.active_markets = {}
        self.monitoring_active = False
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Mapping of roulette numbers to Betfair selection IDs
        # This would need to be configured based on actual Betfair market structure
        self.number_to_selection_map = {
            0: "47972",   # Example selection IDs - these need to be actual IDs
            1: "47973",
            2: "47974",
            3: "47975",
            4: "47976",
            5: "47977",
            6: "47978",
            7: "47979",
            8: "47980",
            9: "47981",
            10: "47982",
            11: "47983",
            12: "47984",
            13: "47985",
            14: "47986",
            15: "47987",
            16: "47988",
            17: "47989",
            18: "47990",
            19: "47991",
            20: "47992",
            21: "47993",
            22: "47994",
            23: "47995",
            24: "47996",
            25: "47997",
            26: "47998",
            27: "47999",
            28: "48000",
            29: "48001",
            30: "48002",
            31: "48003",
            32: "48004",
            33: "48005",
            34: "48006",
            35: "48007",
            36: "48008"
        }
        
        # Reverse mapping
        self.selection_to_number_map = {v: k for k, v in self.number_to_selection_map.items()}
    
    def start_automation(self, user_id: int, target_market_id: str = None) -> bool:
        """
        Start the automation system
        
        Args:
            user_id: LC Automatizador user ID
            target_market_id: Specific market ID to monitor (optional)
            
        Returns:
            bool: True if started successfully
        """
        try:
            # Login to Betfair
            if not self.betfair_client.login():
                self.logger.error("Failed to login to Betfair")
                return False
            
            # Get available roulette markets
            markets = self.betfair_client.get_roulette_markets()
            if not markets:
                self.logger.error("No roulette markets found")
                return False
            
            # Select market to monitor
            if target_market_id:
                selected_market = next((m for m in markets if m['market_id'] == target_market_id), None)
                if not selected_market:
                    self.logger.error(f"Target market {target_market_id} not found")
                    return False
            else:
                # Select the first available market
                selected_market = markets[0]
            
            self.logger.info(f"Starting automation for market: {selected_market['market_name']} ({selected_market['market_id']})")
            
            # Start monitoring
            self.monitoring_active = True
            self.active_markets[selected_market['market_id']] = {
                'user_id': user_id,
                'market_data': selected_market
            }
            
            # Start monitoring loop
            asyncio.run(self._monitor_market(selected_market['market_id'], user_id))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting automation: {str(e)}")
            return False
    
    def stop_automation(self):
        """Stop the automation system"""
        self.monitoring_active = False
        self.active_markets.clear()
        self.betfair_client.logout()
        self.logger.info("Automation stopped")
    
    async def _monitor_market(self, market_id: str, user_id: int):
        """
        Monitor a specific market for results and place bets
        
        Args:
            market_id: Betfair market ID
            user_id: LC Automatizador user ID
        """
        last_version = None
        spin_history = []
        
        while self.monitoring_active:
            try:
                # Get market book
                market_book = self.betfair_client.get_market_book(market_id)
                
                if not market_book:
                    await asyncio.sleep(2)
                    continue
                
                # Check if market version changed (new spin result)
                if market_book['version'] != last_version:
                    last_version = market_book['version']
                    
                    # Check if market is complete (result available)
                    if market_book['complete']:
                        winning_number = self._extract_winning_number(market_book)
                        
                        if winning_number is not None:
                            self.logger.info(f"New spin result: {winning_number}")
                            
                            # Add to history
                            spin_history.insert(0, winning_number)
                            if len(spin_history) > 20:  # Keep last 20 spins
                                spin_history = spin_history[:20]
                            
                            # Send result to LC Automatizador backend
                            await self._process_spin_result(user_id, winning_number, market_id)
                            
                            # Wait for new market to become available
                            await self._wait_for_new_market()
                
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                self.logger.error(f"Error in market monitoring: {str(e)}")
                await asyncio.sleep(5)
    
    def _extract_winning_number(self, market_book: Dict) -> Optional[int]:
        """
        Extract winning roulette number from market book
        
        Args:
            market_book: Betfair market book data
            
        Returns:
            Winning number or None if not found
        """
        try:
            for runner in market_book.get('runners', []):
                if runner.get('status') == 'WINNER':
                    selection_id = str(runner.get('selection_id'))
                    winning_number = self.selection_to_number_map.get(selection_id)
                    return winning_number
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting winning number: {str(e)}")
            return None
    
    async def _process_spin_result(self, user_id: int, winning_number: int, market_id: str):
        """
        Send spin result to LC Automatizador backend for processing
        
        Args:
            user_id: User ID
            winning_number: Winning roulette number
            market_id: Betfair market ID
        """
        try:
            payload = {
                'user_id': user_id,
                'winning_number': winning_number,
                'roulette_type': 'betfair',
                'betting_house': 'betfair',
                'market_id': market_id,
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.lc_backend_url}/api/automation/process_spin",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                bets_generated = result.get('bets_generated', [])
                
                if bets_generated:
                    self.logger.info(f"Generated {len(bets_generated)} bets for strategies")
                    
                    # Place bets on Betfair
                    for bet_data in bets_generated:
                        await self._place_bet_on_betfair(bet_data)
                else:
                    self.logger.info("No bets generated for this spin")
            else:
                self.logger.error(f"Error processing spin result: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.logger.error(f"Error processing spin result: {str(e)}")
    
    async def _place_bet_on_betfair(self, bet_data: Dict):
        """
        Place a bet on Betfair based on LC Automatizador bet data
        
        Args:
            bet_data: Bet data from LC Automatizador
        """
        try:
            # Extract bet information
            bet_numbers = json.loads(bet_data.get('bet_numbers', '[]'))
            bet_amount = bet_data.get('bet_amount', 0)
            bet_id = bet_data.get('id')
            
            # For each number in the bet
            for number in bet_numbers:
                selection_id = self.number_to_selection_map.get(number)
                
                if not selection_id:
                    self.logger.error(f"No selection ID found for number {number}")
                    continue
                
                # Calculate odds (this would need to be dynamic based on market)
                # For now, using standard roulette odds
                odds = 36.0  # 35:1 payout + original stake
                
                # Place bet
                bet_result = self.betfair_client.place_bet(
                    market_id=bet_data.get('market_id', ''),
                    selection_id=selection_id,
                    side='B',  # Back bet
                    size=bet_amount,
                    price=odds
                )
                
                if bet_result and bet_result.get('success'):
                    self.logger.info(f"Bet placed successfully on number {number}: {bet_result}")
                    
                    # Update bet status in LC Automatizador
                    await self._update_bet_status(bet_id, 'placed', bet_result)
                else:
                    self.logger.error(f"Failed to place bet on number {number}: {bet_result}")
                    await self._update_bet_status(bet_id, 'failed', bet_result)
                
        except Exception as e:
            self.logger.error(f"Error placing bet on Betfair: {str(e)}")
    
    async def _update_bet_status(self, bet_id: int, status: str, bet_result: Dict):
        """
        Update bet status in LC Automatizador backend
        
        Args:
            bet_id: Bet ID in LC Automatizador
            status: New status
            bet_result: Result from Betfair
        """
        try:
            payload = {
                'bet_id': bet_id,
                'status': status,
                'betfair_bet_id': bet_result.get('bet_id') if bet_result else None,
                'betfair_result': bet_result
            }
            
            response = requests.put(
                f"{self.lc_backend_url}/api/bets/{bet_id}",
                json=payload,
                timeout=10
            )
            
            if response.status_code != 200:
                self.logger.error(f"Error updating bet status: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.logger.error(f"Error updating bet status: {str(e)}")
    
    async def _wait_for_new_market(self):
        """Wait for a new roulette market to become available"""
        self.logger.info("Waiting for new roulette market...")
        
        # In a real implementation, this would check for new markets
        # For now, just wait a bit
        await asyncio.sleep(30)  # Wait 30 seconds for next spin

# Configuration example
BETFAIR_CONFIG = {
    'username': 'your_betfair_username',
    'password': 'your_betfair_password',
    'app_key': 'your_betfair_app_key',
    'cert_files': None  # ('cert.crt', 'key.key') for certificate auth
}

# Example usage
if __name__ == "__main__":
    automation = BetfairAutomation(BETFAIR_CONFIG)
    
    try:
        # Start automation for user ID 1
        automation.start_automation(user_id=1)
    except KeyboardInterrupt:
        print("Stopping automation...")
        automation.stop_automation()

