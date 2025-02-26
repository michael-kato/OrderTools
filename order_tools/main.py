import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow
from coinbase_client import CoinbaseClient


def main():
    """Main entry point for the Coinbase Order Tracker application."""
    # Initialize the application
    app = QApplication(sys.argv)
    app.setApplicationName("Coinbase Order Tracker")
    
    # Initialize the Coinbase client
    coinbase_client = CoinbaseClient(api_key="organizations/beefaea2-3517-461a-95a0-2fc091251865/apiKeys/022fd8a9-e259-4b4f-b9fd-7362a19a4b25", api_secret="-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEIPQz28pZWTbTq6Pfe7pB6tUVTKYR/Mf1S2yYcLoGxzzwoAoGCCqGSM49\nAwEHoUQDQgAEGSXxx7t2pLoVX578JZe2ChoxiNTMErX7yPfV6V/s1XxwxAdDH28q\nMjHkMLbQkfyYTLXbK28bFH9Dw/vTEqo+UA==\n-----END EC PRIVATE KEY-----\n")
    
    # Initialize and show the main window
    main_window = MainWindow(coinbase_client)
    main_window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
