import tempfile
import unittest
from pathlib import Path
from shutil import copy2

from graph_analysis.commands import compare_md_model, create_md_model

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
            composition_changed = 'Composition Example 2 Model Changed 2.xlsx'
            excel_files = [
                (DATA_DIRECTORY / 'Composition Example 2 Model Baseline.xlsx'),
                (DATA_DIRECTORY / composition_changed),
                (DATA_DIRECTORY / 'Composition Example 2 Model Changed.xlsx'),
                (DATA_DIRECTORY / 'Composition Example 2.xlsx'),
                (DATA_DIRECTORY / 'Composition Example With Props.xlsx'),
                (DATA_DIRECTORY / 'Invalid Pattern.xlsx'),
                (DATA_DIRECTORY / 'Sample Equations.xlsx')]
            for xl_file in excel_files:
                copy2(DATA_DIRECTORY / xl_file, tmpdir)

            wkbk_path = [
                ROOT / 'graph_analysis' / 'patterns' / 'Composition.json',
                DATA_DIRECTORY / 'Composition Example 2.xlsx',
                tmpdir,
            ]
            create_md_model(wkbk_path)
            # expect 4
            cr_json = list(tmpdir.glob('*.json'))
            self.assertEqual(4, len(cr_json))
            self.assertTrue(
                (DATA_DIRECTORY / 'Composition Example 2.json').is_file())

            with tempfile.TemporaryDirectory() as out_tmp_dir:
                out_tmp_dir = Path(out_tmp_dir)
                create_md_model(wkbk_path, out_tmp_dir)
                new_json = list(out_tmp_dir.glob('*.json'))
                self.assertEqual(4, len(new_json))

    def test_compare_md_model(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            excel_files = [
                DATA_DIRECTORY / 'Composition Example 2 Model Baseline.xlsx',
                DATA_DIRECTORY / 'Composition Example 2 Model Changed.xlsx',
                DATA_DIRECTORY / 'Composition Example 2 Model Changed 2.xlsx',
                DATA_DIRECTORY / 'Composition Example Model Baseline.xlsx',
                DATA_DIRECTORY / 'Composition Example Model Changed.xlsx',
            ]
            for xl in excel_files:
                copy2(DATA_DIRECTORY / xl, tmpdir)

            original = tmpdir / 'Composition Example 2 Model Baseline.xlsx'
            updated = [tmpdir / 'Composition Example 2 Model Changed.xlsx',
                       tmpdir / 'Composition Example 2 Model Changed 2.xlsx'
                       ]
            orig = tmpdir / 'Composition Example Model Baseline.xlsx'
            update = tmpdir / 'Composition Example Model Changed.xlsx'

            inputs = [original]
            inputs.extend(updated)
            try:
                compare_md_model(inputs, output_path=inputs[0])
            except RuntimeError:
                self.assertTrue(True)
            compare_md_model(inputs)
            ins = [orig, update]
            compare_md_model(ins)
            # expect 3 json and 3 more excel files
            cr_json = list(tmpdir.glob('*.json'))
            self.assertEqual(3, len(cr_json))
            # check for created excel files by name
            diff_files = list(tmpdir.glob('Model Diffs*.xlsx'))
            self.assertEqual(3, len(diff_files))

            with tempfile.TemporaryDirectory() as tmpdir2:
                outdir = Path(tmpdir2)
                compare_md_model(inputs, outdir)
                compare_md_model(ins, outdir)
                # expect 3 json and 3 more excel files
                cr_json = list(outdir.glob('*.json'))
                self.assertEqual(3, len(cr_json))
                diff_files = list(tmpdir.glob('Model Diffs*.xlsx'))
                self.assertEqual(3, len(diff_files))

    def test_compare_md_model_dir(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tempdir = Path(tempdir)
            excel_files = [
                DATA_DIRECTORY / 'Composition Example 2 Model Baseline.xlsx',
                DATA_DIRECTORY / 'Composition Example 2 Model Changed.xlsx',
                DATA_DIRECTORY / 'Composition Example 2 Model Changed 2.xlsx',
            ]
            for xl in excel_files:
                copy2(DATA_DIRECTORY / xl, tempdir)

            original = tempdir / 'Composition Example 2 Model Baseline.xlsx'

            compare_md_model([original, tempdir])
            dir_json = list(tempdir.glob('*.json'))
            dir_xl = list(tempdir.glob('Model Diff*.xlsx'))
            self.assertEqual(2, len(dir_json))
            self.assertEqual(2, len(dir_xl))

            # with tempfile.TemporaryDirectory() as tmpdir3:
            #     outdir = Path(tmpdir3)
            #     copy2(DATA_DIRECTORY /
            #           'Composition Example 2 Model Baseline.xlsx', outdir)
            #     copy2(DATA_DIRECTORY /
            #           'Composition Example 2 Model Changed.xlsx', outdir)
            #     copy2(DATA_DIRECTORY /
            #           'Composition Example 2 Model Changed 2.xlsx', outdir)
            #     orig3 = outdir / 'Composition Example 2 Model Baseline.xlsx'
            #     input3 = [orig3, outdir]
            #     compare_md_model(input3, output_path=outdir)
            #     new_json = list(outdir.glob('*.json'))
            #     new_xl = list(outdir.glob('Model Diffs*.xlsx'))
            #     self.assertEqual(3, len(new_json))
            #     self.assertEqual(3, len(new_xl))

    def tearDown(self):
        pass
