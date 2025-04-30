# Crypto Order Tracker

A desktop application that allows you to query and manage your open spot limit orders across multiple cryptocurrency exchanges, with the ability to calculate the potential value of your account if all limit orders were filled.

## Features

- **Multi-Exchange Support**: Supports exchanges like Coinbase Pro and Mexc using the `ccxt` library.
- **View Open Limit Orders**: Displays all your open limit orders with details like product, price, size, and total value.
- **Filter Orders**: Narrow down orders by product ID.
- **Calculate Potential Account Value**: Shows how your account balances would change if all limit orders were filled.
- **Cancel Orders**: Cancel all orders for a selected coin.
- **Market Sell**: Market sell the entire position for a selected coin.
- **Auto-refresh**: Automatically updates data from the exchange to keep information current.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/crypto-order-tracker.git
   cd crypto-order-tracker
   ```

2. Install the package:
   ```bash
   pip install -e .
   ```

## Configuration

You need to set up your API credentials for the exchange you want to use. You can do this by providing a JSON file with your API key details:

- Create a file named `api_credentials.json` with the following structure:
  ```json
  {
    "exchange": "mexc",
    "api_key": "your_api_key",
    "api_secret": "your_api_secret"
  }
  ```

## Supported Exchanges

This application uses the `ccxt` library, which supports a wide range of cryptocurrency exchanges. For a full list of supported exchanges, visit the [ccxt documentation](https://github.com/ccxt/ccxt).

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
6. **Refresh Button**: Manually update data from the exchange.

## Project Structure

- `main.py`: Entry point for the application.
- `coinbase_client.py` (renamed to `exchange_client.py`): Handles API communication with exchanges using `ccxt`.
- `main_window.py`: Main application window.
- `account_value_model.py`: Data model for account value table.

## Requirements

- Python 3.6+
- PyQt5 5.15.2+
- ccxt 3.0.0+

## License

MIT