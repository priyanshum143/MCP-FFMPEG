"""
This file contains the code for different FFmpeg tools
"""

import os
import shutil
import asyncio
from pathlib import Path

from MCP_ffmpeg.utils.loggers import get_logger, get_job_ffmpeg_logger
from MCP_ffmpeg.utils.variables import CommonVariables

logger = get_logger(__name__)


def _resolve_ffmpeg() -> str:
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

    # Checking if the ffmpeg exists
    ffmpeg = _resolve_ffmpeg()

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
        ffmpeg,
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
    logger.info(f"\njob_id={job_id} | Starting trim process | input={input_path}")
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

    logger.info(f"job_id={job_id} | Trim complete | output={output_file}")
    ffmpeg_log.info(f"Success. Output: {output_file}")
    return str(output_file)


async def change_video_format(
    input_file: str,
    output_format: str,
    job_id: str,
) -> str:
    """
    This method will change the format (container) of the given video file.

    :param input_file: input video file
    :param output_format: desired output format (e.g., mp4, mkv, avi)
    :param job_id: job id
    :return: converted video path
    """

    # Checking if the ffmpeg exists
    ffmpeg = _resolve_ffmpeg()

    # Checking if the input file exists
    input_path = Path(input_file)
    logger.debug(f"Input file's path for format change: [{input_path}]")
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Normalize output format (remove dot if provided)
    output_format = output_format.lstrip(".")

    # Setting up the output file directory
    job_dir = CommonVariables.OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    output_file = job_dir / f"output.{output_format}"
    logger.debug(f"Output file will be stored at: [{output_file}]")

    # Creating command for format change
    cmd = [
        ffmpeg,
        "-y",
        "-i", str(input_path),
        "-c", "copy",   # no re-encoding, just container change
        str(output_file),
    ]
    logger.debug(f"Command used to change video format: [{cmd}]")

    # Setting up the logger file for this action
    ffmpeg_log = get_job_ffmpeg_logger(job_id)
    ffmpeg_log.info("Command: %s", " ".join(map(str, cmd)))

    # Starting the process
    logger.info(f"\njob_id={job_id} | Starting format change | input={input_path}")
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

    # Checking return code
    return_code = await process.wait()
    if return_code != 0:
        tail = "\n".join(stderr_lines[-20:])
        logger.error(f"job_id={job_id} | FFmpeg format change failed")
        ffmpeg_log.error(f"FFmpeg exited with code={return_code}")
        raise RuntimeError("FFmpeg format change failed\n" + tail)

    logger.info(f"job_id={job_id} | Format change complete | output={output_file}")
    ffmpeg_log.info(f"Success. Output: {output_file}")

    return str(output_file)


async def change_video_resolution(
    input_file: str,
    height: int,
    width: int,
    job_id: str,
) -> str:
    """
    This method will change the resolution of the given video file.

    :param input_file: input video file
    :param height: target height
    :param width: target width
    :param job_id: job id
    :return: converted video path
    """

    # Checking if the ffmpeg exists
    ffmpeg = _resolve_ffmpeg()

    # Checking if the input file exists
    input_path = Path(input_file)
    logger.debug(f"Input file's path for resolution change: [{input_path}]")
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Setting up the output file directory
    job_dir = CommonVariables.OUTPUT_DIR / job_id
    output_file = job_dir / f"output{input_path.suffix}"
    logger.debug(f"Output file will be stored at: [{output_file}]")

    # Creating command for resolution change (re-encoding required)
    cmd = [
        ffmpeg,
        "-y",
        "-i", str(input_path),
        "-vf", f"scale={width}:{height}",
        "-c:v", "libx264",
        "-c:a", "copy",
        str(output_file),
    ]
    logger.debug(f"Command used to change video resolution: [{cmd}]")

    # Setting up the logger file for this action
    ffmpeg_log = get_job_ffmpeg_logger(job_id)
    ffmpeg_log.info("Command: %s", " ".join(map(str, cmd)))

    # Starting the process
    logger.info(f"\njob_id={job_id} | Starting resolution change | input={input_path}")
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

    # Checking return code
    return_code = await process.wait()
    if return_code != 0:
        tail = "\n".join(stderr_lines[-20:])
        logger.error(f"job_id={job_id} | FFmpeg resolution change failed")
        ffmpeg_log.error(f"FFmpeg exited with code={return_code}")
        raise RuntimeError("FFmpeg resolution change failed\n" + tail)

    logger.info(f"job_id={job_id} | Resolution change complete | output={output_file}")
    ffmpeg_log.info(f"Success. Output: {output_file}")

    return str(output_file)


async def change_subtitle_format(
    input_file: str,
    target_format: str,
    job_id: str,
) -> str:
    """
    This method will convert the subtitle file to a different format (e.g. srt, vtt, ass).

    :param input_file: input subtitle file path
    :param target_format: desired subtitle format/extension (e.g. "srt", "vtt", "ass")
    :param job_id: job id
    :return: converted subtitle path
    """

    # Checking if the ffmpeg exists
    ffmpeg = _resolve_ffmpeg()

    # Checking if the input file exists
    input_path = Path(input_file)
    logger.debug(f"Input file's path for subtitle format change: [{input_path}]")
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Normalize/validate target format
    fmt = target_format.lower().lstrip(".")
    if not fmt:
        raise ValueError("target_format must be a non-empty extension like 'srt' or 'vtt'")

    # Setting up the output file directory
    job_dir = CommonVariables.OUTPUT_DIR / job_id
    output_file = job_dir / f"output.{fmt}"
    logger.debug(f"Output subtitle will be stored at: [{output_file}]")

    # Creating command for subtitle format conversion
    cmd = [
        ffmpeg,
        "-y",
        "-i", str(input_path),
        "-map", "0:s:0",
        "-c:s", fmt,
        str(output_file),
    ]
    logger.debug(f"Command used to change subtitle format: [{cmd}]")

    # Setting up the logger file for this action
    ffmpeg_log = get_job_ffmpeg_logger(job_id)
    ffmpeg_log.info("Command: %s", " ".join(map(str, cmd)))

    # Starting the process
    logger.info(f"\njob_id={job_id} | Starting subtitle format change | input={input_path}")
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

    # Checking return code
    return_code = await process.wait()
    if return_code != 0:
        tail = "\n".join(stderr_lines[-20:])
        logger.error(f"job_id={job_id} | FFmpeg subtitle format change failed")
        ffmpeg_log.error(f"FFmpeg exited with code={return_code}")
        raise RuntimeError("FFmpeg subtitle format change failed\n" + tail)

    logger.info(f"job_id={job_id} | Subtitle format change complete | output={output_file}")
    ffmpeg_log.info(f"Success. Output: {output_file}")

    return str(output_file)
