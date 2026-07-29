"""Platform-aware dataset base path.

On Linux:   /home/qy/dataset-202607/quality test/dataset/
On Windows: D:/dataset-202607/quality test/dataset/

Override on any platform via the ``DATASET_BASE`` environment variable::

    DATASET_BASE=/your/custom/path python grab_photos/grab_gui.py
"""

import os
import sys
from pathlib import Path

_ENV = os.environ.get("DATASET_BASE")
if _ENV:
    DATASET_BASE = Path(_ENV)
elif sys.platform == "win32":
    DATASET_BASE = Path("D:/dataset-202607/quality test/dataset")
else:
    DATASET_BASE = Path("/home/qy/dataset-202607/quality test/dataset")
