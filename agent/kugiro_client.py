"""
kugiro_client.py — talks to Alex's Kugiro MCP server as a client.

Auth: Authorization: Bearer kgr_...  (a personal API key minted in Kugiro
settings). Transport: streamable-HTTP at <base>/api/mcp, matching the MCP
server design spec. Every tool output is a JSON string inside one text block,
so we parse the first text block of each result.
"""
import json
import os
from contextlib import asynccontextmanager

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


def _endpoint() -> str:
    base = os.environ.get("KUGIRO_BASE_URL", "http://localhost:3000").rstrip("/")
    return f"{base}/api/mcp"


def _auth_headers() -> dict:
    key = os.environ.get("KUGIRO_API_KEY", "")
    if not key:
        raise RuntimeError("KUGIRO_API_KEY is not set in .env")
    return {"Authorization": f"Bearer {key}"}


def _parse_tool_result(result) -> object:
    """Kugiro returns compact JSON inside a single text content block."""
    for block in result.content:
        if getattr(block, "type", None) == "text":
            return json.loads(block.text)
    return None


@asynccontextmanager
async def kugiro_session():
    """Open an authenticated MCP session to Kugiro."""
    async with streamablehttp_client(_endpoint(), headers=_auth_headers()) as (
        read, write, _,
    ):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def call_tool(session: ClientSession, name: str, args: dict | None = None):
    """Call one Kugiro MCP tool and return its parsed JSON payload."""
    result = await session.call_tool(name, args or {})
    payload = _parse_tool_result(result)
    if isinstance(payload, dict) and "error" in payload:
        raise RuntimeError(f"Kugiro tool '{name}' error: {payload['error']}")
    return payload


# --- Convenience wrappers for the tools we actually use -------------------

async def get_search_profile(session, profile_id: str | None = None) -> dict:
    args = {"profile_id": profile_id} if profile_id else {}
    return await call_tool(session, "get_search_profile", args)


async def list_jobs(session, profile_id: str | None = None,
                    min_score: int | None = None, limit: int = 50) -> list:
    args: dict = {"limit": limit}
    if profile_id:
        args["profile_id"] = profile_id
    if min_score is not None:
        args["min_score"] = min_score
    return await call_tool(session, "list_jobs", args)


async def get_job(session, job_id: str) -> dict:
    return await call_tool(session, "get_job", {"job_id": job_id})
