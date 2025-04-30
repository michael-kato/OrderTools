
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "coinbase_advanced"))
import json
import ccxt
from PyQt5.QtWidgets import QApplication
from ui import UI

"""
IDEAS:
Add stink bid sell orders and stink bid buy orders on all charts
Add signals bot that looks for abnormal volume spikes. Start tracking paper trades for the bot's success. 
Add candlestick charts.
"""


class CoinInfo():
    def __init__(self):
        self.available_coins = 0.0
        self.current_value = 0.0
        self.potential_gain = 0.0


class ExchangeClient:
    """Client for interacting with cryptocurrency exchanges using ccxt."""

    def __init__(self, exchange_name, api_key, api_secret):
        """
        Initialize the exchange client.

        Args:
            exchange_name (str): Name of the exchange (e.g., 'coinbasepro', 'mexc').
            api_key (str): API key for the exchange.
            api_secret (str): API secret for the exchange.
        """
        self.exchange_name = exchange_name.lower()
        self.api_key = api_key
        self.api_secret = api_secret

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

def main():
    # Initialize the application
    app = QApplication(sys.argv)
    app.setApplicationName("Order Tools")
    
    # Initialize the exchange client
    client = ExchangeClient(api_key_file="cdp_api_key_ordertools_trade.json")
    
    # Initialize and show the main window
    main_window = UI(client)
    main_window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
