import sys
import os
import json
import ccxt
from PyQt5.QtWidgets import QApplication
from ui import UI

"""
IDEAS:
Add stink bid sell orders and stink bid buy orders on all charts
Add fat finger tool to always have some orders on every chart
Add signals bot that looks for abnormal volume spikes. Start tracking paper trades for the bot's success. 
Add candlestick charts.
"""


class CoinInfo:
    def __init__(self):
        self.available_coins = 0.0
        self.current_value = 0.0
        self.potential_gain = 0.0


class ExchangeClient:
    """Client for interacting with cryptocurrency exchanges using ccxt."""

    def __init__(self, config_file):
        """
        Initialize the exchange client using a configuration file.

        Args:
            config_file (str): Path to the JSON file containing API credentials and exchange name.
        """
        # Load API credentials from the configuration file
        with open(config_file, 'r') as file:
            config = json.load(file)

        self.exchange_name = config['exchange'].lower()
        self.api_key = config['api_key']
        self.api_secret = config['api_secret']

        # Initialize the exchange instance
        self.exchange = getattr(ccxt, self.exchange_name)({
            'apiKey': self.api_key,
            'secret': self.api_secret,
        })

        # Check if the exchange supports fetching balances
        if not self.exchange.has.get('fetchBalance', False):
            raise ValueError(f"{self.exchange_name} does not support fetching balances.")

        # Cached data
        self.balances = {}
        self.open_orders = []
        self.total_potential_gain = 0

    def fetch_balances(self):
        """Fetch account balances from the exchange."""
        try:
            balance_data = self.exchange.fetch_balance()
            self.balances = balance_data['total']
        except Exception as e:
            print(f"Error fetching balances: {e}")
            self.balances = {}

    def fetch_open_orders(self, symbol=None):
        """
        Fetch open orders from the exchange.

        Args:
            symbol (str, optional): Market symbol (e.g., 'BTC/USDT'). Fetches all orders if None.
        """
        try:
            self.open_orders = self.exchange.fetch_open_orders(symbol)
        except Exception as e:
            print(f"Error fetching open orders: {e}")
            self.open_orders = []

    def calculate_potential_account_value(self):
        """
        Calculate the potential account value if all open limit sell orders were filled.

        Returns:
            dict: A dictionary containing current and potential values by currency.
        """
        potential_gains = {}
        for order in self.open_orders:
            if order['side'] == 'sell' and order['status'] == 'open':
                symbol = order['symbol']
                base_currency = symbol.split('/')[0]
                price = float(order['price'])
                amount = float(order['amount'])

                if base_currency not in potential_gains:
                    potential_gains[base_currency] = 0

                potential_gains[base_currency] += price * amount

        self.total_potential_gain = sum(potential_gains.values())
        return potential_gains

    def cancel_all_orders(self, symbol=None):
        """
        Cancel all open orders for a specific symbol or all symbols.

        Args:
            symbol (str, optional): Market symbol (e.g., 'BTC/USDT'). Cancels all orders if None.
        """
        try:
            orders_to_cancel = self.open_orders if symbol is None else [
                order for order in self.open_orders if order['symbol'] == symbol
            ]
            for order in orders_to_cancel:
                self.exchange.cancel_order(order['id'], order['symbol'])
        except Exception as e:
            print(f"Error canceling orders: {e}")

    def market_sell_entire_position(self, symbol):
        """
        Market sell the entire position for a specific symbol.

        Args:
            symbol (str): Market symbol (e.g., 'BTC/USDT').
        """
        base_currency = symbol.split('/')[0]
        if base_currency in self.balances and self.balances[base_currency] > 0:
            try:
                self.exchange.create_market_sell_order(symbol, self.balances[base_currency])
            except Exception as e:
                print(f"Error placing market sell order: {e}")
    
    def get_usd_pairs_under_threshold(self, threshold=20.0):
        """
        Get all USD trading pairs where current balance is under threshold.
        
        Args:
            threshold (float): Minimum USD value threshold
            
        Returns:
            list: List of dicts with currency, balance, and symbol info
        """
        try:
            markets = self.exchange.load_markets()
            usd_pairs = []
            
            for symbol, market in markets.items():
                if market['quote'] == 'USD' and market['active']:
                    base_currency = market['base']
                    
                    # Get current balance in USD
                    balance = self.balances.get(base_currency, 0)
                    
                    # Get current price to calculate USD value
                    try:
                        ticker = self.exchange.fetch_ticker(symbol)
                        current_price = ticker['last']
                        usd_value = balance * current_price
                        
                        if usd_value < threshold:
                            usd_pairs.append({
                                'currency': base_currency,
                                'balance': usd_value,
                                'symbol': symbol
                            })
                    except Exception as e:
                        print(f"Error fetching ticker for {symbol}: {e}")
                        continue
            
            # Sort by currency name
            usd_pairs.sort(key=lambda x: x['currency'])
            return usd_pairs
            
        except Exception as e:
            print(f"Error getting USD pairs: {e}")
            return []
    
    def market_buy_multiple(self, symbols, usd_amount_per_coin):
        """
        Execute market buy orders for multiple symbols.
        
        Args:
            symbols (list): List of trading pair symbols (e.g., ['BTC/USD', 'ETH/USD'])
            usd_amount_per_coin (float): USD amount to spend on each coin
            
        Returns:
            dict: Results with success/failure info for each symbol
        """
        results = {'success': [], 'failed': []}
        
        for symbol in symbols:
            try:
                # Get current price
                ticker = self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                # Calculate amount to buy
                amount = usd_amount_per_coin / current_price
                
                # Place market buy order
                order = self.exchange.create_market_buy_order(symbol, amount)
                results['success'].append({
                    'symbol': symbol,
                    'amount': amount,
                    'order_id': order['id']
                })
                
            except Exception as e:
                results['failed'].append({
                    'symbol': symbol,
                    'error': str(e)
                })
                print(f"Error buying {symbol}: {e}")
        
        return results

def run():
    # Initialize the application
    app = QApplication(sys.argv)
    app.setApplicationName("Field Orders")

    # Initialize the exchange client
    client = ExchangeClient(config_file="cdp_api_key_fieldorders.json")

    # Initialize and show the main window
    main_window = UI(client)
    main_window.show()

    # Start the application event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()