import json
from coinbase_advanced.coinbase.rest import RESTClient
from coinbase_advanced.coinbase.websocket import WSClient, WebsocketResponse


"""
IDEAS:
Add stink bid sell orders and stink bid buy orders on all charts
Add signals bot that looks for abnormal volume spikes. Start tracking paper trades for the bot's success. 
Add candlestick charts.
"""


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
        self.accounts = []
        self.balances = {}
        self.non_tradable_coins = [] # this is either a list of delisted coins or maybe coins on the roadmap. Might be worth a punt?
        self.total_potential_gain = 0
        """
        FOR GPT, self.cached_orders data structure looks like this. 
        {'avg_price': '0', 'cancel_reason': '', 'client_order_id': 'alt-9e8984effcfa0d37afc6da81639c95b2', 'completion_percentage': '0', 'contract_expiry_type': 'UNKNOWN_CONTRACT_EXPIRY_TYPE', 'cumulative_quantity': '0', 'filled_value': '0', 'leaves_quantity': '6.56', 'limit_price': '3.575', 'number_of_fills': '0', 'order_id': 'b18a763a-9e2d-4042-aba0-ad369fb18373', 'order_side': 'SELL', 'order_type': 'Limit', 'outstanding_hold_amount': '6.56', 'post_only': 'true', 'product_id': 'CORECHAIN-USD', 'product_type': 'SPOT', 'reject_reason': None, 'retail_portfolio_id': 'aa1fb89d-364f-51f7-a02e-73a06312a0a6', 'risk_managed_by': 'UNKNOWN_RISK_MANAGEMENT_TYPE', 'status': 'OPEN', 'stop_price': '', 'time_in_force': 'GOOD_UNTIL_CANCELLED', 'total_fees': '0', 'total_value_after_fees': '23.416822', 'trigger_status': 'INVALID_ORDER_TYPE', 'creation_time': '2025-02-27T18:42:39.772546Z', 'end_time': '0001-01-01T00:00:00Z', 'start_time': '0001-01-01T00:00:00Z', 'reject_Reason': ''}
        """
        self.cached_orders = []

        self.debug_currency = "XRP"


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
        Calculate the potential account value if all open limit sell orders were filled
        and available balances were sold at the highest limit sell price.
        
        Returns:
            dict: A dictionary containing current and potential values by currency.
        """
        open_orders = self.get_open_orders()
        
        # Add in potential values from open orders
        for order in open_orders:
            if order.order_type == 'Limit' and order.status == 'OPEN':
                side = order.order_side
                product_id = order.product_id
                coin = product_id.split('-')[0]
                
                # Parse order details
                price = float(order.limit_price)
                size = float(order.leaves_quantity)
                
                # Initialize currencies if they don't exist in balances
                if coin not in self.balances:
                    self.balances[coin] = CoinInfo()
                
                if side == 'SELL':
                    # If sell order is filled, we lose base currency and gain quote currency
                    self.balances[coin].potential_gain += (price * size)

                    if coin == self.debug_currency:
                        print(coin, price, size, 'new total', self.balances[coin].potential_gain)
        
        # Calculate potential gains from available balances
        for coin, coin_info in self.balances.items():
            if coin_info.current_value > 0:
                # Find the highest limit sell order for this currency
                highest_sell_price = max(
                    (float(order.limit_price) for order in open_orders
                     if order.order_side == 'SELL' and order.product_id == f"{coin}-USD"),
                    default=0
                )

                if highest_sell_price > 0:
                    # Calculate potential gain if available balance is sold at the highest sell price
                    coin_info.potential_gain += coin_info.available_coins * highest_sell_price

                    if coin == self.debug_currency:
                        print('potential free coins value', coin, highest_sell_price, coin_info.available_coins, '=', coin_info.available_coins * highest_sell_price)
        
        # Calculate total potential gain
        self.total_potential_gain = sum(coin_info.potential_gain for coin_info in self.balances.values())
    
    def refresh_data(self):
        """Force refresh of all cached data using WebSocket."""

        self.fetch_data_via_websocket()
        
        # zero out everything before refresh
        #self.balances = {}
        #self.cached_orders = []

        # get all active accounts/balances
        cursor = None
        accounts = self.rest_client.get_accounts(limit=250)
        # "Could not find user's accounts information
        while accounts.has_next == True:
            accounts = self.rest_client.get_accounts(limit=250, cursor=cursor)
            cursor = accounts.cursor # save our place for next fetch
            self.accounts.extend(accounts.accounts)

        product_ids = [f"{p.available_balance['currency']}-USD" for p in self.accounts]
        # skip coins that are not tradable
        tradable_coins_info = self.rest_client.get_public_products(product_ids=product_ids, product_type='SPOT', get_tradability_status=True)
        tradable_coins = [x['base_currency_id'] for x in tradable_coins_info.products if x.trading_disabled == False]

        for account in self.accounts:
            coin = account.available_balance['currency']
            if coin not in self.balances:
                self.balances[coin] = CoinInfo()

            if coin not in tradable_coins:
                print(coin, 'not tradable')
                self.non_tradable_coins.append(coin)
                continue
        
        coins = [coin+'-USD' for coin in self.balances.keys()]
        products = self.rest_client.get_products(product_ids=coins, get_tradability_status=True).products
        for product in products:
            if product.price:
                price = float(product.price)
            else:
                price = 0.0

            self.balances[coin].available_coins = float(account.available_balance['value'])
            self.balances[coin].current_value = (self.balances[coin].available_coins + float(account.hold['value'])) * price

            if coin == self.debug_currency:
                print(coin, "current price", price, "current coins", (self.balances[coin].available_coins + float(account.hold['value'])), "current value", self.balances[coin].current_value)

        # Calculate potential account values after fetching data
        self.calculate_potential_account_value()

    def cancel_all_orders(self, coin):
        # Cancel all orders for a specific coin
        open_orders = self.get_open_orders()
        order_ids_to_cancel = [order.order_id for order in open_orders if order.product_id == coin+'-USD']
        if order_ids_to_cancel:
            self.rest_client.cancel_orders(order_ids_to_cancel)

    def market_sell_entire_position(self, coin):
        # Market sell the entire position for a specific coin
        if coin in self.balances:
            available_coins = self.balances[coin].available_coins
            if available_coins > 0:
                self.rest_client.market_order(
                    product_id=f"{coin}-USD",
                    side="sell",
                    base_size=str(available_coins)
                )


class CoinInfo():
    def __init__(self):
        self.available_coins = 0.0
        self.current_value = 0.0
        self.potential_gain = 0.0