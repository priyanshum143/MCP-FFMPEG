"""
This file contains the code related to MCP server
"""

import asyncio
import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict
from collections.abc import AsyncIterator

from mcp.server.fastmcp import FastMCP

from MCP_ffmpeg.jobs.job_manager import JobManager
from MCP_ffmpeg.jobs.worker import Worker
from MCP_ffmpeg.jobs.models import JobAction
from MCP_ffmpeg.utils.loggers import get_logger
from MCP_ffmpeg.utils.variables import CommonVariables

logger = get_logger(__name__)

job_manager = JobManager()
worker = Worker()


async def _run_worker_forever(worker_id: int) -> None:
    """
    One worker loop: repeatedly take a job from the queue (when available) and execute it.
    Multiple workers share the same queue; each job is taken by exactly one worker.
    """

    while True:
        await worker.get_task_from_queue_and_execute(
            job_manager.job_queue, worker_id=worker_id
        )
        await asyncio.sleep(CommonVariables.WORKER_RE_RUN_TIME)


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[None]:
    """
    FastMCP lifespan hook: start N background workers without blocking initialization.
    """
    num_workers = CommonVariables.PARALLEL_EXECUTIONS_ALLOWED
    tasks = [asyncio.create_task(_run_worker_forever(worker_id=i)) for i in range(num_workers)]
    logger.debug("Started %s MCP worker(s)", num_workers)
    try:
        yield
    finally:
        for task in tasks:
            task.cancel()
        for task in tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass


# Create server WITH lifespan so the worker starts in background
mcp = FastMCP("mcp-ffmpeg", lifespan=app_lifespan)


def _job_details_path(job_id: str) -> Path:
    """
    This method returns the path of job_details.json file according to the job id

    :param job_id: job id
    :return: job_details.json file path
    """

    return CommonVariables.OUTPUT_DIR / job_id / CommonVariables.JOB_DETAILS_JSON_FILE_NAME


def _read_job_details(job_id: str) -> Dict[str, Any]:
    """
    This method reads the json file and returns the data as a dict
    :param job_id: job id
    :return: job details
    """

    path = _job_details_path(job_id)
    if not path.exists():
        raise FileNotFoundError(f"job_details.json not found for job_id={job_id}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@mcp.tool()
async def start_trim(
    input_file: str,
    start_time: float,
    duration: float,
    force_run: bool = False,
) -> Dict[str, Any]:
    """
    Enqueue a TRIM job. Returns immediately with job_id + status.

    input_file: path to input video file (must exist)
    start_time: seconds (float)
    duration: seconds (float)
    force_run: if we need to force run a job or not ignoring cache
    """
    params = {
        "input_file": input_file,
        "start_time": start_time,
        "duration": duration,
    }
    status, job_id = await job_manager.handle_job(JobAction.TRIM, params, force_run)

    # Return stored status if cached; queued otherwise
    return {
        "job_id": job_id,
        "status": status.value if hasattr(status, "value") else str(status),
        "job_details_path": str(_job_details_path(job_id)),
    }


@mcp.tool()
async def start_change_format(
    input_file: str,
    output_format: str,
    force_run: bool = False,
) -> Dict[str, Any]:
    """
    Enqueue a CHANGE_FORMAT job. Converts video to another container (e.g. mp4, mkv, avi) without re-encoding.
    Returns immediately with job_id + status.

    input_file: path to input video file (must exist)
    output_format: desired output format (e.g., mp4, mkv, avi); dot is optional
    force_run: if True, run even when a cached result exists for the same inputs
    """
    params = {
        "input_file": input_file,
        "output_format": output_format,
    }
    status, job_id = await job_manager.handle_job(JobAction.CHANGE_FORMAT, params, force_run)

    return {
        "job_id": job_id,
        "status": status.value if hasattr(status, "value") else str(status),
        "job_details_path": str(_job_details_path(job_id)),
    }


@mcp.tool()
async def start_change_resolution(
    input_file: str,
    height: int,
    width: int,
    force_run: bool = False,
) -> Dict[str, Any]:
    """
    Enqueue a CHANGE_RESOLUTION job. Converts the video resolution according to the user's provided height and width.
    Returns immediately with job_id + status.

    input_file: path to input video file (must exist)
    height: desired height of the video
    width: desired width of the video
    force_run: if True, run even when a cached result exists for the same inputs
    """
    params = {
        "input_file": input_file,
        "height": height,
        "width": width,
    }
    status, job_id = await job_manager.handle_job(JobAction.CHANGE_RESOLUTION, params, force_run)

    return {
        "job_id": job_id,
        "status": status.value if hasattr(status, "value") else str(status),
        "job_details_path": str(_job_details_path(job_id)),
    }


@mcp.tool()
async def get_job_status(job_id: str) -> Dict[str, Any]:
    """
    Get the latest status for a job_id.
    """
    details = _read_job_details(job_id)
    return {
        "job_id": job_id,
        "status": details.get("status"),
        "updated_at": details.get("updated_at"),
        "error": details.get("error"),
    }


@mcp.tool()
async def get_job_result(job_id: str) -> Dict[str, Any]:
    """
    Retrieve the final output of a completed job.

    This tool should only be called after the job status is 'success'.
    If the job is still 'queued' or 'running', this will return the current status.
    If the job has 'failed', it will return the error details.
    """

    details = _read_job_details(job_id)
    status = details.get("status")

    result: Dict[str, Any] = {
        "job_id": job_id,
        "status": status,
        "job_details_path": str(_job_details_path(job_id)),
    }

    try:
        params = details.get("params", {})
        if "output_format" in params:
            fmt = params["output_format"].lstrip(".")
            output_path = CommonVariables.OUTPUT_DIR / job_id / f"output.{fmt}"
        else:
            input_file = params.get("input_file", "")
            suffix = Path(input_file).suffix
            output_path = CommonVariables.OUTPUT_DIR / job_id / f"output{suffix}"
        result["output_path"] = str(output_path)
    except Exception:
        pass

    return result


if __name__ == "__main__":
    """
    This is the main method to bring up our MCP server
    """

    mcp.run(transport="stdio")
