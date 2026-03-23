import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

class TestStrategyBase(unittest.TestCase):
    def setUp(self):
        self.name = "TestStrategy"
        self.description = "A strategy for testing"

        # Patch pandas and other modules only during the import of strategy_base
        with patch.dict('sys.modules', {
            'pandas': MagicMock(),
            'numpy': MagicMock(),
            'scipy': MagicMock(),
            'scipy.optimize': MagicMock()
        }):
            from data_service.strategies.strategy_base import StrategyBase, StrategyResult
            self.StrategyResult = StrategyResult

            class ConcreteStrategy(StrategyBase):
                def generate_signals(self, factor_data, price_data, **kwargs):
                    pass
            self.strategy = ConcreteStrategy(self.name, self.description)

    def test_calculate_performance_metrics_standard(self):
        """Test with standard data"""
        result = self.StrategyResult(
            strategy_name=self.name,
            selected_stocks=['AAPL', 'GOOGL'],
            weights={'AAPL': 0.6, 'GOOGL': 0.4},
            parameters={},
            execution_time=datetime.now(),
            performance_metrics={},
            metadata={}
        )
        # price_data is not used in the default implementation
        metrics = self.strategy.calculate_performance_metrics(result, MagicMock())

        self.assertEqual(metrics['num_stocks'], 2)
        self.assertEqual(metrics['total_weight'], 1.0)
        self.assertEqual(metrics['max_weight'], 0.6)
        self.assertEqual(metrics['min_weight'], 0.4)

    def test_calculate_performance_metrics_empty(self):
        """Test with empty data"""
        result = self.StrategyResult(
            strategy_name=self.name,
            selected_stocks=[],
            weights={},
            parameters={},
            execution_time=datetime.now(),
            performance_metrics={},
            metadata={}
        )
        metrics = self.strategy.calculate_performance_metrics(result, MagicMock())

        self.assertEqual(metrics['num_stocks'], 0)
        self.assertEqual(metrics['total_weight'], 0.0)
        self.assertEqual(metrics['max_weight'], 0.0)
        self.assertEqual(metrics['min_weight'], 0.0)

    def test_set_and_get_parameters(self):
        """Test parameter related methods"""
        params = {'p': 1}
        self.strategy.set_parameters(params)
        self.assertEqual(self.strategy.parameters['p'], 1)

        info = self.strategy.get_parameter_info()
        self.assertEqual(info['name'], self.name)
        self.assertEqual(info['description'], self.description)
        self.assertEqual(info['parameters'], params)
        self.assertEqual(info['parameter_schema'], {})

    def test_set_parameters_invalid(self):
        """Test set_parameters with invalid input"""
        with patch.object(self.strategy, 'validate_parameters', return_value=False):
            with self.assertRaises(ValueError):
                self.strategy.set_parameters({'invalid': True})

    def test_preprocess_and_postprocess(self):
        """Test data processing methods"""
        df_factor = MagicMock()
        df_price = MagicMock()

        f, p = self.strategy.preprocess_data(df_factor, df_price)
        self.assertEqual(f, df_factor)
        self.assertEqual(p, df_price)

        result = MagicMock(spec=self.StrategyResult)
        processed_result = self.strategy.postprocess_result(result)
        self.assertEqual(processed_result, result)

    def test_string_representation(self):
        """Test __str__ and __repr__"""
        self.assertEqual(str(self.strategy), f"Strategy({self.name})")
        self.assertEqual(repr(self.strategy), f"Strategy({self.name}, params={{}})")

        self.strategy.set_parameters({'p': 1})
        self.assertEqual(repr(self.strategy), f"Strategy({self.name}, params={{'p': 1}})")

if __name__ == '__main__':
    unittest.main()
