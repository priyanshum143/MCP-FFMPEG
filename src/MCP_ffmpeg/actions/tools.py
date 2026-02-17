"""
This file contains the code for different FFmpeg tools
"""

import asyncio
from pathlib import Path

from src.MCP_ffmpeg.utils.loggers import get_logger, get_job_ffmpeg_logger

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

    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    output_file = (
        input_path.parent
        / f"{input_path.stem}_trimmed_{start_time}_{duration}{input_path.suffix}"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-ss", str(start_time),
        "-i", str(input_path),
        "-t", str(duration),
        "-c", "copy",
        str(output_file),
    ]

    ffmpeg_log = get_job_ffmpeg_logger(job_id)
    logger.info("job_id=%s | starting trim | input=%s", job_id, input_path)
    ffmpeg_log.info("Command: %s", " ".join(map(str, cmd)))

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
    )

    stderr_lines: list[str] = []

    # Stream stderr to file line-by-line
    while True:
        line = await process.stderr.readline()
        if not line:
            break
        msg = line.decode(errors="replace").rstrip()
        stderr_lines.append(msg)
        ffmpeg_log.info(msg)

    return_code = await process.wait()

    if return_code != 0:
        tail = "\n".join(stderr_lines[-20:])
        logger.error("job_id=%s | FFmpeg trim failed", job_id)
        ffmpeg_log.error("FFmpeg exited with code=%s", return_code)
        raise RuntimeError("FFmpeg trim failed\n" + tail)

    logger.info("job_id=%s | trim complete | output=%s", job_id, output_file)
    ffmpeg_log.info("Success. Output: %s", output_file)
    return str(output_file)

async def main():
    output_file = await trim_a_video(
        "/media/priyanshu/Local Disk/Clips/Podcasts/video.mp4",
        10,
        10,
        "123",
    )
    print("Trimmed file created at:", output_file)


if __name__ == "__main__":
    asyncio.run(main())