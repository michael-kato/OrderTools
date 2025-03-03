from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QTableView, QPushButton, QLabel, 
                            QGroupBox, QSplitter, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt
from account_value_model import AccountValueTableModel
import traceback
import time

class MainWindow(QMainWindow):
    """Main window for the Coinbase Order Tracker application."""
    
    def __init__(self, coinbase_client):
        super().__init__()
        self.coinbase_client = coinbase_client
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
        
        # Create splitter for resizable sections
        splitter = QSplitter(Qt.Vertical)
        
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
        self.account_table.setSelectionBehavior(QTableView.SelectRows)
        
        account_layout.addWidget(account_label)
        account_layout.addWidget(account_desc)
        account_layout.addWidget(self.account_table)
        
        # Add account widget to splitter
        splitter.addWidget(account_widget)
        
        # Buttons for actions
        action_buttons_widget = QWidget()
        action_buttons_layout = QHBoxLayout(action_buttons_widget)
        
        self.cancel_orders_button = QPushButton("Cancel All Orders")
        self.market_sell_button = QPushButton("Market Sell Entire Position")
        
        action_buttons_layout.addWidget(self.cancel_orders_button)
        action_buttons_layout.addWidget(self.market_sell_button)
        
        account_layout.addWidget(action_buttons_widget)
        
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
        
        # Total Potential Gain and Refresh button at the bottom
        self.total_potential_gain_label = QLabel("<h2>Total Potential Gain: 0.00000000</h2>")
        main_layout.addWidget(self.total_potential_gain_label)
        
        # Status label
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)

        self.refresh_button = QPushButton("Refresh Data")
        main_layout.addWidget(self.refresh_button)
        
        self.setCentralWidget(central_widget)
    
    def setup_connections(self):
        """Set up signal/slot connections."""
        self.refresh_button.clicked.connect(self.refresh_data)
        self.account_table.selectionModel().selectionChanged.connect(self.update_stats_for_selected_coin)
        self.cancel_orders_button.clicked.connect(self.cancel_all_orders)
        self.market_sell_button.clicked.connect(self.market_sell_entire_position)
    
    def refresh_data(self):
        """Refresh all data from Coinbase."""
        try:
            self.status_label.setText("Refreshing data...")
            
            # Fetch data via WebSocket and get updated account values
            self.coinbase_client.refresh_data()
            
            # Get open orders
            orders = self.coinbase_client.get_open_orders()
            
            # Update account values in the model
            self.account_value_model.update_account_values(self.coinbase_client.balances, orders)
            
            # Calculate total potential gain
            total_potential_gain = sum(coin_info.potential_gain for coin_info in self.coinbase_client.balances.values())
            self.total_potential_gain_label.setText(f"Total Potential Gain: {total_potential_gain:.8f}")
            
            # Resize table columns to contents
            self.account_table.resizeColumnsToContents()
            
            self.status_label.setText(f"Data refreshed at {time.strftime('%H:%M:%S')}")
        
        except Exception as e:
            error_message = f"Error refreshing data: {str(e)}"
            self.status_label.setText(error_message)
            QMessageBox.critical(self, "Error", error_message)
            traceback.print_exc()
    
    def cancel_all_orders(self):
        """Cancel all orders for the selected coin."""
        selected_indexes = self.account_table.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "Warning", "No coin selected.")
            return
        
        selected_index = selected_indexes[0]
        coin = self.account_value_model.data(selected_index, Qt.DisplayRole)
        
        try:
            self.coinbase_client.cancel_all_orders(coin)
            QMessageBox.information(self, "Success", f"All orders for {coin} have been canceled.")
            self.refresh_data()
        except Exception as e:
            error_message = f"Error canceling orders: {str(e)}"
            QMessageBox.critical(self, "Error", error_message)
            traceback.print_exc()
    
    def market_sell_entire_position(self):
        """Market sell the entire position for the selected coin."""
        selected_indexes = self.account_table.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "Warning", "No coin selected.")
            return
        
        selected_index = selected_indexes[0]
        coin = self.account_value_model.data(selected_index, Qt.DisplayRole)
        
        try:
            self.coinbase_client.market_sell_entire_position(coin)
            QMessageBox.information(self, "Success", f"Entire position for {coin} has been sold.")
            self.refresh_data()
        except Exception as e:
            error_message = f"Error selling position: {str(e)}"
            QMessageBox.critical(self, "Error", error_message)
            traceback.print_exc()
    
    def update_stats_for_selected_coin(self):
        """Update stats for the selected coin in the account table."""
        selected_indexes = self.account_table.selectionModel().selectedRows()
        if not selected_indexes:
            return
        
        selected_index = selected_indexes[0]
        coin = self.account_value_model.data(selected_index, Qt.DisplayRole)
        
        # Find the corresponding account value
        if coin in self.coinbase_client.balances:
            coin_info = self.coinbase_client.balances[coin]
            potential_gain = coin_info.potential_gain
            current_value = coin_info.current_value
            percentage_gain = ((potential_gain - current_value) / current_value) * 100 if current_value != 0 else 0
            
            # Update stats labels
            self.total_orders_label.setText(f"Total Orders: {len([order for order in self.coinbase_client.get_open_orders() if order['product_id'].startswith(coin)])}")
            self.current_value_label.setText(f"Current Total Value: {current_value:.2f} USD")
            self.percentage_gain_label.setText(f"Percentage Gain: {percentage_gain:.2f}%")
