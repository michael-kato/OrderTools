import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "coinbase_advanced"))
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow
from coinbase_client import CoinbaseClient


def main():
    """Main entry point for the Coinbase Order Tracker application."""
    # Initialize the application
    app = QApplication(sys.argv)
    app.setApplicationName("Coinbase Order Tracker")
    
    # Initialize the Coinbase client
    coinbase_client = CoinbaseClient(api_key_file="cdp_api_key_ordertools_trade.json")
    
    # Initialize and show the main window
    main_window = MainWindow(coinbase_client)
    main_window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
