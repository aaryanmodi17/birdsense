"""Test configuration: make the repo root importable so `import src...` works,
and provide shared fixtures (regenerate synthetic data + load its manifest)."""

import json
import os
import subprocess
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

RAW_DIR = os.path.join(REPO_ROOT, "data", "raw")
GENERATOR = os.path.join(REPO_ROOT, "scripts", "make_synthetic_data.py")
MANIFEST = os.path.join(RAW_DIR, "synthetic_manifest.json")


@pytest.fixture(scope="session")
def synthetic_manifest():
    """Regenerate the synthetic data (fixed seed) and return its planted-record
    manifest — the ground truth the validation drop-counts are checked against."""
    subprocess.run([sys.executable, GENERATOR], check=True, capture_output=True)
    with open(MANIFEST) as fh:
        return json.load(fh)


@pytest.fixture(scope="session")
def stage1(synthetic_manifest):
    """Run Stage 1 cleaning on the freshly generated synthetic data."""
    from src import load_and_clean
    return load_and_clean.run_stage1(RAW_DIR)
