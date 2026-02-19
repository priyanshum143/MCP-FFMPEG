"""
This file contains the models related to the tools
"""

from typing import Dict, Type

from src.MCP_ffmpeg.jobs.models import JobAction
from src.MCP_ffmpeg.actions.tools import trim_a_video

# Mapping of jobs and the params they require
JOB_ACTION_PARAMS: Dict[JobAction, Dict[str, Type]] = {
    JobAction.TRIM: {
        "input_file": str,
        "start_time": float,
        "duration": float,
    },
}


#  Mapping of jobs and the method they require to call
JOB_ACTION_MAPPING = {
    JobAction.TRIM: trim_a_video,
}
