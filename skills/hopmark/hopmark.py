#!/usr/bin/env python3
import argparse
import asyncio
import json
import os
import sys
import hashlib

try:
    import aiohttp
    from aiohttp import BasicAuth
except ModuleNotFoundError as exc:
    print(
        "Error: aiohttp is required. Install with 'uv pip install aiohttp' in a venv.",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc


class WebWorkflow:
    def __init__(self, host, password, timeout=10.0):
        self.base_url = f"http://{host}"
        self.auth = BasicAuth('', password)
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(auth=self.auth, timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    async def list_files(self) -> dict:
        headers = {'Accept': 'application/json'}
        async with self.session.get(f"{self.base_url}/fs/", headers=headers) as r:
            r.raise_for_status()
            content_type = r.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                return await r.json()
            html = await r.text()
            print("[WebWorkflow] /fs/ returned HTML:")
            print(html)
            return {}

    async def read_file(self, path):
        async with self.session.get(f"{self.base_url}/fs/{path}") as r:
            r.raise_for_status()
            return await r.read()

    async def write_file(self, path, content):
        async with self.session.put(f"{self.base_url}/fs/{path}", data=content) as r:
            r.raise_for_status()

    async def delete_file(self, path):
        async with self.session.delete(f"{self.base_url}/fs/{path}") as r:
            r.raise_for_status()

    async def get_device_info(self) -> dict:
        """Get device information without authentication"""
        async with self.session.get(f"{self.base_url}/cp/version.json") as r:
            r.raise_for_status()
            return await r.json()

    async def discover_peers(self) -> dict:
        """Discover other CircuitPython devices on the network"""
        async with self.session.get(f"{self.base_url}/cp/devices.json") as r:
            r.raise_for_status()
            return await r.json()

    async def hash_file(self, path: str, algorithm: str = 'md5') -> str:
        """Stream and compute the hash of a remote file.
        Returns the hex digest. Algorithm may be 'md5', 'sha1', 'sha256', etc.
        """
        try:
            hasher = hashlib.new(algorithm)
        except ValueError as exc:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}") from exc
        async with self.session.get(f"{self.base_url}/fs/{path}") as r:
            r.raise_for_status()
            async for chunk in r.content.iter_chunked(8192):
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()


def normalize_path(path: str) -> str:
    return path.lstrip("/")


def read_payload(args: argparse.Namespace) -> bytes:
    if args.text is not None:
        return args.text.encode("utf-8")
    if args.file is not None:
        return open(args.file, "rb").read()
    return sys.stdin.buffer.read()


async def run_async(args: argparse.Namespace) -> int:
    async with WebWorkflow(args.host, args.password, timeout=args.timeout) as ww:
        if args.command == "list":
            result = await ww.list_files()
            print(json.dumps(result, indent=2, sort_keys=True))
        elif args.command == "read":
            data = await ww.read_file(normalize_path(args.path))
            if args.binary:
                sys.stdout.buffer.write(data)
            else:
                sys.stdout.write(data.decode("utf-8", errors="replace"))
        elif args.command == "write":
            content = read_payload(args)
            await ww.write_file(normalize_path(args.path), content)
        elif args.command == "delete":
            await ww.delete_file(normalize_path(args.path))
        elif args.command == "info":
            info = await ww.get_device_info()
            print(json.dumps(info, indent=2, sort_keys=True))
        elif args.command == "peers":
            peers = await ww.discover_peers()
            print(json.dumps(peers, indent=2, sort_keys=True))
        elif args.command == "hash":
            digest = await ww.hash_file(normalize_path(args.path), algorithm=args.algorithm)
            print(digest)
        else:
            raise ValueError(f"Unknown command: {args.command}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CircuitPython Web Workflow CLI")
    parser.add_argument("--host", default=os.environ.get("CP_WEB_WORKFLOW_HOST", "circuitpython.local"))
    parser.add_argument(
        "--password",
        default=os.environ.get("CP_WEB_WORKFLOW_PASSWORD", "no-password-provided"),
        help="Device password (or set CP_WEB_WORKFLOW_PASSWORD)",
    )
    parser.add_argument("--timeout", type=float, default=10.0, help="Total request timeout in seconds")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List files")

    read_parser = subparsers.add_parser("read", help="Read a file")
    read_parser.add_argument("path", help="Remote path, e.g. /code.py")
    read_parser.add_argument("--binary", action="store_true", help="Write raw bytes to stdout")

    write_parser = subparsers.add_parser("write", help="Write a file")
    write_parser.add_argument("path", help="Remote path, e.g. /code.py")
    write_group = write_parser.add_mutually_exclusive_group()
    write_group.add_argument("--text", help="Text payload (UTF-8)")
    write_group.add_argument("--file", help="Read payload from file")

    delete_parser = subparsers.add_parser("delete", help="Delete a file")
    delete_parser.add_argument("path", help="Remote path, e.g. /code.py")

    subparsers.add_parser("info", help="Get device info")
    subparsers.add_parser("peers", help="Discover peers")

    hash_parser = subparsers.add_parser("hash", help="Hash a remote file")
    hash_parser.add_argument("path", help="Remote path, e.g. /code.py")
    hash_parser.add_argument("--algorithm", default="md5", help="Hash algorithm (default: md5)")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        return asyncio.run(run_async(args))
    except aiohttp.ClientError as exc:
        print(f"Error: HTTP request failed: {exc}", file=sys.stderr)
    except asyncio.TimeoutError:
        print("Error: request timed out", file=sys.stderr)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
