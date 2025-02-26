from PyQt5.QtCore import Qt, QAbstractTableModel
from datetime import datetime

class OrderTableModel(QAbstractTableModel):
    """Table model for displaying Coinbase orders in a QTableView."""
    
    def __init__(self, orders=None):
        super().__init__()
        self._orders = orders or []
        self._headers = ["Product", "Side", "Type", "Price", "Size", "Value", "Created At", "Status"]
    
    def rowCount(self, parent=None):
        return len(self._orders)
    
    def columnCount(self, parent=None):
        return len(self._headers)
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._orders)):
            return None
        
        order = self._orders[index.row()]
        column = index.column()
        
        if role == Qt.DisplayRole:
            if column == 0:  # Product
                return order.product_id
            elif column == 1:  # Side
                return order.order_side
            elif column == 2:  # Type
                return order.order_type
            elif column == 3:  # Price
                price_info = order.limit_price
                return f"{price_info} USD"
            elif column == 4:  # Size
                size_info = order.outstanding_hold_amount
                return f"{size_info} USD"
            elif column == 5:  # Value
                return f"{float(order.total_value_after_fees)} USD"
            elif column == 6:  # Created At
                timestamp = order.creation_time
                if timestamp:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    return dt.strftime("%Y-%m-%d %H:%M:%S")
                return ""
            elif column == 7:  # Status
                return order.status
        
        elif role == Qt.TextAlignmentRole:
            if column in [3, 4, 5]:  # Price, Size, Value
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter
        
        elif role == Qt.BackgroundRole:
            side = order.order_side
            if side == "BUY":
                return Qt.green
            elif side == "SELL":
                return Qt.red
        
        return None
    
    def update_orders(self, orders):
        """Update the model with new orders."""
        self.beginResetModel()
        self._orders = orders
        self.endResetModel()
