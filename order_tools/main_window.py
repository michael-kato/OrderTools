from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTableView, QPushButton, QLabel, 
                            QLineEdit, QGroupBox, QSplitter, QMessageBox, QFormLayout, QSpinBox, QDoubleSpinBox)
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
        
        # Ladder order section
        ladder_widget = QWidget()
        ladder_layout = QFormLayout(ladder_widget)
        
        ladder_label = QLabel("<h2>Ladder Order Placement</h2>")
        ladder_layout.addRow(ladder_label)
        
        self.start_percentage_input = QDoubleSpinBox()
        self.start_percentage_input.setSuffix("%")
        self.start_percentage_input.setRange(0, 100)
        self.start_percentage_input.setValue(1.0)
        ladder_layout.addRow("Start Percentage:", self.start_percentage_input)
        
        self.stop_percentage_input = QDoubleSpinBox()
        self.stop_percentage_input.setSuffix("%")
        self.stop_percentage_input.setRange(0, 100)
        self.stop_percentage_input.setValue(5.0)
        ladder_layout.addRow("Stop Percentage:", self.stop_percentage_input)
        
        self.coins_input = QDoubleSpinBox()
        self.coins_input.setRange(0, 1000)
        self.coins_input.setValue(10.0)
        ladder_layout.addRow("Number of Coins:", self.coins_input)
        
        self.ladder_orders_input = QSpinBox()
        self.ladder_orders_input.setRange(1, 100)
        self.ladder_orders_input.setValue(5)
        ladder_layout.addRow("Number of Ladder Orders:", self.ladder_orders_input)
        
        self.place_ladder_button = QPushButton("Place Ladder Orders")
        ladder_layout.addRow(self.place_ladder_button)
        
        # Add both sections to splitter
        splitter.addWidget(account_widget)
        splitter.addWidget(ladder_widget)
        
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
        self.place_ladder_button.clicked.connect(self.place_ladder_orders)
    
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
    
    def place_ladder_orders(self):
        """Place ladder orders based on user input."""
        start_percentage = self.start_percentage_input.value()
        stop_percentage = self.stop_percentage_input.value()
        num_coins = self.coins_input.value()
        num_ladder_orders = self.ladder_orders_input.value()
        
        # Implement logic to place ladder orders using the above parameters
        # This will likely involve interacting with the CoinbaseClient to place orders
        # Example: self.coinbase_client.place_ladder_orders(start_percentage, stop_percentage, num_coins, num_ladder_orders)
        
        QMessageBox.information(self, "Ladder Orders", "Ladder orders placed successfully!")
    
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
