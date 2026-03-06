"""
This file contains the models related to the tools
"""

from typing import Dict, Type

from MCP_ffmpeg.jobs.models import JobAction
from MCP_ffmpeg.actions.tools import (
    trim_a_video,
    change_video_format,
    change_video_resolution,
    change_subtitle_format,
)


# Mapping of jobs and the params they require
JOB_ACTION_PARAMS: Dict[JobAction, Dict[str, Type]] = {
    JobAction.TRIM: {
        "input_file": str,
        "start_time": float,
        "duration": float,
    },
    JobAction.CHANGE_FORMAT: {
        "input_file": str,
        "output_format": str,
    },
    JobAction.CHANGE_RESOLUTION: {
        "input_file": str,
        "height": int,
        "width": int,
    },
    JobAction.CHANGE_SUBTITLE_FORMAT: {
        "input_file": str,
        "target_format": str,
    },
}


#  Mapping of jobs and the method they require to call
JOB_ACTION_MAPPING = {
    JobAction.TRIM: trim_a_video,
    JobAction.CHANGE_FORMAT: change_video_format,
    JobAction.CHANGE_RESOLUTION: change_video_resolution,
    JobAction.CHANGE_SUBTITLE_FORMAT: change_subtitle_format,
}
