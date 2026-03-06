"""
This file will contain the models required for job manager
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict


class JobAction(Enum):
    TRIM = "trim"
    CHANGE_FORMAT = "change_format"
    CHANGE_RESOLUTION = "change_resolution"
    CHANGE_SUBTITLE_FORMAT = "change_subtitle_format"


class JobStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class JobDetails:
    job_id: str
    action: JobAction
    params: Dict
    error: str = None
    status: JobStatus = JobStatus.QUEUED
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
