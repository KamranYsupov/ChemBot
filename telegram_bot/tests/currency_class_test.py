import unittest

from programming_elements.classes import CurrencyUnit
from programming_elements.enums import OperationsType


class MyTestCase(unittest.TestCase):
    def test_mapconverter_to_class_CurrencyUnit(self):
        data = {"USD": [{"operation": "BUY", "from": "0.00", "to": "1000.00", "course": "92.17"}, {"operation": "BUY", "from": "1000.00", "to": "10000.00", "course": "92.17"}, {"operation": "BUY", "from": "10000.00", "to": "20000.00", "course": "92.27"}, {"operation": "BUY", "from": "20000.00", "to": "9999999.00", "course": "92.27"}, {"operation": "SELL", "from": "0.00", "to": "1000.00", "course": "95.97"}, {"operation": "SELL", "from": "1000.00", "to": "10000.00", "course": "95.97"}, {"operation": "SELL", "from": "10000.00", "to": "20000.00", "course": "95.87"}, {"operation": "SELL", "from": "20000.00", "to": "9999999.00", "course": "95.87"}], "EUR": [{"operation": "BUY", "from": "0.00", "to": "1000.00", "course": "98.69"}, {"operation": "BUY", "from": "1000.00", "to": "10000.00", "course": "98.69"}, {"operation": "BUY", "from": "10000.00", "to": "20000.00", "course": "98.69"}, {"operation": "BUY", "from": "20000.00", "to": "9999999.00", "course": "98.69"}, {"operation": "SELL", "from": "0.00", "to": "1000.00", "course": "104.69"}, {"operation": "SELL", "from": "1000.00", "to": "10000.00", "course": "104.69"}, {"operation": "SELL", "from": "10000.00", "to": "20000.00", "course": "104.59"}, {"operation": "SELL", "from": "20000.00", "to": "9999999.00", "course": "104.59"}], "CNY": [{"operation": "BUY", "from": "0.00", "to": "9999999.00", "course": "12.48"}, {"operation": "SELL", "from": "0.00", "to": "9999999.00", "course": "13.68"}]}
        data_set = [[key for key in data.keys()], [values for values in data.values()]]
        complete_data = list(map(CurrencyUnit, *data_set))
        self.assertIsInstance(complete_data, list)  # add assertion here

    def test_sort_operations_to_class_CurrenyUnit(self):
        data = {"USD": [{"operation": "BUY", "from": "0.00", "to": "1000.00", "course": "92.17"},
                        {"operation": "BUY", "from": "1000.00", "to": "10000.00", "course": "92.17"},
                        {"operation": "BUY", "from": "10000.00", "to": "20000.00", "course": "92.27"},
                        {"operation": "BUY", "from": "20000.00", "to": "9999999.00", "course": "92.27"},
                        {"operation": "SELL", "from": "0.00", "to": "1000.00", "course": "95.97"},
                        {"operation": "SELL", "from": "1000.00", "to": "10000.00", "course": "95.97"},
                        {"operation": "SELL", "from": "10000.00", "to": "20000.00", "course": "95.87"},
                        {"operation": "SELL", "from": "20000.00", "to": "9999999.00", "course": "95.87"}],
                "EUR": [{"operation": "BUY", "from": "0.00", "to": "1000.00", "course": "98.69"},
                        {"operation": "BUY", "from": "1000.00", "to": "10000.00", "course": "98.69"},
                        {"operation": "BUY", "from": "10000.00", "to": "20000.00", "course": "98.69"},
                        {"operation": "BUY", "from": "20000.00", "to": "9999999.00", "course": "98.69"},
                        {"operation": "SELL", "from": "0.00", "to": "1000.00", "course": "104.69"},
                        {"operation": "SELL", "from": "1000.00", "to": "10000.00", "course": "104.69"},
                        {"operation": "SELL", "from": "10000.00", "to": "20000.00", "course": "104.59"},
                        {"operation": "SELL", "from": "20000.00", "to": "9999999.00", "course": "104.59"}],
                "CNY": [{"operation": "BUY", "from": "0.00", "to": "9999999.00", "course": "12.48"},
                        {"operation": "SELL", "from": "0.00", "to": "9999999.00", "course": "13.68"}]}
        data_set = [[key for key in data.keys()], [values for values in data.values()]]
        complete_data = list(map(CurrencyUnit, *data_set))
        self.assertIsInstance(complete_data, list)

    def test_sort_operations_to_class_CurrencyUnit_from_zero_to_10k(self):
        data = {"USD": [{"operation": "BUY", "from": "0.00", "to": "1000.00", "course": "92.17"},
                        {"operation": "BUY", "from": "1000.00", "to": "10000.00", "course": "92.17"},
                        {"operation": "BUY", "from": "10000.00", "to": "20000.00", "course": "92.27"},
                        {"operation": "BUY", "from": "20000.00", "to": "9999999.00", "course": "92.27"},
                        {"operation": "SELL", "from": "0.00", "to": "1000.00", "course": "95.97"},
                        {"operation": "SELL", "from": "1000.00", "to": "10000.00", "course": "95.97"},
                        {"operation": "SELL", "from": "10000.00", "to": "20000.00", "course": "95.87"},
                        {"operation": "SELL", "from": "20000.00", "to": "9999999.00", "course": "95.87"}],
                "EUR": [{"operation": "BUY", "from": "0.00", "to": "1000.00", "course": "98.69"},
                        {"operation": "BUY", "from": "1000.00", "to": "10000.00", "course": "98.69"},
                        {"operation": "BUY", "from": "10000.00", "to": "20000.00", "course": "98.69"},
                        {"operation": "BUY", "from": "20000.00", "to": "9999999.00", "course": "98.69"},
                        {"operation": "SELL", "from": "0.00", "to": "1000.00", "course": "104.69"},
                        {"operation": "SELL", "from": "1000.00", "to": "10000.00", "course": "104.69"},
                        {"operation": "SELL", "from": "10000.00", "to": "20000.00", "course": "104.59"},
                        {"operation": "SELL", "from": "20000.00", "to": "9999999.00", "course": "104.59"}],
                "CNY": [{"operation": "BUY", "from": "0.00", "to": "9999999.00", "course": "12.48"},
                        {"operation": "SELL", "from": "0.00", "to": "9999999.00", "course": "13.68"}]}
        data_set = [[key for key in data.keys()], [values for values in data.values()]]
        complete_data = list(map(CurrencyUnit, *data_set))
        operator_list = await complete_data[1].find_to_all_operations(10000)
        self.assertEqual(operator_list[0].operation, OperationsType.buy)
        self.assertEqual(int(float(operator_list[0].from_)), 1000)
        self.assertEqual(int(float(operator_list[0].to)), 10000)
        self.assertEqual(operator_list[1].operation, OperationsType.sell)
        self.assertEqual(int(float(operator_list[1].from_)), 1000)
        self.assertEqual(int(float(operator_list[1].to)), 10000)

    def test_sort_operations_to_class_CurrencyUnit_from_10k_to_inf(self):
        data = {"USD": [{"operation": "BUY", "from": "0.00", "to": "1000.00", "course": "92.17"},
                        {"operation": "BUY", "from": "1000.00", "to": "10000.00", "course": "92.17"},
                        {"operation": "BUY", "from": "10000.00", "to": "20000.00", "course": "92.27"},
                        {"operation": "BUY", "from": "20000.00", "to": "9999999.00", "course": "92.27"},
                        {"operation": "SELL", "from": "0.00", "to": "1000.00", "course": "95.97"},
                        {"operation": "SELL", "from": "1000.00", "to": "10000.00", "course": "95.97"},
                        {"operation": "SELL", "from": "10000.00", "to": "20000.00", "course": "95.87"},
                        {"operation": "SELL", "from": "20000.00", "to": "9999999.00", "course": "95.87"}],
                "EUR": [{"operation": "BUY", "from": "0.00", "to": "1000.00", "course": "98.69"},
                        {"operation": "BUY", "from": "1000.00", "to": "10000.00", "course": "98.69"},
                        {"operation": "BUY", "from": "10000.00", "to": "20000.00", "course": "98.69"},
                        {"operation": "BUY", "from": "20000.00", "to": "9999999.00", "course": "98.69"},
                        {"operation": "SELL", "from": "0.00", "to": "1000.00", "course": "104.69"},
                        {"operation": "SELL", "from": "1000.00", "to": "10000.00", "course": "104.69"},
                        {"operation": "SELL", "from": "10000.00", "to": "20000.00", "course": "104.59"},
                        {"operation": "SELL", "from": "20000.00", "to": "9999999.00", "course": "104.59"}],
                "CNY": [{"operation": "BUY", "from": "0.00", "to": "9999999.00", "course": "12.48"},
                        {"operation": "SELL", "from": "0.00", "to": "9999999.00", "course": "13.68"}]}
        data_set = [[key for key in data.keys()], [values for values in data.values()]]
        complete_data = list(map(CurrencyUnit, *data_set))
        operator_list = await complete_data[1].find_to_all_operations(9999999)
        self.assertEqual(operator_list[0].operation, OperationsType.buy)
        self.assertEqual(int(float(operator_list[0].from_)), 20000)
        self.assertEqual(int(float(operator_list[0].to)), 9999999)
        self.assertEqual(operator_list[1].operation, OperationsType.sell)
        self.assertEqual(int(float(operator_list[1].from_)), 20000)
        self.assertEqual(int(float(operator_list[1].to)), 9999999)



if __name__ == '__main__':
    unittest.main()
