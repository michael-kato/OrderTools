# Coinbase Order Tracker

A desktop application that allows you to query and manage your open spot limit orders on Coinbase, with the ability to calculate the potential value of your account if all limit orders were filled.

## Features

- **View Open Limit Orders**: Displays all your open limit orders with details like product, price, size, and total value.
- **Filter Orders**: Narrow down orders by product ID.
- **Calculate Potential Account Value**: Shows how your account balances would change if all limit orders were filled.
- **Cancel Orders**: Cancel all orders for a selected coin.
- **Market Sell**: Market sell the entire position for a selected coin.
- **Auto-refresh**: Automatically updates data from Coinbase to keep information current.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/coinbase-order-tracker.git
   cd coinbase-order-tracker
   ```

2. Install the package:
   ```bash
   pip install -e .
   ```

## Configuration

You need to set up your Coinbase API credentials before using the application. You can do this by providing a JSON file with your API key details:

- Create a file named `cdp_api_key_ordertools_trade.json` with the following structure:
  ```json
  {
    "api_key": "your_api_key",
    "api_secret": "your_api_secret"
  }
  ```

## Getting Coinbase API Keys

1. Log in to your Coinbase Advanced account.
2. Go to API settings.
3. Create a new API key with the following permissions:
   - View account information
   - View orders
4. Make sure to save your API secret as it will only be shown once.

## Usage

Run the application:

```bash
python main.py
```

### Features

1. **Orders Table**: Displays all your open limit orders with details like product, price, size, and total value.
2. **Filter**: Use the filter box to narrow down orders by product ID.
3. **Account Value Table**: Shows how your account balances would change if all limit orders were filled.
4. **Cancel Orders**: Cancel all orders for a selected coin.
5. **Market Sell**: Market sell the entire position for a selected coin.
6. **Refresh Button**: Manually update data from Coinbase.

## Project Structure

- `main.py`: Entry point for the application.
- `coinbase_client.py`: Handles API communication with Coinbase.
- `main_window.py`: Main application window.
- `account_value_model.py`: Data model for account value table.

## Requirements

- Python 3.6+
- PyQt5 5.15.2+
- Requests 2.25.0+

## License

MIT