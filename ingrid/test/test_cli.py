"""
Copyright (C) 2020 by the Georgia Tech Research Institute (GTRI)
This software may be modified and distributed under the terms of
the BSD 3-Clause license. See the LICENSE file for details.
"""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from shutil import copy2

from . import DATA_DIRECTORY, ROOT


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
            excel_files = [
                DATA_DIRECTORY / "Composition Example 2 Model Baseline.xlsx",
                DATA_DIRECTORY / "Composition Example 2 Model Changed 2.xlsx",
                DATA_DIRECTORY / "Composition Example 2 Model Changed.xlsx",
                DATA_DIRECTORY / "Composition Example 2.xlsx",
                DATA_DIRECTORY / "Composition Example With Props.xlsx",
                DATA_DIRECTORY / "Invalid Pattern.xlsx",
                DATA_DIRECTORY / "Sample Equations.xlsx",
            ]
            for xl_file in excel_files:
                copy2(xl_file, tmpdir)

            wkbk_path = [
                ROOT / "model_processing" / "patterns" / "Composition.json",
                # tmpdir / "Composition Example 2.xlsx",
                tmpdir,
            ]

            pattern_path = (
                ROOT
                / "src"
                / "model_processing"
                / "patterns"
                / "Composition.json"
            )
            pattern_command = (
                ["model-processing", "--create", "--input"]
                + [str(tmpdir / "Composition Example 2.xlsx")]
                + ["--pattern", str(pattern_path)]
            )
            subprocess.run(pattern_command)
            command = ["model-processing", "--create", "--input"] + [
                str(f) for f in wkbk_path
            ]
            subprocess.run(command)

            good_excel_files = [
                f
                for f in excel_files
                if f.name
                not in [
                    "Invalid Pattern.xlsx",
                    "Composition Example With Props.xlsx",
                ]
            ]
            expected_json_files = [
                tmpdir / f.name.replace(".xlsx", ".json")
                for f in good_excel_files
            ]

            # expect 5
            cr_json = list(tmpdir.glob("*.json"))
            self.assertEqual(len(good_excel_files), len(cr_json))
            for json_file in expected_json_files:
                self.assertTrue(json_file.is_file())

            with tempfile.TemporaryDirectory() as out_tmp_dir:
                out_tmp_dir = Path(out_tmp_dir)
                command = (
                    ["model-processing", "--create", "--input"]
                    + [str(f) for f in tmpdir.iterdir()]
                    + ["--output", str(out_tmp_dir)]
                )
                subprocess.run(command)
                new_json = list(out_tmp_dir.glob("*.json"))
                self.assertEqual(len(good_excel_files), len(new_json))

    def test_compare_md_model(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            excel_files = [
                DATA_DIRECTORY / "Composition Example 2 Model Baseline.xlsx",
                DATA_DIRECTORY / "Composition Example 2 Model Changed.xlsx",
                DATA_DIRECTORY / "Composition Example 2 Model Changed 2.xlsx",
                DATA_DIRECTORY / "Composition Example Model Baseline.xlsx",
                DATA_DIRECTORY / "Composition Example Model Changed.xlsx",
            ]
            for xl in excel_files:
                copy2(DATA_DIRECTORY / xl, tmpdir)

            original = tmpdir / "Composition Example 2 Model Baseline.xlsx"
            updated = [
                tmpdir / "Composition Example 2 Model Changed.xlsx",
                tmpdir / "Composition Example 2 Model Changed 2.xlsx",
            ]
            orig = tmpdir / "Composition Example Model Baseline.xlsx"
            update = tmpdir / "Composition Example Model Changed.xlsx"

            command = [
                "model-processing",
                "--compare",
                "--original",
                str(original),
                "--updated",
                *[str(u) for u in updated],
                "--output",
                str(tmpdir),
            ]
            subprocess.run(command, check=True)

            command = [
                "model-processing",
                "--compare",
                "--original",
                str(orig),
                "--updated",
                str(update),
                "--output",
                str(tmpdir),
            ]
            subprocess.run(command, check=True)

            # expect 3 json and 3 more excel files
            cr_json = list(tmpdir.glob("*.json"))
            self.assertEqual(3, len(cr_json))
            # check for created excel files by name
            diff_files = list(tmpdir.glob("Model Diffs*.xlsx"))
            self.assertEqual(3, len(diff_files))

            with tempfile.TemporaryDirectory() as tmpdir2:
                outdir = Path(tmpdir2)
                command = [
                    "model-processing",
                    "--compare",
                    "--original",
                    str(original),
                    "--updated",
                    *[str(u) for u in updated],
                    "--output",
                    str(outdir),
                ]
                subprocess.run(command, check=True)
                command = [
                    "model-processing",
                    "--compare",
                    "--original",
                    str(orig),
                    "--updated",
                    str(update),
                    "--output",
                    str(outdir),
                ]
                subprocess.run(command, check=True)
                # expect 3 json and 3 more excel files
                cr_json = list(outdir.glob("*.json"))
                self.assertEqual(3, len(cr_json))
                diff_files = list(tmpdir.glob("Model Diffs*.xlsx"))
                self.assertEqual(3, len(diff_files))

    def test_compare_md_model_dir(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tempdir = Path(tempdir)
            excel_files = [
                DATA_DIRECTORY / "Composition Example 2 Model Baseline.xlsx",
                DATA_DIRECTORY / "Composition Example 2 Model Changed.xlsx",
                DATA_DIRECTORY / "Composition Example 2 Model Changed 2.xlsx",
            ]
            for xl in excel_files:
                copy2(DATA_DIRECTORY / xl, tempdir)

            original = tempdir / "Composition Example 2 Model Baseline.xlsx"

            command = [
                "model-processing",
                "--compare",
                "--original",
                str(original),
                "--updated",
                str(tempdir),
            ]
            subprocess.run(command, check=True)
            dir_json = list(tempdir.glob("*.json"))
            dir_xl = list(tempdir.glob("Model Diff*.xlsx"))
            self.assertEqual(2, len(dir_json))
            self.assertEqual(2, len(dir_xl))

    def test_validate_create_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            excel_files = [(DATA_DIRECTORY / "Composition Example 2.xlsx")]
            for xl_file in excel_files:
                copy2(xl_file, tmpdir)

            wkbk_path = tmpdir / "Composition Example 2.xlsx"

            with tempfile.TemporaryDirectory() as out_tmp_dir:
                out_tmp_dir = Path(out_tmp_dir)
                command = [
                    "model-processing",
                    "--create",
                    "--input",
                    str(wkbk_path),
                    "--output",
                    str(out_tmp_dir),
                ]
                subprocess.run(command, check=True)
                new_json = list(out_tmp_dir.glob("*.json"))
                self.assertEqual(1, len(new_json))
                cr_data_path = out_tmp_dir / "Composition Example 2.json"
                cr_data = json.loads(cr_data_path.read_text())
                # TODO: This is a hardcoded validation to check the number
                # of objs created meets a known working count
                # it would be possible but difficult to compute internally
                assert 458 == len(cr_data["modification targets"])

    def test_validate_compare_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            excel_files = [
                DATA_DIRECTORY / "Composition Example 2 Model Baseline.xlsx",
                DATA_DIRECTORY / "Composition Example 2 Model Changed.xlsx",
            ]
            for xl in excel_files:
                copy2(DATA_DIRECTORY / xl, tmpdir)

            original = tmpdir / "Composition Example 2 Model Baseline.xlsx"
            updated = [tmpdir / "Composition Example 2 Model Changed.xlsx"]

            with tempfile.TemporaryDirectory() as tmpdir2:
                outdir = Path(tmpdir2)
                pattern_path = (
                    ROOT
                    / "src"
                    / "model_processing"
                    / "patterns"
                    / "Composition.json"
                )
                command = [
                    "model-processing",
                    "--compare",
                    "--original",
                    str(original),
                    "--updated",
                    str(updated[0]),
                    "--pattern",
                    str(pattern_path),
                    "--output",
                    str(outdir),
                ]
                subprocess.run(command, check=True)
                # expect 3 json and 3 more excel files
                cmp_json = list(outdir.glob("*.json"))
                compare_data = json.loads(cmp_json[0].read_text())
                # TODO: This is hardcoded validation as it checks at a known
                # point when the library works. This test passing does not
                # guarantee that it should always work.
                assert 28 == len(compare_data["modification targets"])

    def tearDown(self):
        pass
