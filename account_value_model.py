from PyQt5.QtCore import Qt, QAbstractTableModel
from PyQt5.QtGui import QColor

class AccountValueTableModel(QAbstractTableModel):
    """Table model for displaying account values in a QTableView."""
    
    def __init__(self, account_values=None):
        super().__init__()
        self._account_values = []
        self._headers = ["Currency", "Potential Gain", "Open Orders"]
        
        if account_values:
            self.update_account_values(account_values)
    
    def rowCount(self, parent=None):
        return len(self._account_values)
    
    def columnCount(self, parent=None):
        return len(self._headers)
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._account_values)):
            return None
        
        item = self._account_values[index.row()]
        column = index.column()
        
        if role == Qt.DisplayRole:
            if column == 0:  # Currency
                return item["currency"]
            elif column == 1:  # Potential Gain
                return float(item['potential_gain'])  # Ensure it's a float
            elif column == 2:  # Open Orders
                return item['open_orders']  # Number of open orders
        
        elif role == Qt.TextAlignmentRole:
            if column == 0:  # Currency
                return Qt.AlignLeft | Qt.AlignVCenter
            return Qt.AlignRight | Qt.AlignVCenter
        
        elif role == Qt.BackgroundRole:
            # Check if there is an available balance but no open orders
            if item['available_coins'] > 0 and item['open_orders'] == 0:
                return QColor(255, 165, 0)  # Orange-red color
        
        return None
    
    def update_account_values(self, account_values, open_orders):
        """
        Update the model with new account values and open orders.
        
        Args:
            account_values (dict): Dictionary of account values from CoinbaseClient.
            open_orders (list): List of open orders from CoinbaseClient.
        """
        self.beginResetModel()
        self._account_values = []
        
        # Calculate the number of open orders for each currency
        open_orders_count = {}
        for order in open_orders:
            currency = order.product_id.split('-')[0]
            if currency not in open_orders_count:
                open_orders_count[currency] = 0
            open_orders_count[currency] += 1
        
        for coin, coin_info in account_values.items():
            self._account_values.append({
                "currency": coin,
                "potential_gain": coin_info.potential_gain,
                "open_orders": open_orders_count.get(coin, 0),
                "available_coins": coin_info.available_coins  # Store available coins
            })
        
        # Sort by potential gain value (descending)
        self._account_values.sort(key=lambda x: x["potential_gain"], reverse=True)
        
        self.endResetModel()