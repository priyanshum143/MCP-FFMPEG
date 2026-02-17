"""
This file contains some common variables being used across the project
"""

from pathlib import Path


class CommonVariables:
    ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
    OUTPUT_DIR = ROOT_DIR / "outputs"