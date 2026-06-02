import sys
from pathlib import Path

# Ensure the package in src/ is importable when running tests from the repository root
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
