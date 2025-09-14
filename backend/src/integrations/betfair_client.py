import betfairlightweight
from betfairlightweight import APIClient
from betfairlightweight.filters import (
    market_filter,
    price_projection,
    place_instruction,
    limit_order,
    market_book_filter
)
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional

class BetfairClient:
    def __init__(self, username: str, password: str, app_key: str, cert_files: tuple = None):
        """
        Initialize Betfair API client
        
        Args:
            username: Betfair username
            password: Betfair password  
            app_key: Betfair application key
            cert_files: Tuple of (cert_file_path, key_file_path) for certificate authentication
        """
        self.username = username
        self.password = password
        self.app_key = app_key
        self.cert_files = cert_files
        self.client = None
        self.session_token = None
        self.is_logged_in = False
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def login(self) -> bool:
        """
        Login to Betfair API
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            # Create API client
            if self.cert_files:
                # Certificate-based authentication (more secure)
                self.client = APIClient(
                    username=self.username,
                    password=self.password,
                    app_key=self.app_key,
                    certs=self.cert_files
                )
            else:
                # Username/password authentication
                self.client = APIClient(
                    username=self.username,
                    password=self.password,
                    app_key=self.app_key
                )
            
            # Login
            self.client.login()
            self.is_logged_in = True
            self.logger.info("Successfully logged in to Betfair API")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to login to Betfair API: {str(e)}")
            self.is_logged_in = False
            return False
    
    def logout(self):
        """Logout from Betfair API"""
        if self.client and self.is_logged_in:
            try:
                self.client.logout()
                self.is_logged_in = False
                self.logger.info("Successfully logged out from Betfair API")
            except Exception as e:
                self.logger.error(f"Error during logout: {str(e)}")
    
    def get_roulette_markets(self) -> List[Dict]:
        """
        Get available roulette markets
        
        Returns:
            List of roulette market data
        """
        if not self.is_logged_in:
            self.logger.error("Not logged in to Betfair API")
            return []
        
        try:
            # Create market filter for roulette
            market_filter_obj = market_filter(
                event_type_ids=['2'],  # Casino games
                market_type_codes=['ROULETTE'],  # Roulette markets
                in_play_only=True  # Only live markets
            )
            
            # Get markets
            markets = self.client.betting.list_market_catalogue(
                filter=market_filter_obj,
                max_results=100,
                market_projection=['COMPETITION', 'EVENT', 'EVENT_TYPE', 'MARKET_START_TIME', 'MARKET_DESCRIPTION']
            )
            
            roulette_markets = []
            for market in markets:
                roulette_markets.append({
                    'market_id': market.market_id,
                    'market_name': market.market_name,
                    'event_name': market.event.name if market.event else 'Unknown',
                    'start_time': market.market_start_time,
                    'total_matched': market.total_matched if hasattr(market, 'total_matched') else 0
                })
            
            self.logger.info(f"Found {len(roulette_markets)} roulette markets")
            return roulette_markets
            
        except Exception as e:
            self.logger.error(f"Error getting roulette markets: {str(e)}")
            return []
    
    def get_market_book(self, market_id: str) -> Optional[Dict]:
        """
        Get market book data for a specific market
        
        Args:
            market_id: Betfair market ID
            
        Returns:
            Market book data or None if error
        """
        if not self.is_logged_in:
            self.logger.error("Not logged in to Betfair API")
            return None
        
        try:
            price_proj = price_projection(
                price_data=['EX_BEST_OFFERS', 'EX_TRADED'],
                ex_best_offers_overrides=None,
                virtualise=False,
                rollover_stakes=False
            )
            
            market_books = self.client.betting.list_market_book(
                market_ids=[market_id],
                price_projection=price_proj
            )
            
            if market_books and len(market_books) > 0:
                market_book = market_books[0]
                return {
                    'market_id': market_book.market_id,
                    'is_market_data_delayed': market_book.is_market_data_delayed,
                    'status': market_book.status,
                    'bet_delay': market_book.bet_delay,
                    'bsp_reconciled': market_book.bsp_reconciled,
                    'complete': market_book.complete,
                    'inplay': market_book.inplay,
                    'number_of_winners': market_book.number_of_winners,
                    'number_of_runners': market_book.number_of_runners,
                    'number_of_active_runners': market_book.number_of_active_runners,
                    'last_match_time': market_book.last_match_time,
                    'total_matched': market_book.total_matched,
                    'total_available': market_book.total_available,
                    'cross_matching': market_book.cross_matching,
                    'runners_voidable': market_book.runners_voidable,
                    'version': market_book.version,
                    'runners': [
                        {
                            'selection_id': runner.selection_id,
                            'fullImage': runner.full_image if hasattr(runner, 'full_image') else {},
                            'handicap': runner.handicap,
                            'status': runner.status,
                            'adjustment_factor': runner.adjustment_factor,
                            'last_price_traded': runner.last_price_traded,
                            'total_matched': runner.total_matched,
                            'removal_date': runner.removal_date,
                            'ex': {
                                'available_to_back': [
                                    {'price': price.price, 'size': price.size}
                                    for price in (runner.ex.available_to_back or [])
                                ],
                                'available_to_lay': [
                                    {'price': price.price, 'size': price.size}
                                    for price in (runner.ex.available_to_lay or [])
                                ],
                                'traded': [
                                    {'price': price.price, 'size': price.size}
                                    for price in (runner.ex.traded or [])
                                ]
                            } if runner.ex else {}
                        }
                        for runner in (market_book.runners or [])
                    ]
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting market book for {market_id}: {str(e)}")
            return None
    
    def place_bet(self, market_id: str, selection_id: str, side: str, size: float, price: float) -> Optional[Dict]:
        """
        Place a bet on Betfair
        
        Args:
            market_id: Betfair market ID
            selection_id: Selection ID (runner)
            side: 'B' for back, 'L' for lay
            size: Stake amount
            price: Odds
            
        Returns:
            Bet placement result or None if error
        """
        if not self.is_logged_in:
            self.logger.error("Not logged in to Betfair API")
            return None
        
        try:
            # Create place instruction
            instruction = place_instruction(
                order_type='LIMIT',
                selection_id=selection_id,
                handicap=0,
                side=side,
                limit_order=limit_order(size=size, price=price, persistence_type='LAPSE')
            )
            
            # Place bet
            bet_result = self.client.betting.place_orders(
                market_id=market_id,
                instructions=[instruction],
                customer_ref=f"LC_AUTO_{int(time.time())}"
            )
            
            if bet_result.status == 'SUCCESS':
                instruction_result = bet_result.instruction_reports[0]
                if instruction_result.status == 'SUCCESS':
                    bet_id = instruction_result.bet_id
                    size_matched = instruction_result.size_matched
                    avg_price_matched = instruction_result.average_price_matched
                    
                    self.logger.info(f"Bet placed successfully: ID={bet_id}, Size={size_matched}, Price={avg_price_matched}")
                    
                    return {
                        'success': True,
                        'bet_id': bet_id,
                        'size_matched': size_matched,
                        'avg_price_matched': avg_price_matched,
                        'status': instruction_result.status
                    }
                else:
                    self.logger.error(f"Bet placement failed: {instruction_result.error_code}")
                    return {
                        'success': False,
                        'error': instruction_result.error_code
                    }
            else:
                self.logger.error(f"Bet placement failed: {bet_result.error_code}")
                return {
                    'success': False,
                    'error': bet_result.error_code
                }
                
        except Exception as e:
            self.logger.error(f"Error placing bet: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_current_orders(self, market_id: str = None) -> List[Dict]:
        """
        Get current orders (bets)
        
        Args:
            market_id: Optional market ID to filter orders
            
        Returns:
            List of current orders
        """
        if not self.is_logged_in:
            self.logger.error("Not logged in to Betfair API")
            return []
        
        try:
            current_orders = self.client.betting.list_current_orders(
                market_ids=[market_id] if market_id else None
            )
            
            orders = []
            for order in current_orders.current_orders:
                orders.append({
                    'bet_id': order.bet_id,
                    'market_id': order.market_id,
                    'selection_id': order.selection_id,
                    'full_image': order.full_image,
                    'side': order.side,
                    'status': order.status,
                    'persistence_type': order.persistence_type,
                    'order_type': order.order_type,
                    'placed_date': order.placed_date,
                    'matched_date': order.matched_date,
                    'average_price_matched': order.average_price_matched,
                    'size_matched': order.size_matched,
                    'size_remaining': order.size_remaining,
                    'size_lapsed': order.size_lapsed,
                    'size_cancelled': order.size_cancelled,
                    'size_voided': order.size_voided,
                    'customer_order_ref': order.customer_order_ref,
                    'customer_strategy_ref': order.customer_strategy_ref
                })
            
            return orders
            
        except Exception as e:
            self.logger.error(f"Error getting current orders: {str(e)}")
            return []
    
    def monitor_roulette_results(self, market_id: str, callback_function=None):
        """
        Monitor roulette results for a specific market
        
        Args:
            market_id: Betfair market ID to monitor
            callback_function: Function to call when result is detected
        """
        if not self.is_logged_in:
            self.logger.error("Not logged in to Betfair API")
            return
        
        self.logger.info(f"Starting to monitor roulette results for market {market_id}")
        
        last_version = None
        
        while True:
            try:
                market_book = self.get_market_book(market_id)
                
                if market_book and market_book['version'] != last_version:
                    last_version = market_book['version']
                    
                    # Check if market is complete (result available)
                    if market_book['complete']:
                        # Find winning runner
                        winning_runner = None
                        for runner in market_book['runners']:
                            if runner['status'] == 'WINNER':
                                winning_runner = runner
                                break
                        
                        if winning_runner and callback_function:
                            result_data = {
                                'market_id': market_id,
                                'winning_selection_id': winning_runner['selection_id'],
                                'result_time': datetime.now(),
                                'market_data': market_book
                            }
                            callback_function(result_data)
                        
                        # Market is complete, stop monitoring
                        break
                
                # Wait before next check
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error monitoring market {market_id}: {str(e)}")
                time.sleep(5)  # Wait longer on error

# Example usage and configuration
if __name__ == "__main__":
    # Configuration - REPLACE WITH YOUR ACTUAL CREDENTIALS
    BETFAIR_CONFIG = {
        'username': 'your_betfair_username',
        'password': 'your_betfair_password',
        'app_key': 'your_betfair_app_key',
        'cert_files': None  # ('path/to/cert.crt', 'path/to/key.key') for certificate auth
    }
    
    # Initialize client
    client = BetfairClient(**BETFAIR_CONFIG)
    
    # Login
    if client.login():
        print("Successfully connected to Betfair API")
        
        # Get roulette markets
        markets = client.get_roulette_markets()
        print(f"Found {len(markets)} roulette markets")
        
        for market in markets[:3]:  # Show first 3 markets
            print(f"Market: {market['market_name']} - ID: {market['market_id']}")
        
        # Logout
        client.logout()
    else:
        print("Failed to connect to Betfair API")

