"""Machine-readable report generation."""
from __future__ import annotations
import json
from pathlib import Path

def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
