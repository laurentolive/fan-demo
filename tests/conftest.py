import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
# e2sim package: E2SIM_ROOT (exported by the Makefile), else the version fetched by tools/fetch.py
sys.path.insert(0, os.environ.get("E2SIM_ROOT") or str(ROOT / ".tools" / "e2Sim"))

pytest_plugins = ["e2sim.pytest_plugin"]


@pytest.fixture
def e2sim_board():
    return Path(__file__).parent.parent / "sim" / "hmi.board.yaml"
