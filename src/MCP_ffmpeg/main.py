"""
This is a main file to run our MCP server
"""

import asyncio

from MCP_ffmpeg.jobs.worker import Worker
from MCP_ffmpeg.jobs.job_manager import JobManager
from MCP_ffmpeg.jobs.models import JobAction
from MCP_ffmpeg.utils.loggers import get_logger
from MCP_ffmpeg.utils.cli_utils import prompt_params_for_action
from MCP_ffmpeg.utils.variables import CommonVariables

job_manager = JobManager()
worker = Worker()
logger = get_logger(__name__)


async def run_worker(worker_id: int):
    """
    One worker loop: repeatedly take a job from the queue (when available) and execute it.
    Multiple run_worker tasks share the same queue; each job is taken by exactly one worker.
    """

    while True:
        await worker.get_task_from_queue_and_execute(
            job_manager.job_queue, worker_id=worker_id
        )
        await asyncio.sleep(CommonVariables.WORKER_RE_RUN_TIME)


async def main():
    """
    This method is the main method that we will execute to run the server and use the tools
    """

    logger.info("MCP FFmpeg Server started!!")

    # start N workers in background (N = PARALLEL_EXECUTIONS_ALLOWED); each checks the queue and runs jobs
    num_workers = CommonVariables.PARALLEL_EXECUTIONS_ALLOWED
    for i in range(num_workers):
        asyncio.create_task(run_worker(worker_id=i))
    logger.debug("Started %s worker(s)", num_workers)

    while True:
        # Printing all the available actions
        print("\nAvailable Actions:")
        for idx, action in enumerate(JobAction, start=1):
            print(f"{idx}. {action.value}")
        print("0. Exit")

        # Asking user to choose an action
        choice = await asyncio.to_thread(
            input, "\nSelect an action by number: "
        )
        choice = choice.strip()

        # Stop the execution
        if choice == "0":
            print("Exiting MCP FFmpeg Server...")
            break

        # Mapping of user choice with actual action
        try:
            choice = int(choice)
            selected_action = list(JobAction)[choice - 1]
        except (ValueError, IndexError):
            print("Invalid selection")
            continue
        print(f"You selected: {selected_action.value}")
        logger.debug(f"User chose action: {selected_action.value}")

        # Taking required params for the action user chose
        params = await prompt_params_for_action(selected_action)

        # Handling the job according to action and params
        logger.debug(
            f"Calling job handler for action [{selected_action}] with params: {params}"
        )
        status, job_id = await job_manager.handle_job(selected_action, params)
        print(f"Job [{job_id}] handled successfully. Current status -> {status.value}")
        logger.debug(f"Job handled with status {status}")


def run_server():
    """
    This is the SYNCHRONOUS entry point for the CLI.
    It boots the event loop and runs your async main().
    """
    asyncio.run(main())


if __name__ == "__main__":
    run_server()
