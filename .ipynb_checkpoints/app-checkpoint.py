import runpy
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "app"))
runpy.run_path(str(PROJECT_ROOT / "app" / "main.py"))
