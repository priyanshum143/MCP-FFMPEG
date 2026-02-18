"""
This file contains the models related to the tools
"""

from typing import Dict, Type

from src.MCP_ffmpeg.jobs.models import JobAction

JOB_ACTION_PARAMS: Dict[JobAction, Dict[str, Type]] = {
    JobAction.TRIM: {
        "input_file": str,
        "start_time": float,
        "duration": float,
    },
}
