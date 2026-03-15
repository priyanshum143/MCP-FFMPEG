"""
This file contains some common variables being used across the project
"""

from pathlib import Path


class CommonVariables:
    ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
    OUTPUT_DIR = ROOT_DIR / "outputs"
    LOGS_DIR = ROOT_DIR / "logs"

    JOB_DETAILS_JSON_FILE_NAME = "job_details.json"

    PARALLEL_EXECUTIONS_ALLOWED = 3
    WORKER_RE_RUN_TIME = 10

    SUB_ENCODER_MAP: dict[str, str] = {
        "srt": "subrip",
        "vtt": "webvtt",
        "ass": "ass",
        "ssa": "ssa",
    }
    UNSUPPORTED_BY_FFMPEG = {"scc"}

    AUDIO_ENCODER_MAPPING = {
        "mp3": "libmp3lame",
        "aac": "aac",
        "wav": "pcm_s16le",
        "flac": "flac",
        "m4a": "aac",
        "opus": "libopus",
        "ogg": "libvorbis",
    }
