import unittest
import json
import pandas as pd
from utils import (get_edge_type, get_composite_owner_names,
                   get_a_composite_owner_names)


class TestUtils(unittest.TestCase):

    def setUp(self):
        with open('../data/PathMasterExpanded.json') as f:
            self.data = json.load(f)

    def test_edge_type(self):
        self.assertEqual('type',
                         get_edge_type(data=self.data, index=0))

    def test_get_composite_owner_names(self):
        composite_data = pd.Series({'Car': 1, 'Wheel': 1, 'Engine': 1})
        composite_owner_output = get_composite_owner_names(
            prefix='composite owner', data=composite_data)
        composite_data_list = ['composite owner Car',
                               'composite owner Wheel',
                               'composite owner Engine']
        self.assertListEqual(composite_data_list, composite_owner_output)

    def test_get_a_composite_owner_name(self):
        composite_data = pd.Series({'Car': 1, 'Wheel': 1, 'Engine': 1})
        composite_owner_output = get_a_composite_owner_names(
            prefix='A_thing_component', data=composite_data)
        composite_data_list = ['A_Car_component',
                               'A_Wheel_component',
                               'A_Engine_component']
        self.assertListEqual(composite_data_list, composite_owner_output)


if __name__ == '__main__':
    unittest.main()
