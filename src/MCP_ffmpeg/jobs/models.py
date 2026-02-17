"""
This file will contain the models required for job manager
"""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Dict

class JobAction(Enum):
    TRIM = "trim"


class JobStatus(Enum):
    QUEUED = "queued"
    RUNNING =  "running"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class JobDetails:
    job_id: str
    action: JobAction
    params: Dict
    status: JobStatus
    created_at: datetime
    updated_at: datetime
