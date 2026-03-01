"""
This file contains the util methods to interact with CLI
"""

import asyncio
import os
import shutil
from pathlib import Path

from MCP_ffmpeg.jobs.models import JobAction
from MCP_ffmpeg.actions.models import JOB_ACTION_PARAMS
from MCP_ffmpeg.utils.loggers import get_logger

logger = get_logger(__name__)


async def prompt_params_for_action(action: JobAction) -> dict:
    """
    This method takes the required params for the provided action

    :param action: action to perform
    :return: params
    """

    schema = JOB_ACTION_PARAMS.get(action)
    if not schema:
        raise ValueError(f"No param schema defined for action: {action}")
    logger.debug(f"Expected schema for action [{action.value}] -> {schema}")

    params = {}
    print("\nEnter required parameters:")

    for key, typ in schema.items():
        while True:
            raw = await asyncio.to_thread(
                input, f"- {key} ({typ.__name__}): "
            )
            raw = raw.strip()

            try:
                if typ is str:
                    value = raw
                elif typ is float:
                    value = float(raw)
                elif typ is int:
                    value = int(raw)
                else:
                    value = typ(raw)

                params[key] = value
                break

            except ValueError:
                print(f"Invalid value for {key}. Expected {typ.__name__}. Try again.")

    logger.debug(f"Params provided by user: {params}")
    return params


def resolve_ffmpeg() -> str:
    """
    Resolve ffmpeg executable path in this priority order:
    1. FFMPEG_PATH env variable (Claude MCP case)
    2. ffmpeg available in system PATH (CLI case)
    3. Common Windows install location (fallback)
    """

    # 1️⃣ Env variable (for Claude Desktop)
    env_path = os.getenv("FFMPEG_PATH")
    if env_path and Path(env_path).exists():
        return env_path

    # 2️⃣ System PATH (for CLI use)
    which_path = shutil.which("ffmpeg")
    if which_path:
        return which_path

    # 3️⃣ Common Windows fallback
    default_path = Path("C:/ffmpeg/bin/ffmpeg.exe")
    if default_path.exists():
        return str(default_path)

    raise FileNotFoundError(
        "ffmpeg.exe not found.\n"
        "Install FFmpeg or set FFMPEG_PATH env variable."
    )