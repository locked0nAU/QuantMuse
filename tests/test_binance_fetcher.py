import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Ensure we can import data_service
sys.path.insert(0, os.getcwd())

# We need to mock these modules before they are imported by BinanceFetcher
mock_modules = {
    "pandas": MagicMock(),
    "binance": MagicMock(),
    "binance.client": MagicMock(),
    "binance.websockets": MagicMock(),
    "binance.exceptions": MagicMock(),
    "requests": MagicMock()
}

# Define some specific behavior for the mocks
class MockBinanceAPIException(Exception):
    def __init__(self, response=None, status_code=None, text=None):
        self.response = response
        self.status_code = status_code
        self.text = text

mock_modules["binance.exceptions"].BinanceAPIException = MockBinanceAPIException

# Mock DataFrame to satisfy basic operations in BinanceFetcher
class MockDataFrame:
    def __init__(self, data=None, **kwargs):
        self.data = data if data is not None else []
    def __len__(self):
        return len(self.data)
    def __getitem__(self, key):
        return MagicMock()
    def __setitem__(self, key, value):
        pass
    def set_index(self, *args, **kwargs):
        return self
    def astype(self, *args, **kwargs):
        return self

mock_modules["pandas"].DataFrame = MockDataFrame
mock_modules["pandas"].to_datetime.return_value = MagicMock()

# Apply the mocks to sys.modules
for name, m in mock_modules.items():
    sys.modules[name] = m

from data_service.fetchers.binance_fetcher import BinanceFetcher

class TestBinanceFetcher(unittest.TestCase):
    """Test cases for BinanceFetcher"""

    def setUp(self):
        """Set up test fixtures"""
        # Patch the Client class used by BinanceFetcher
        self.client_patcher = patch('data_service.fetchers.binance_fetcher.Client')
        self.mock_client_class = self.client_patcher.start()
        
        self.mock_client_instance = Mock()
        self.mock_client_class.return_value = self.mock_client_instance
        
        # Create fetcher with mocked client
        self.fetcher = BinanceFetcher()

    def tearDown(self):
        """Clean up after each test"""
        self.client_patcher.stop()

    def test_initialization(self):
        """Test if fetcher initializes correctly"""
        self.assertIsNotNone(self.fetcher.client)

    def test_fetch_historical_data_error(self):
        """Test error handling in historical data fetching"""
        # Simulate an API error
        self.mock_client_instance.get_klines.side_effect = Exception("API Error")
        
        from data_service.utils.exceptions import DataFetchError
        with self.assertRaises(DataFetchError):
            self.fetcher.fetch_historical_data("BTCUSDT")

    def test_websocket_error_handling(self):
        """Test error handling in websocket message processing"""
        # Patch BinanceSocketManager where it's used
        with patch('data_service.fetchers.binance_fetcher.BinanceSocketManager') as MockBSM:
            mock_bsm_instance = MockBSM.return_value
            self.fetcher.bm = None

            # Capture the callback passed to start_kline_socket
            callback_captured = None
            def mock_start_kline_socket(symbol, callback, interval):
                nonlocal callback_captured
                callback_captured = callback
                return "test_conn_key"

            mock_bsm_instance.start_kline_socket.side_effect = mock_start_kline_socket

            # Initialize websocket to get the handle_socket_message callback
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.fetcher.start_websocket("BTCUSDT", Mock()))

            self.assertIsNotNone(callback_captured)

            # Test with malformed message to trigger exception in handle_socket_message
            malformed_msg = {'e': 'kline'} # Missing expected 's', 'E', 'k' keys

            with self.assertLogs('data_service.fetchers.binance_fetcher', level='ERROR') as cm:
                callback_captured(malformed_msg)
                self.assertTrue(any("Error processing websocket message" in output for output in cm.output))

if __name__ == '__main__':
    unittest.main()
