import json
from coinbase_advanced.coinbase.rest import RESTClient
from coinbase_advanced.coinbase.websocket import WSClient, WebsocketResponse

class CoinbaseClient:
    """Client for interacting with the Coinbase Advanced Trade API via WebSocket."""
    
    def __init__(self, api_key_file):
        """
        Initialize the Coinbase WebSocket client.
        
        Args:
            api_key (str, optional): Coinbase API key. If not provided, will attempt to load from environment.
            api_secret (str, optional): Coinbase API secret. If not provided, will attempt to load from environment.
        """
        self.api_key_file = api_key_file

        self.ws_client = WSClient(key_file=api_key_file, on_message=self.on_message)
        self.rest_client = RESTClient(key_file=api_key_file)

        """
        FOR GPT: self.accounts data structure looks like this
        {'uuid': '7799066c-9fa6-5e77-b6b4-687e609521a5', 'name': 'PNUT Wallet', 'currency': 'PNUT', 'available_balance': {'value': '0.01', 'currency': 'PNUT'}, 'default': True, 'active': True, 'created_at': '2025-01-14T19:35:30.318Z', 'updated_at': '2025-02-25T20:02:22.923824Z', 'deleted_at': None, 'type': 'ACCOUNT_TYPE_CRYPTO', 'ready': True, 'hold': {'value': '283.12', 'currency': 'PNUT'}, 'retail_portfolio_id': 'aa1fb89d-364f-51f7-a02e-73a06312a0a6', 'platform': 'ACCOUNT_PLATFORM_CONSUMER'}
        """
        self.accounts = {}
        self.available_balances = {}

        """
        FOR GPT, self.cached_orders data structure looks like this. 
        {'avg_price': '0', 'cancel_reason': '', 'client_order_id': 'alt-9e8984effcfa0d37afc6da81639c95b2', 'completion_percentage': '0', 'contract_expiry_type': 'UNKNOWN_CONTRACT_EXPIRY_TYPE', 'cumulative_quantity': '0', 'filled_value': '0', 'leaves_quantity': '6.56', 'limit_price': '3.575', 'number_of_fills': '0', 'order_id': 'b18a763a-9e2d-4042-aba0-ad369fb18373', 'order_side': 'SELL', 'order_type': 'Limit', 'outstanding_hold_amount': '6.56', 'post_only': 'true', 'product_id': 'CORECHAIN-USD', 'product_type': 'SPOT', 'reject_reason': None, 'retail_portfolio_id': 'aa1fb89d-364f-51f7-a02e-73a06312a0a6', 'risk_managed_by': 'UNKNOWN_RISK_MANAGEMENT_TYPE', 'status': 'OPEN', 'stop_price': '', 'time_in_force': 'GOOD_UNTIL_CANCELLED', 'total_fees': '0', 'total_value_after_fees': '23.416822', 'trigger_status': 'INVALID_ORDER_TYPE', 'creation_time': '2025-02-27T18:42:39.772546Z', 'end_time': '0001-01-01T00:00:00Z', 'start_time': '0001-01-01T00:00:00Z', 'reject_Reason': ''}
        """
        self.cached_orders = []

    def fetch_data_via_websocket(self):
        """Fetch data using WebSocket and update caches."""

        # Connect and subscribe to channels
        self.ws_client.open()
        
        self.ws_client.subscribe(product_ids=[], channels=['user'])
        self.ws_client.sleep_with_exception_check(1)
        self.ws_client.unsubscribe(product_ids=[], channels=['user'])
        
        # Disconnect after fetching data
        self.ws_client.close()

    def on_message(self, message):
        """Handle incoming WebSocket messages."""

        data = json.loads(message)
        ws_object = WebsocketResponse(data)
        if ws_object.channel == "user" :
            for event in ws_object.events:
                self.cached_orders.extend(event['orders'])
        else:
            return
    
    def get_open_orders(self):
        """Get all open orders from Coinbase."""
        return [order for order in self.cached_orders if order.status == 'OPEN']
    
    def calculate_potential_account_value(self):
        """
        Calculate the potential account value if all open limit orders were filled
        and available balances were sold at the highest limit sell price.
        
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
                size = float(order.leaves_quantity)
                
                # Initialize currencies if they don't exist in balances
                if base_currency not in balances:
                    balances[base_currency] = {'current': 0, 'potential': 0}
                
                if side == 'SELL':
                    # If sell order is filled, we lose base currency and gain quote currency
                    balances[base_currency]['potential'] += (price * size)
        
        # Calculate potential gains from available balances
        for currency, balance in balances.items():
            if balance['current'] > 0:
                # Find the highest limit sell order for this currency
                highest_sell_price = max(
                    (float(order.limit_price) for order in open_orders
                     if order.order_side == 'SELL' and order.product_id.startswith(currency)),
                    default=0
                )
                if highest_sell_price > 0:
                    # Calculate potential gain if available balance is sold at the highest sell price
                    balance['potential'] += balance['current'] * highest_sell_price
        
        return balances
    
    def refresh_data(self):
        """Force refresh of all cached data using WebSocket."""
        self.fetch_data_via_websocket()
        
        self.accounts = self.rest_client.get_accounts().accounts
        for account in self.accounts:
            self.available_balances[account.available_balance['currency']] = account.available_balance['value']

        # Calculate potential account values after fetching data
        account_values = self.calculate_potential_account_value()
        return account_values
