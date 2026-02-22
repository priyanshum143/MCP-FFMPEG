"""
This file contains some common variables being used across the project
"""

from pathlib import Path


class CommonVariables:
    ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
    OUTPUT_DIR = ROOT_DIR / "outputs"
    LOGS_DIR = ROOT_DIR / "logs"

    JOB_DETAILS_JSON_FILE_NAME = "job_details.json"

    PARALLEL_EXECUTIONS_ALLOWED = 1