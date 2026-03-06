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
- **Caching** — Same inputs produce the same job ID; completed jobs are reused unless `force_run` is used.

## Requirements

- **Python** 3.13+
- **FFmpeg** — Must be on your system PATH or set via `FFMPEG_PATH` (see [Configuration](#configuration)).

## Installation

From the project root:

```bash
# With uv
uv sync

# Or with pip
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

```bash
# From project root (with src on PYTHONPATH)
uv run python -m MCP_ffmpeg.main

# Or after pip install
python -m MCP_ffmpeg.main
```

You get a menu: choose an action, enter the requested parameters. Jobs are enqueued and processed by background workers. Logs show which worker picked which job.

### MCP server (stdio)

For MCP clients (e.g. Claude Desktop) that talk over stdio:

```bash
uv run python -m MCP_ffmpeg.mcp_server
```

Or point your MCP config to the `mcp-ffmpeg` package and the `mcp_server` module as needed by your client.

Dummy `claude_desktop_config.json` file

```bash
{
  "mcpServers": {
    "mcp-ffmpeg": {
      "command": "MCP-FFMPEG\\.venv\\Scripts\\python.exe",
      "args": [
        "-m",
        "MCP_ffmpeg.mcp_server"
      ],
      "env": {
        "FFMPEG_PATH": "C:\\ffmpeg\\bin\\ffmpeg.exe"
      }
    }
  },
  "preferences": {
    "coworkWebSearchEnabled": true,
    "sidebarMode": "chat",
    "coworkScheduledTasksEnabled": false
  }
}
```

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
