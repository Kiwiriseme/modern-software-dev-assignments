from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("dog_image")

API_BASE = "https://dog.ceo/api"
USER_AGENT = "dog-image-app/1.0"


async def make_dog_image_request(url: str) -> dict[str, Any] | None:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


@mcp.tool()
async def get_dog_image(breed: str) -> str:
    url = f"{API_BASE}/breed/{breed}/images/random"
    data = await make_dog_image_request(url)
    if not data or data.get("status") != "success":
        return "Unable to fetch dog image."
    return data["message"]


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
