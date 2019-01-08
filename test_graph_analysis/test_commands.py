import unittest

from graph_analysis.commands import create_md_model

from . import DATA_DIRECTORY, OUTPUT_DIRECTORY, PATTERNS


class TestCommands(unittest.TestCase):

    def setUp(self):
        pass

    def test_create_md_model(self):
        wkbk_path = [DATA_DIRECTORY / 'Composition Example 2.xlsx',
                     DATA_DIRECTORY]
        create_md_model(wkbk_path)
        self.assertTrue(False)
        pass

    def tearDown(self):
        pass
