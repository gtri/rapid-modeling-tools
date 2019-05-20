"""
Copyright (C) 2018 by the Georgia Tech Research Institute (GTRI)
This software may be modified and distributed under the terms of
the BSD 3-Clause license. See the LICENSE file for details.
"""


from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent

DATA_DIRECTORY = HERE / "data_test"
PATTERNS = ROOT / "graph_analysis" / "patterns"
OUTPUT_DIRECTORY = ROOT / "data"


__version__ = "0.1.0"
