import os
import time
import hmac
import hashlib
from urllib.parse import urlencode
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configuration
API_KEY = os.getenv('ASTER_API_KEY')
API_SECRET = os.getenv('ASTER_API_SECRET')
BASE_URL = 'https://sapi.asterdex.com/v1'  # Spot API base URL

def get_timestamp():
    """Generate current timestamp in ms."""
    return int(time.time() * 1000)

def sign_request(params):
    """Generate HMAC-SHA256 signature for query string."""
    query_string = urlencode(sorted(params.items()))
    signature = hmac.new(
        API_SECRET.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature

def get_account_balance():
    """Fetch account balances."""
    timestamp = get_timestamp()
    params = {'timestamp': timestamp, 'recvWindow': 5000}
    params['signature'] = sign_request(params)
    headers = {'X-MBX-APIKEY': API_KEY}
    try:
        response = requests.get(f'{BASE_URL}/account', params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Balance fetch failed: {e}")
        return None

def place_spot_order(action, symbol, amount):
    """
    Place a spot market order.
    - action: 'buy' or 'sell'
    - symbol: e.g., 'ETHUSDC'
    - amount: quote amount for buy (USDC), base amount for sell (ETH)
    """
    timestamp = get_timestamp()
    side = 'BUY' if action.lower() == 'buy' else 'SELL'
    params = {
        'symbol': symbol,
        'side': side,
        'type': 'MARKET',
        'timestamp': timestamp,
        'recvWindow': 5000
    }
    if action.lower() == 'buy':
        params['quoteOrderQty'] = amount  # Buy with fixed USDC amount
    else:
        params['quantity'] = amount  # Sell fixed token amount
    params['signature'] = sign_request(params)
    headers = {'X-MBX-APIKEY': API_KEY}
    try:
        response = requests.post(f'{BASE_URL}/order', params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {'error': str(e), 'statusCode': response.status_code if response else None}

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle TradingView alert POST."""
    if not request.is_json:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    data = request.get_json()
    action = data.get('action')
    symbol = data.get('symbol')
    amount = float(data.get('amount', 0))
    
    if not action or not symbol or amount <= 0:
        return jsonify({'error': 'Missing action, symbol, or valid amount'}), 400
    
    if action.lower() not in ['buy', 'sell']:
        return jsonify({'error': 'Action must be "buy" or "sell"'}), 400
    
    # Validate symbol (optional: fetch valid symbols from /exchangeInfo)
    if not symbol.endswith('USDC'):  # Basic validation; enhance as needed
        return jsonify({'error': 'Symbol must end with USDC (e.g., ETHUSDC)'}), 400
    
    # Check balance (optional)
    balance = get_account_balance()
    if balance:
        print(f"Current balances: {balance}")
    
    # Place order
    result = place_spot_order(action, symbol, amount)
    
    if 'orderId' in result:
        print(f"Order placed: {action} {amount} {symbol} - Order ID: {result['orderId']}")
        return jsonify({'status': 'success', 'order': result}), 200
    else:
        print(f"Order failed: {result}")
        return jsonify({'status': 'error', 'details': result}), 500

@app.route('/', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'Bot running'}), 200

if __name__ == '__main__':
    if not API_KEY or not API_SECRET:
        raise ValueError("Set ASTER_API_KEY and ASTER_API_SECRET environment variables.")
    app.run(host='0.0.0.0', port=5000, debug=False)