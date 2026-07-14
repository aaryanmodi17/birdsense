"""Test configuration: make the repo root importable so `import src...` works.

The pipeline/acceptance tests run against the real eBird data in data/raw
(the synthetic generator and its ground-truth tests were removed once the real
data was in place)."""

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
