"""
This file will contain the code to manage the jobs submitted by user
"""

import hashlib
import json
import asyncio
from dataclasses import asdict

from src.MCP_ffmpeg.jobs.models import JobAction, JobDetails, JobStatus
from src.MCP_ffmpeg.utils.variables import CommonVariables
from src.MCP_ffmpeg.utils.loggers import get_logger
from src.MCP_ffmpeg.utils.serialization import freeze
from src.MCP_ffmpeg.actions.models import JOB_ACTION_PARAMS

logger = get_logger(__name__)


class JobManager:
    """
    This class contains the code to handle and manage jobs+
    """

    def __init__(self):
        self.job_queue: asyncio.Queue[str] = asyncio.Queue()

    async def generate_job_id(self, action: JobAction, *args) -> str:
        """
        This method will generate a job id based on action, input file path and the other arguments

        :param action: action needs to be performed
        :param args: other arguments
        :return: job id
        """

        # Creating a payload to generate a job_id
        payload = {
            "action": action.value,
            "args": freeze(args),
        }
        logger.debug(f"Payload to generate a job id: {payload}")

        # canonical string to generate a job_id
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        logger.debug(f"Canonical string to generate a job id: {canonical}")

        job_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        logger.debug(f"Generated job id: {job_id}")
        return job_id


    async def check_if_job_is_present(self, job_id: str) -> bool:
        """
        This method will check if the given job id is already present or not

        :param job_id: job id
        :return: True if job id is present, False otherwise
        """

        job_dir = CommonVariables.OUTPUT_DIR / job_id
        return await asyncio.to_thread(job_dir.exists)


    async def create_job(self, job_id: str, action: JobAction, params: dict) -> None:
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
        logger.debug(f"Creating a job details model for job id [{job_id}] with data: {job_dict}")

        # Creating a JSON file to write details and writing the data
        job_file = job_dir / "job_details.json"
        with open(job_file, "w", encoding="utf-8") as f:
            json.dump(job_dict, f, indent=4)
        logger.debug(f"Successfully added the data for job_id: {job_id}")


    async def handle_job(self, action: JobAction, params: dict) -> JobStatus:
        """
        This is the main method to handle a job based of action and the params

        :param action: action to perform
        :param params: params
        :return: job status
        """

        # Creating a job id
        schema = JOB_ACTION_PARAMS[action]
        args_in_order = [params[key] for key in schema.keys()]

        logger.debug(f"Creating a job id for action [{action.value}] with params: {args_in_order}")
        job_id = await self.generate_job_id(
            action,
            *args_in_order
        )
        logger.debug(f"Job id generated successfully: {job_id}")

        # Checking if job already exists
        logger.debug(f"Checking if job id [{job_id}] already exists")
        does_job_exist = await self.check_if_job_is_present(job_id)
        if does_job_exist:
            logger.debug(f"Job id [{job_id}] already exists")
            # TODO need to return proper status from the job details file
            return JobStatus.SUCCESS

        # Creating a new job
        logger.debug(f"Job id [{job_id}] does not exists, creating a new job")
        await self.create_job(
            job_id=job_id,
            action=action,
            params=params,
        )

        # Adding the job in the queue
        logger.debug(f"Adding job id [{job_id}] in queue.")
        await self.job_queue.put(job_id)
        return JobStatus.QUEUED
