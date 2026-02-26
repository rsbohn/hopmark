---
name: hopmark
description: Communicate with the CircuitPython device at 192.168.0.33 using Web Workflow (list/read/write files, device info, peer discovery).
---

# Hopmark Web Workflow

## Purpose

Use this skill to interact with the CircuitPython device at `circuitpython.local` via Web Workflow APIs.

## Common workflows

### CLI (uv run)

```bash
CP_WEB_WORKFLOW_HOST=<hostname|ip-address>
read -p "password? " CP_WEB_WORKFLOW_PASSWORD
uv run ./skills/hopmark/hopmark.py list
uv run ./skills/hopmark/hopmark.py read /code.py
uv run ./skills/hopmark/hopmark.py write /hello.txt --text "hello"
uv run ./skills/hopmark/hopmark.py delete /hello.txt
```

Perhaps you will `alias hop="uv run skills/hopmark/hopmark.py"`

## Notes

- Requires `aiohttp` for the CLI tool; install in a venv if needed.
- CLI defaults can be overridden with `CP_WEB_WORKFLOW_HOST` and `CP_WEB_WORKFLOW_PASSWORD` (default password is `no-password-provided`).
- Web Workflow uses HTTP Basic Auth with a blank username and the device password.
- The file listing endpoint returns JSON (`/fs/`) when available.
