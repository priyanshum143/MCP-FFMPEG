"""
This is a main file to run our MCP server
"""

import asyncio

from src.MCP_ffmpeg.jobs.worker import Worker
from src.MCP_ffmpeg.jobs.job_manager import JobManager
from src.MCP_ffmpeg.jobs.models import JobAction
from src.MCP_ffmpeg.utils.loggers import get_logger
from src.MCP_ffmpeg.utils.cli_utils import prompt_params_for_action
from src.MCP_ffmpeg.utils.variables import CommonVariables

job_manager = JobManager()
worker = Worker()
logger = get_logger(__name__)


async def run_worker():
    """
    Ths method will start the worker to make it run in background forever
    """

    logger.debug("Worker started!!")
    while True:
        await worker.get_task_from_queue_and_execute(
            job_manager.job_queue
        )
        await asyncio.sleep(CommonVariables.WORKER_RE_RUN_TIME)

async def main():
    """
    This method is the main method that we will execute to run the server and use the tools
    """

    logger.info("MCP FFmpeg Server started!!")

    # start worker in background
    asyncio.create_task(run_worker())

    # Showing the available actions to the user
    print("\nAvailable Actions:")
    for idx, action in enumerate(JobAction, start=1):
        print(f"{idx}. {action.value}")

    # Asking user to choose an action
    choice = input("\nSelect an action by number: ")
    try:
        choice = int(choice)
        selected_action = list(JobAction)[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection")
        return
    print(f"You selected: {selected_action.value}")
    logger.debug(f"User chose action: {selected_action.value}")

    # Collecting params
    params = prompt_params_for_action(selected_action)
    print("\nCollected params:", params)
    logger.debug(f"Params added by user: {params}")

    # Creating and handling the job
    logger.debug(f"Calling the job handler for action [{selected_action}] with params: {params}")
    status = await job_manager.handle_job(selected_action, params)
    logger.debug(f"Job handled successfully with current status as {status}")
    print(f"Job status for the task -> {status.value}")

    # WAIT until worker processes all queued jobs
    await job_manager.job_queue.join()


if __name__ == "__main__":
    asyncio.run(main())
