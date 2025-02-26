import os
import json
import time
from typing import List, Dict, Any, Optional
from coinbase_advanced.coinbase.websocket import WSClient, WebsocketResponse, WSClientConnectionClosedException, WSClientException

class CoinbaseClient:
    """Client for interacting with the Coinbase Advanced Trade API via WebSocket."""
    
    def __init__(self, api_key=None, api_secret=None):
        """
        Initialize the Coinbase WebSocket client.
        
        Args:
            api_key (str, optional): Coinbase API key. If not provided, will attempt to load from environment.
            api_secret (str, optional): Coinbase API secret. If not provided, will attempt to load from environment.
        """
        self.api_key = api_key or os.environ.get('COINBASE_API_KEY')
        self.api_secret = api_secret or os.environ.get('COINBASE_API_SECRET')
        self.cached_orders = []

    def fetch_data_via_websocket(self):
        """Fetch data using WebSocket and update caches."""
        self.client = WSClient(api_key=self.api_key, 
                               api_secret=self.api_secret, 
                               on_message=self.on_message, 
                               #max_size=50 * 1024 * 1024, 
                               verbose=True)
        
        # Wait for data to be fetched
        #try:
        # Connect and subscribe to channels
        self.client.open()
        self.client.subscribe(product_ids=[], channels=['user'])

        time.sleep(10)

        #except WSClientConnectionClosedException as e:
        #    print("Connection closed! Retry attempts exhausted.")
        #except WSClientException as e:
        #    print("Error encountered!")
        
        self.client.unsubscribe(product_ids=[], channels=['user'])
        # Disconnect after fetching data
        self.client.close()

    def on_message(self, message):
        """Handle incoming WebSocket messages."""
        while True:
            data = json.loads(message)
            ws_object = WebsocketResponse(data)
            if ws_object.channel == "user" :
                # ran out of orders
                #if len(ws_object.events[0]['orders']) < 50:
                #    return
                for event in ws_object.events:
                    self.cached_orders.extend(event['orders'])
                    
                    return # we need bettter logic to get all orders
            else:
                return


    
    def get_open_orders(self):
        """Get all open orders from Coinbase."""
        return [order for order in self.cached_orders if order.status == 'OPEN']
    
    def calculate_potential_account_value(self):
        """
        Calculate the potential account value if all open limit orders were filled.
        
        Returns:
            dict: A dictionary containing current and potential values by currency.
        """
        open_orders = self.get_open_orders()
        balances = {}
        
        # Add in potential values from open orders
        for order in open_orders:
            if order.order_type == 'Limit' and order.status == 'OPEN':

                ## debug
                if order.product_id == 'CORECHAIN-USD':
                    print("\n=========================================")
                    print("CORECHAIN")
                    print(order)
                    print("=========================================\n")

                side = order.order_side
                product_id = order.product_id
                base_currency, quote_currency = product_id.split('-')
                
                # Parse order details
                price = float(order.limit_price)
                leaves_quantity = float(order.leaves_quantity)
                outstanding_hold_amount = float(order.outstanding_hold_amount) # different?
                
                # Initialize currencies if they don't exist in balances
                if base_currency not in balances:
                    balances[base_currency] = {'current': 0, 'potential': 0}
                
                if side == 'SELL':
                    # If sell order is filled, we lose base currency and gain quote currency
                    balances[base_currency]['potential'] += (price * leaves_quantity)
        
        return balances
    
    def refresh_data(self):
        """Force refresh of all cached data using WebSocket."""
        self.fetch_data_via_websocket()
        # Calculate potential account values after fetching data
        account_values = self.calculate_potential_account_value()
        return account_values
