# Coinbase Order Tracker

A desktop application that allows you to query and sort your open spot limit orders on Coinbase, with the ability to calculate the potential value of your account if all limit orders were filled.

## Features

- View all open limit orders on Coinbase
- Filter orders by product (e.g., BTC-USD)
- Calculate potential account value if all limit orders were filled
- See the percentage change in account value for each currency
- Cancel all orders for a selected coin
- Market sell the entire position for a selected coin
- Auto-refresh functionality to keep data up-to-date

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/your-username/coinbase-order-tracker.git
   cd coinbase-order-tracker
   ```

2. Install the package:
   ```
   pip install -e .
   ```

## Configuration

You need to set up your Coinbase API credentials before using the application. There are two ways to do this:

### Option 1: Environment Variables

Set the following environment variables:

```
COINBASE_API_KEY=your_api_key
COINBASE_API_SECRET=your_api_secret
```

### Option 2: Modify the code

Alternatively, you can directly provide your API credentials when initializing the CoinbaseClient in `main.py`:

```python
# Initialize the Coinbase client
coinbase_client = CoinbaseClient(
    api_key="your_api_key",
    api_secret="your_api_secret"
)
```

## Getting Coinbase API Keys

1. Log in to your Coinbase Advanced account
2. Go to API settings
3. Create a new API key with the following permissions:
   - View account information
   - View orders
4. Make sure to save your API secret as it will only be shown once

## Usage

Run the application:

```
coinbase-order-tracker
```

Or run directly with Python:

```
python main.py
```

### Features

1. **Orders Table**: Displays all your open limit orders with details like product, price, size, and total value
2. **Filter**: Use the filter box to narrow down orders by product ID
3. **Account Value Table**: Shows how your account balances would change if all limit orders were filled
4. **Cancel Orders**: Cancel all orders for a selected coin
5. **Market Sell**: Market sell the entire position for a selected coin
6. **Refresh Button**: Manually update data from Coinbase

## Project Structure

- `main.py`: Entry point for the application
- `logic/`: Contains business logic and data models
  - `coinbase_client.py`: Handles API communication with Coinbase
  - `order_model.py`: Data model for orders table
  - `account_value_model.py`: Data model for account value table
- `ui/`: Contains UI components
  - `main_window.py`: Main application window

## Requirements

- Python 3.6+
- PyQt5 5.15.2+
- Requests 2.25.0+

## License

MIT