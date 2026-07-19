from __future__ import annotations

import os
import runpy
import subprocess
from pathlib import Path

from setuptools import setup

root = Path(os.environ.get("GITHUB_WORKSPACE", Path(__file__).resolve().parents[2])).resolve()
runpy.run_path(str(root / "scripts" / "migrate_management_archive.py"), run_name="__main__")
subprocess.run(
    ["git", "add", "docs/ROUTES.yaml", "docs/ACTIONS.yaml", "docs/DECISIONS.md"],
    cwd=root,
    check=True,
)

setup(name="volleyplay-archive-migration", version="0.0.0")
