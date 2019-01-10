import tempfile
import unittest
from pathlib import Path
from shutil import copy2

from graph_analysis.commands import create_md_model

from . import DATA_DIRECTORY, OUTPUT_DIRECTORY, PATTERNS, ROOT


class TestCommands(unittest.TestCase):

    def setUp(self):
        pass

    def test_create_md_model(self):
        # make temp dir with temp file
        # copy some excel files that I want to test on into it
        # test by reading excel files from the tmp file
        # for one of the tests, run the input path as the whole
        # tmpdir without an output path and then create second
        # tmpdir and supply that as the output path. Check for
        # expected files.
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            excel_files = list(DATA_DIRECTORY.glob('*.xlsx'))
            for xl_file in excel_files:
                copy2(DATA_DIRECTORY / xl_file, tmpdir)

            wkbk_path = [
                ROOT / 'graph_analysis' / 'patterns' / 'Composition.json',
                DATA_DIRECTORY / 'Composition Example 2.xlsx',
                tmpdir,
            ]
            create_md_model(wkbk_path)
            # expect 5
            cr_json = list(tmpdir.glob('*.json'))
            self.assertEqual(5, len(cr_json))
            self.assertTrue(
                (DATA_DIRECTORY / 'Composition Example 2.json').is_file())

            with tempfile.TemporaryDirectory() as out_tmp_dir:
                out_tmp_dir = Path(out_tmp_dir)
                create_md_model(wkbk_path, out_tmp_dir)
                new_json = list(out_tmp_dir.glob('*.json'))
                self.assertEqual(5, len(new_json))

    def tearDown(self):
        pass
