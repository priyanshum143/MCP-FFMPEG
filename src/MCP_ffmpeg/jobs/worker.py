"""
This file contains the code to pick a task from jobs queue and execute it
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Type

from src.MCP_ffmpeg.actions.models import JOB_ACTION_MAPPING, JOB_ACTION_PARAMS
from src.MCP_ffmpeg.jobs.models import JobStatus, JobAction
from src.MCP_ffmpeg.utils.loggers import get_logger
from src.MCP_ffmpeg.utils.variables import CommonVariables

logger = get_logger(__name__)


class Worker:
    """
    This class contains the code to get a job from queue and execute the task
    """

    def __init__(self):
        self.parallel_execution_allowed = CommonVariables.PARALLEL_EXECUTIONS_ALLOWED
        self.execution_in_progress = 0

    async def get_task_from_queue_and_execute(self, job_queue: asyncio.Queue) -> None:
        """
        This method will dequeue the task from jobs queue and execute the task

        :param job_queue: queue with job ids
        :return: True if launched a task, False otherwise
        """

        if job_queue.empty():
            logger.debug("Jobs queue is empty, No task to launch")
            return

        if self.execution_in_progress == self.parallel_execution_allowed:
            logger.debug(
                f"Can not dequeue any task from queue, "
                f"as number of parallel executions running is [{self.execution_in_progress}], "
                f"Adding more executions will exceed the limit: [{self.parallel_execution_allowed}]"
            )
            return

        job_id = await job_queue.get()
        logger.debug(f"Got the job id [{job_id}] from queue")
        self.execution_in_progress += 1

        try:
            logger.info(f"Executing the job using job id: {job_id}")
            await self._execute_job(job_id)
        finally:
            self.execution_in_progress -= 1
            job_queue.task_done()

    async def _execute_job(self, job_id: str) -> None:
        """
        This method will execute the job using given job id

        :param job_id: job id to execute
        :return: None
        """

        job_dir = CommonVariables.OUTPUT_DIR / job_id
        job_details_path = (
                job_dir / CommonVariables.JOB_DETAILS_JSON_FILE_NAME
        )

        if not job_details_path.exists():
            logger.debug(f"Could not find the path: {job_details_path}")
            return

        # Load job details
        logger.debug(f"Loading the json file: {job_details_path}")
        with open(job_details_path, "r") as f:
            job_data = json.load(f)

        # Reconstruct enums
        action = JobAction(job_data["action"])
        params = job_data["params"]
        logger.debug(f"Got the action to execute from file {job_details_path}: [{action}] with params: {params}")

        # Update status to RUNNING
        job_data["status"] = JobStatus.RUNNING.value
        job_data["updated_at"] = datetime.utcnow().isoformat()
        logger.debug(f"Updated the job status of job id {job_id} to [{job_data['status']}]")

        # Updating the job json file
        logger.debug(f"Updating the json file: {job_details_path} with data: [{job_data}]")
        with open(job_details_path, "w") as f:
            json.dump(job_data, f, indent=4)

        try:
            action_to_execute = JOB_ACTION_MAPPING[action]
            logger.debug(f"Calling the method [{action_to_execute}] with params: {params}")
            await action_to_execute(job_id=job_id, **params)

            # Update status to SUCCESS
            job_data["status"] = JobStatus.SUCCESS.value
            logger.debug(f"Updated the job status with [{job_data['status']}]")

        except Exception as e:
            job_data["status"] = JobStatus.FAILED.value
            job_data["error"] = str(e)
            logger.debug(f"While running the job {job_id}, got the error: {str(e)}")
            logger.debug(f"Updating the job status for job {job_id} as {job_data['status']} ")

        finally:
            job_data["updated_at"] = datetime.utcnow().isoformat()

            with open(job_details_path, "w") as f:
                json.dump(job_data, f, indent=4)
