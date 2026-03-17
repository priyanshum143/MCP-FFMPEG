# MCP-FFMPEG

An MCP (Model Context Protocol) server and CLI for running FFmpeg jobs via a job queue with configurable parallel workers.

## Features

- **Job queue** — Enqueue video jobs; workers process them in the background.
- **Parallel workers** — Run multiple jobs at once (number set in config).
- **Two interfaces**
  - **CLI** — Interactive menu to pick an action and enter parameters.
  - **MCP server** — Tools for AI assistants (e.g. Claude Desktop) to enqueue and check jobs.
- **Actions**
  - **Trim** — Cut a segment from a video (start time + duration).
  - **Change video format** — Convert to another container (e.g. mp4 → mkv) without re-encoding.
  - **Change resolution** — Convert to another resolution, height and width provided by user.
  - **Change Subtitle format** — Convert to another subtitle format (e.g. srt -> vtt).
  - **Extract Audio** - Extract audio from an input video file
- **Caching** — Same inputs produce the same job ID; completed jobs are reused unless `force_run` is used.

## Requirements

- **Python** 3.13+
- **FFmpeg** — Must be on your system PATH or set via `FFMPEG_PATH` (see [Configuration](#configuration)).

## Installation

Choose one of the following:

### Option 1: Install from PyPI

```bash
pip install mcp-ffmpeg
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add mcp-ffmpeg
```

### Option 2: Clone the repository

```bash
git clone https://github.com/priyanshum143/MCP-FFMPEG.git
cd MCP-FFMPEG
```

Then install from the project root:

```bash
# With uv
uv sync

# Or with pip (editable install)
pip install -e .
```

## Configuration

- **FFmpeg path**  
  - Default: use `ffmpeg` from system PATH.  
  - Optional: set env var `FFMPEG_PATH` to the full path of the FFmpeg executable (e.g. for Claude Desktop).

- **Worker and paths**  
  Edit `src/MCP_ffmpeg/utils/variables.py` (class `CommonVariables`):
  - `PARALLEL_EXECUTIONS_ALLOWED` — Number of jobs that can run at once (default: 3).
  - `WORKER_RE_RUN_TIME` — Seconds to wait between queue checks (default: 10).
  - `OUTPUT_DIR` / `LOGS_DIR` — Where job outputs and logs are stored (default: `outputs/` and `logs/` under project root).

## Running

### CLI (interactive)

You get a menu: choose an action, enter the requested parameters. Jobs are enqueued and processed by background workers. Logs show which worker picked which job.

**If you installed from PyPI:**

```bash
mcp-ffmpeg-cli
```

**If you cloned the repo:**

```bash
# With uv (from project root)
uv run python -m MCP_ffmpeg.main

# Or after pip install -e .
mcp-ffmpeg-cli
```

### MCP server (e.g. Claude Desktop)

Use the `mcp-ffmpeg` command so the MCP server runs over stdio.

**If you installed from PyPI:** use `mcp-ffmpeg` in your MCP config.

**If you cloned the repo:** after `pip install -e .`, use `mcp-ffmpeg` the same way. If you used `uv sync`, use `uv run mcp-ffmpeg` in the terminal, or in your MCP config use the path to your venv’s `mcp-ffmpeg` script so the server runs in that environment.

Add this to your `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or the equivalent config for your MCP client:

```json
{
  "mcpServers": {
    "mcp-ffmpeg": {
      "command": "mcp-ffmpeg",
      "env": {
        "FFMPEG_PATH": "C:\\path\\to\\your\\ffmpeg.exe"
      }
    }
  }
}
```

On macOS/Linux, use your normal config path and set `FFMPEG_PATH` to the path of your `ffmpeg` binary if needed.

## Project layout

```
src/MCP_ffmpeg/
├── main.py           # CLI entrypoint
├── mcp_server.py     # MCP server entrypoint + tool definitions
├── actions/          # FFmpeg actions (trim, change format)
├── jobs/             # Job queue, manager, worker
└── utils/            # Logging, paths, CLI helpers
```

- **outputs/** — One folder per job (by job ID), containing `job_details.json`, output file, and optional `ffmpeg_logs.log`.
- **logs/** — Application logs.

## License

No license required, Clone/Fork the repo and enjoy.

## Author

**Priyanshu** CSE 2025 Graduate | Software Engineer at Amagi Media Labs

- **GitHub**: [priyanshum143](https://github.com/priyanshum143)
- **LinkedIn**: [Priyanshu Mehta](https://www.linkedin.com/in/priyanshu-mehta-a40799238/) 
- **Project Repository**: [MCP-FFMPEG](https://github.com/priyanshum143/MCP-FFMPEG)
- **PyPi**: [MCP-FFmpeg](https://pypi.org/project/mcp-ffmpeg/)

Feel free to reach out for collaborations or if you encounter any issues!
