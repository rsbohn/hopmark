# hopmark

Hopmark provides a Web Workflow helper for interacting with a CircuitPython device (default host: `circuitpython.local`). The repo packages the skill assets and a small CLI wrapper.

## Contents

- `skills/hopmark/SKILL.md` — skill documentation and usage guidance
- `skills/hopmark/hopmark.py` — CLI helper for listing, reading, writing, and deleting files via Web Workflow

## Usage (CLI)

```bash
read -p "?? " CP_WEB_WORKFLOW_PASSWORD
uv run skills/hopmark/hopmark.py list
uv run skills/hopmark/hopmark.py read /code.py
uv run skills/hopmark/hopmark.py write /hello.txt --text "hello"
uv run skills/hopmark/hopmark.py delete /hello.txt
```

## Notes

- The CLI relies on `aiohttp`. Install dependencies in your virtual environment as needed.
- Web Workflow uses HTTP Basic Auth with a blank username and the device password.
