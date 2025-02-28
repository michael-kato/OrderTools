from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTableView, QPushButton, QLabel, QComboBox,
                            QLineEdit, QGroupBox, QSplitter, QMessageBox, QAbstractItemView)
from PyQt5.QtCore import Qt, QTimer
from order_model import OrderTableModel
from account_value_model import AccountValueTableModel
import traceback
import time

class MainWindow(QMainWindow):
    """Main window for the Coinbase Order Tracker application."""
    
    def __init__(self, coinbase_client):
        super().__init__()
        self.coinbase_client = coinbase_client
        self.order_model = OrderTableModel()
        self.account_value_model = AccountValueTableModel()
        
        self.init_ui()
        self.setup_connections()
        
        # Initial data fetch
        self.refresh_data()
    
    def init_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Coinbase Order Tracker")
        self.setMinimumSize(900, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Total Potential Gain
        self.total_potential_gain_label = QLabel("<h2>Total Potential Gain: 0.00000000</h2>")
        main_layout.addWidget(self.total_potential_gain_label)
        
        # Create splitter for resizable sections
        splitter = QSplitter(Qt.Vertical)
        
        # Orders section
        orders_widget = QWidget()
        orders_layout = QVBoxLayout(orders_widget)
        
        orders_header = QHBoxLayout()
        orders_label = QLabel("<h2>Open Limit Orders</h2>")
        self.order_filter = QLineEdit()
        self.order_filter.setPlaceholderText("Filter by product (e.g. BTC-USD)")
        orders_header.addWidget(orders_label)
        orders_header.addWidget(self.order_filter)
        
        # Orders table
        self.orders_table = QTableView()
        self.orders_table.setModel(self.order_model)
        self.orders_table.setSortingEnabled(True)
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.horizontalHeader().setStretchLastSection(True)
        
        orders_layout.addLayout(orders_header)
        orders_layout.addWidget(self.orders_table)
        
        # Account value section
        account_widget = QWidget()
        account_layout = QVBoxLayout(account_widget)
        
        account_label = QLabel("<h2>Potential Account Value</h2>")
        account_desc = QLabel("Shows how your account value would change if all open limit orders were filled.")
        account_desc.setWordWrap(True)
        
        # Account value table
        self.account_table = QTableView()
        self.account_table.setModel(self.account_value_model)
        self.account_table.setSortingEnabled(True)
        self.account_table.setAlternatingRowColors(True)
        self.account_table.horizontalHeader().setStretchLastSection(True)
        
        account_layout.addWidget(account_label)
        account_layout.addWidget(account_desc)
        account_layout.addWidget(self.account_table)
        
        # Add both sections to splitter
        splitter.addWidget(orders_widget)
        splitter.addWidget(account_widget)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh Data")
        main_layout.addWidget(self.refresh_button)
        
        # Status label
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
        
        # Stats section
        stats_widget = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_widget)
        
        self.total_orders_label = QLabel("Total Orders: 0")
        stats_layout.addWidget(self.total_orders_label)
        
        self.current_value_label = QLabel("Current Total Value: 0.00 USD")
        stats_layout.addWidget(self.current_value_label)
        
        self.percentage_gain_label = QLabel("Percentage Gain: 0.00%")
        stats_layout.addWidget(self.percentage_gain_label)
        
        # Add stats section to main layout
        main_layout.addWidget(splitter)
        main_layout.addWidget(stats_widget)
        
        self.setCentralWidget(central_widget)
    
    def setup_connections(self):
        """Set up signal/slot connections."""
        self.refresh_button.clicked.connect(self.refresh_data)
        self.order_filter.textChanged.connect(self.filter_orders)
        self.account_table.selectionModel().selectionChanged.connect(self.update_stats_for_selected_coin)
    
    def refresh_data(self):
        """Refresh all data from Coinbase."""
        try:
            self.status_label.setText("Refreshing data...")
            
            # Fetch data via WebSocket and get updated account values
            self.coinbase_client.refresh_data()
            
            # Get open orders
            orders = self.coinbase_client.get_open_orders()
            self.order_model.update_orders(orders)
            
            # Apply filter if one exists
            filter_text = self.order_filter.text()
            if filter_text:
                self.filter_orders(filter_text)
            
            # Update account values in the model
            self.account_value_model.update_account_values(self.coinbase_client.balances)
            
            # Calculate total potential gain
            total_potential_gain = sum(item['potential_gain'] for item in self.coinbase_client.balances.values())
            self.total_potential_gain_label.setText(f"Total Potential Gain: {total_potential_gain:.8f}")
            
            # Resize table columns to contents
            self.orders_table.resizeColumnsToContents()
            self.account_table.resizeColumnsToContents()
            
            self.status_label.setText(f"Data refreshed at {time.strftime('%H:%M:%S')}")
        
        except Exception as e:
            error_message = f"Error refreshing data: {str(e)}"
            self.status_label.setText(error_message)
            QMessageBox.critical(self, "Error", error_message)
            traceback.print_exc()
    
    def filter_orders(self, text):
        """Filter orders table by product ID."""
        try:
            if not text:
                # If filter is empty, show all orders
                self.order_model.update_orders(self.coinbase_client.get_open_orders())
            else:
                # Filter orders by product ID
                all_orders = self.coinbase_client.get_open_orders()
                filtered_orders = [order for order in all_orders if text.upper() in order.get("product_id", "")]
                self.order_model.update_orders(filtered_orders)
            
            self.orders_table.resizeColumnsToContents()
        
        except Exception as e:
            self.status_label.setText(f"Error filtering orders: {str(e)}")
    
    def update_stats_for_selected_coin(self):
        """Update stats for the selected coin in the account table."""
        selected_indexes = self.account_table.selectionModel().selectedRows()
        if not selected_indexes:
            return
        
        selected_index = selected_indexes[0]
        currency = self.account_value_model.data(selected_index, Qt.DisplayRole)
        
        # Find the corresponding account value
        if currency in self.coinbase_client.balances:
            values = self.coinbase_client.balances[currency]
            potential_gain = values['potential_gain']
            current_value = values['current_value']
            percentage_gain = ((potential_gain - current_value) / current_value) * 100 if current_value != 0 else 0
            
            # Update stats labels
            self.total_orders_label.setText(f"Total Orders: {len([order for order in self.coinbase_client.get_open_orders() if order['product_id'].startswith(currency)])}")
            self.current_value_label.setText(f"Current Total Value: {current_value:.2f} USD")
            self.percentage_gain_label.setText(f"Percentage Gain: {percentage_gain:.2f}%")
