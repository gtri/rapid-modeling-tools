"""
Copyright (C) 2019 by the Georgia Tech Research Institute (GTRI)
This software may be modified and distributed under the terms of
the BSD 3-Clause license. See the LICENSE file for details.
"""


from pathlib import Path

import graph_analysis

HERE = Path(__file__).parent
ROOT = HERE.parent

DATA_DIRECTORY = HERE / "data_test"
PATTERNS = Path(graph_analysis.__file__).parent / "patterns"
OUTPUT_DIRECTORY = ROOT / "data"
