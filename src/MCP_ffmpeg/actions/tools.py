"""
This file contains the code for different FFmpeg tools
"""

import asyncio
from pathlib import Path

from src.MCP_ffmpeg.utils.loggers import get_logger, get_job_ffmpeg_logger
from src.MCP_ffmpeg.utils.variables import CommonVariables

logger = get_logger(__name__)


async def trim_a_video(
    input_file: str,
    start_time: float,
    duration: float,
    job_id: str,
) -> str:
    """
    This method will trim the input video according to the given params

    :param input_file: input file to trim
    :param start_time: start time to trim the video
    :param duration: duration of the trimmed video
    :param job_id: job id
    :return: trimmed video path
    """

    # Checking if the input file exists
    input_path = Path(input_file)
    logger.debug(f"Input file's path for trim: [{input_path}]")
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Setting up the output file directory
    job_dir = CommonVariables.OUTPUT_DIR / job_id
    output_file = job_dir / f"output{input_path.suffix}"
    logger.debug(f"Output file will be stored at: [{output_file}]")

    # Creating a command for the trim action
    cmd = [
        "ffmpeg",
        "-y",
        "-ss", str(start_time),
        "-i", str(input_path),
        "-t", str(duration),
        "-c", "copy",
        str(output_file),
    ]
    logger.debug(f"Command used to trim the given video: [{cmd}]")

    # Setting up the logger file for this action
    ffmpeg_log = get_job_ffmpeg_logger(job_id)
    ffmpeg_log.info("Command: %s", " ".join(map(str, cmd)))

    # Starting the process to trim the video
    print(f"\njob_id={job_id} | Starting trim process | input={input_path}")
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
    )

    # Stream stderr to file line-by-line
    stderr_lines: list[str] = []
    while True:
        line = await process.stderr.readline()
        if not line:
            break
        msg = line.decode(errors="replace").rstrip()
        stderr_lines.append(msg)
        ffmpeg_log.info(msg)

    # Checking the return code
    return_code = await process.wait()
    if return_code != 0:
        tail = "\n".join(stderr_lines[-20:])
        logger.error(f"job_id={job_id} | FFmpeg trim failed")
        ffmpeg_log.error(f"FFmpeg exited with code={return_code}")
        raise RuntimeError("FFmpeg trim failed\n" + tail)

    print(f"job_id={job_id} | Trim complete | output={output_file}")
    ffmpeg_log.info(f"Success. Output: {output_file}")
    return str(output_file)
