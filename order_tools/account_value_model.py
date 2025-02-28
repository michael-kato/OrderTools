from PyQt5.QtCore import Qt, QAbstractTableModel

class AccountValueTableModel(QAbstractTableModel):
    """Table model for displaying account values in a QTableView."""
    
    def __init__(self, account_values=None):
        super().__init__()
        self._account_values = []
        self._headers = ["Currency", "Potential Gain"]
        
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
                return f"{item['potential_gain']:.8f}"
        
        elif role == Qt.TextAlignmentRole:
            if column == 0:  # Currency
                return Qt.AlignLeft | Qt.AlignVCenter
            return Qt.AlignRight | Qt.AlignVCenter
        
        return None
    
    def update_account_values(self, account_values):
        """
        Update the model with new account values.
        
        Args:
            account_values (dict): Dictionary of account values from CoinbaseClient.
        """
        self.beginResetModel()
        self._account_values = []
        
        for currency, values in account_values.items():
            potential = values["potential_gain"]
            self._account_values.append({
                "currency": currency,
                "potential_gain": potential
            })
        
        # Sort by potential gain value (descending)
        self._account_values.sort(key=lambda x: x["potential_gain"], reverse=True)
        
        self.endResetModel()
