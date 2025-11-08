from PyQt5.QtCore import Qt, QAbstractTableModel

class USDPairsTableModel(QAbstractTableModel):
    """Table model for displaying USD pairs with low or zero balance."""
    
    def __init__(self):
        super().__init__()
        self._pairs = []
        self._headers = ["Select", "Currency", "Current Balance ($)", "Symbol"]
        self._selected = set()
    
    def rowCount(self, parent=None):
        return len(self._pairs)
    
    def columnCount(self, parent=None):
        return len(self._headers)
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._pairs)):
            return None
        
        item = self._pairs[index.row()]
        column = index.column()
        
        if role == Qt.DisplayRole:
            if column == 1:  # Currency
                return item["currency"]
            elif column == 2:  # Current Balance
                return f"{item['balance']:.2f}"
            elif column == 3:  # Symbol
                return item["symbol"]
        
        elif role == Qt.CheckStateRole and column == 0:  # Select checkbox
            return Qt.Checked if index.row() in self._selected else Qt.Unchecked
        
        elif role == Qt.TextAlignmentRole:
            if column == 1:
                return Qt.AlignLeft | Qt.AlignVCenter
            return Qt.AlignRight | Qt.AlignVCenter
        
        return None
    
    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.CheckStateRole and index.column() == 0:
            if value == Qt.Checked:
                self._selected.add(index.row())
            else:
                self._selected.discard(index.row())
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
            return True
        return False
    
    def flags(self, index):
        if index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def update_pairs(self, pairs):
        """
        Update the model with new USD pairs.
        
        Args:
            pairs (list): List of dicts with keys: currency, balance, symbol
        """
        self.beginResetModel()
        self._pairs = pairs
        self._selected.clear()
        self.endResetModel()
    
    def get_selected_pairs(self):
        """Get list of selected pair symbols."""
        return [self._pairs[idx]["symbol"] for idx in self._selected]
    
    def select_all(self):
        """Select all pairs."""
        self.beginResetModel()
        self._selected = set(range(len(self._pairs)))
        self.endResetModel()
    
    def deselect_all(self):
        """Deselect all pairs."""
        self.beginResetModel()
        self._selected.clear()
        self.endResetModel()