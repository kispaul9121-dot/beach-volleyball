#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
result = subprocess.run(
    [sys.executable, "scripts/validate_profile_activity.py"],
    cwd=ROOT,
    capture_output=True,
    text=True,
    check=False,
)
content = (
    f"exit_code: {result.returncode}\n\n"
    "stdout:\n"
    f"{result.stdout}\n"
    "stderr:\n"
    f"{result.stderr}\n"
)
(ROOT / "docs/PROFILE_VALIDATION_DIAGNOSTIC.txt").write_text(content, encoding="utf-8")
print(content)
