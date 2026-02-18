"""
This is a main file to run our MCP server
"""

import asyncio

from src.MCP_ffmpeg.jobs.job_manager import JobManager
from src.MCP_ffmpeg.jobs.models import JobAction
from src.MCP_ffmpeg.utils.loggers import get_logger
from src.MCP_ffmpeg.utils.cli_utils import prompt_params_for_action

job_manager = JobManager()
logger = get_logger(__name__)


async def main():
    """
    This method is the main method that we will execute to run the server and use the tools

    :return: None
    """

    logger.info("MCP FFmpeg Server started!!")

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
    print(f"Job status -> {status.value}")


if __name__ == "__main__":
    asyncio.run(main())
