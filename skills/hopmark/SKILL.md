---
name: hopmark
description: Communicate with the CircuitPython device at 192.168.0.33 using Web Workflow (list/read/write files, device info, peer discovery).
---

# Hopmark Web Workflow

## Purpose

Use this skill to interact with the CircuitPython device at `192.168.0.33` via Web Workflow APIs.

## Reference implementation

The helper class lives at:

- `/mnt/e/rsbohn/disco-mcp/disco/mcp/web_workflow.py`

## Common workflows

### CLI (uv run)

```bash
read -p "?? " CP_WEB_WORKFLOW_PASSWORD
uv run .pi/skills/hopmark/hopmark.py list
uv run .pi/skills/hopmark/hopmark.py read /code.py
uv run .pi/skills/hopmark/hopmark.py write /hello.txt --text "hello"
uv run .pi/skills/hopmark/hopmark.py delete /hello.txt
```

### Connect and list files (Python)

```python
import asyncio
from disco.mcp.web_workflow import WebWorkflow

async def main():
    async with WebWorkflow("192.168.0.33", "<password>") as ww:
        files = await ww.list_files()
        print(files)

asyncio.run(main())
```

### Read a file

```python
import asyncio
from disco.mcp.web_workflow import WebWorkflow

async def main():
    async with WebWorkflow("192.168.0.33", "<password>") as ww:
        content = await ww.read_file("code.py")
        print(content.decode("utf-8"))

asyncio.run(main())
```

### Write a file

```python
import asyncio
from disco.mcp.web_workflow import WebWorkflow

async def main():
    async with WebWorkflow("192.168.0.33", "<password>") as ww:
        await ww.write_file("hello.txt", b"hello from web workflow\n")

asyncio.run(main())
```

### Delete a file

```python
import asyncio
from disco.mcp.web_workflow import WebWorkflow

async def main():
    async with WebWorkflow("192.168.0.33", "<password>") as ww:
        await ww.delete_file("hello.txt")

asyncio.run(main())
```

### Device info and discovery

```python
import asyncio
from disco.mcp.web_workflow import WebWorkflow

async def main():
    async with WebWorkflow("192.168.0.33", "<password>") as ww:
        info = await ww.get_device_info()
        peers = await ww.discover_peers()
        print(info)
        print(peers)

asyncio.run(main())
```

### Hash a remote file

```python
import asyncio
from disco.mcp.web_workflow import WebWorkflow

async def main():
    async with WebWorkflow("192.168.0.33", "<password>") as ww:
        digest = await ww.hash_file("code.py", algorithm="sha256")
        print(digest)

asyncio.run(main())
```

## Notes

- Requires `aiohttp` for the CLI tool; install in a venv if needed.
- CLI defaults can be overridden with `CP_WEB_WORKFLOW_HOST` and `CP_WEB_WORKFLOW_PASSWORD` (default password is `no-password-provided`).
- Web Workflow uses HTTP Basic Auth with a blank username and the device password.
- The file listing endpoint returns JSON (`/fs/`) when available.
