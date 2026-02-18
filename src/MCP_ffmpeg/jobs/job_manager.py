"""
This file will contain the code to manage the jobs submitted by user
"""

import hashlib
import json
import asyncio
from typing import Any
from enum import Enum
from pathlib import Path
from dataclasses import asdict

from src.MCP_ffmpeg.jobs.models import JobAction, JobDetails
from src.MCP_ffmpeg.utils.variables import CommonVariables
from src.MCP_ffmpeg.utils.loggers import get_logger

logger = get_logger(__name__)


def _freeze(value: Any) -> Any:
    """
    This method converts the arbitrary Python objects into a JSON-serializable, deterministic structure.
    This makes hashing stable even for nested lists/dicts/Paths/enums/etc.

    :param value: Any value given
    :return: serialized value
    """

    if isinstance(value, Enum):
        return {"__enum__": f"{value.__class__.__name__}.{value.name}", "value": value.value}

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    if isinstance(value, Path):
        # normalize path to a consistent string representation
        return {"__path__": str(value)}

    if isinstance(value, (list, tuple, set)):
        # sets are unordered -> sort frozen values deterministically
        frozen_items = [_freeze(v) for v in value]
        if isinstance(value, set):
            return {"__set__": sorted(frozen_items, key=lambda x: json.dumps(x, sort_keys=True, separators=(",", ":")))}
        return frozen_items  # list/tuple keep order

    if isinstance(value, dict):
        # dict order shouldn't matter -> sort keys
        return {str(k): _freeze(v) for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))}

    # fallback: stable-ish representation
    # If you pass custom objects, prefer passing primitive fields instead.
    return {"__repr__": repr(value)}


async def generate_job_id(action: JobAction, input_file_path: str, *args) -> str:
    """
    This method will generate a job id based on action, input file path and the other arguments

    :param action: action needs to be performed
    :param input_file_path: input file path
    :param args: other arguments
    :return: job id
    """

    # Creating a payload to generate a job_id
    payload = {
        "action": action.value,
        "input": str(Path(input_file_path)),
        "args": _freeze(args),
    }
    logger.debug(f"Payload to generate a job id: {payload}")

    # canonical string to generate a job_id
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    logger.debug(f"Canonical string to generate a job id: {canonical}")

    job_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    logger.debug(f"Generated job id: {job_id}")
    return job_id


async def check_if_job_is_present(job_id: str) -> bool:
    """
    This method will check if the given job id is already present or not

    :param job_id: job id
    :return: True if job id is present, False otherwise
    """

    job_dir = CommonVariables.OUTPUT_DIR / job_id
    return await asyncio.to_thread(job_dir.exists)


async def create_job(job_id: str, action: JobAction, params: dict) -> None:
    """
    This method will create a job for the given task

    :param job_id: job id
    :param action: action to perform
    :param params: params for the action
    :return: None
    """

    # Creating a folder for this particular job
    job_dir = CommonVariables.OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    # Making job details model
    job = JobDetails(
        job_id=job_id,
        action=action,
        params=params,
    )

    job_dict = asdict(job)

    # Convert Enums + datetime to serializable format
    job_dict["action"] = job.action.value
    job_dict["status"] = job.status.value
    job_dict["created_at"] = job.created_at.isoformat()
    job_dict["updated_at"] = job.updated_at.isoformat()
    logger.debug(f"Creating a job details model for job id [{job_id}] with this data: {job_dict}")

    # Creating a JSON file to write details and writing the data
    job_file = job_dir / "job_details.json"
    with open(job_file, "w", encoding="utf-8") as f:
        json.dump(job_dict, f, indent=4)
    logger.debug(f"Successfully added the data for job_id: {job_id}")
