"""
This file contains the code related to MCP server
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP

from MCP_ffmpeg.jobs.job_manager import JobManager
from MCP_ffmpeg.jobs.worker import Worker
from MCP_ffmpeg.jobs.models import JobAction
from MCP_ffmpeg.utils.loggers import get_logger
from MCP_ffmpeg.utils.variables import CommonVariables

logger = get_logger(__name__)

mcp = FastMCP("mcp-ffmpeg")

job_manager = JobManager()
worker = Worker()


async def _run_worker_forever() -> None:
    """
    Background worker loop. Runs forever.
    """

    logger.info("Worker background loop started")
    while True:
        await worker.get_task_from_queue_and_execute(job_manager.job_queue)
        await asyncio.sleep(CommonVariables.WORKER_RE_RUN_TIME)


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
) -> Dict[str, Any]:
    """
    Enqueue a TRIM job. Returns immediately with job_id + status.

    input_file: path to input video file (must exist)
    start_time: seconds (float)
    duration: seconds (float)
    """
    params = {
        "input_file": input_file,
        "start_time": start_time,
        "duration": duration,
    }

    status, job_id = await job_manager.handle_job(JobAction.TRIM, params)

    # Return stored status if cached; queued otherwise
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
        input_file = details["params"]["input_file"]
        suffix = Path(input_file).suffix
        output_path = CommonVariables.OUTPUT_DIR / job_id / f"output{suffix}"
        result["output_path"] = str(output_path)
    except Exception:
        pass

    return result


async def main() -> None:
    """
    This is the main method to bring up our MCP server
    """

    # Start worker loop once
    await asyncio.create_task(_run_worker_forever())

    # Run MCP server over stdio
    mcp.run(transport="stdio")


if __name__ == "__main__":
    asyncio.run(main())
