# Market Buy Tab - Implementation Summary

## New Files

### usd_pairs_model.py
Table model for displaying USD trading pairs where you own less than $20 worth. Features:
- Checkboxes for coin selection
- Displays currency, current balance, and symbol
- Select all/deselect all functionality

## Modified Files

### main.py
Added two new methods to ExchangeClient class:

1. **get_usd_pairs_under_threshold(threshold=20.0)**
   - Fetches all USD trading pairs where current balance < threshold
   - Returns list of pairs with currency, balance, and symbol info
   - Sorts results alphabetically

2. **market_buy_multiple(symbols, usd_amount_per_coin)**
   - Executes market buy orders for multiple symbols
   - Calculates amount based on current price and USD amount
   - Returns success/failed results for each order

### ui.py
Added new "Market Buy" tab with:
- Table showing USD pairs under $20 threshold
- Select all/deselect all buttons
- Refresh list button
- USD amount input (configurable per coin)
- Execute market buy button (with confirmation dialog)
- Status display showing results

## Usage

1. Open the "Market Buy" tab
2. Click "Refresh List" to load all USD pairs where you own < $20
3. Select coins using checkboxes (or use Select All button)
4. Set the USD amount to spend per coin
5. Click "Execute Market Buy" to purchase selected coins
6. Confirmation dialog shows total cost before executing

## Notes

- Threshold is set to $20 but can be modified in the code
- Market orders execute at current price
- Failed orders are reported separately from successful ones
- Both tabs automatically refresh after market buys complete