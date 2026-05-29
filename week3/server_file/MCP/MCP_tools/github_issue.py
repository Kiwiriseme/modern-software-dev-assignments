from typing import Any

import httpx
from config import GITHUB_TOKEN
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("github_issue")

github_token = GITHUB_TOKEN
API_BASE = "https://api.github.com"
USER_AGENT = "github-issue-app/1.0"

HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {github_token}",
    "User-Agent": USER_AGENT,
}


async def make_github_request(url: str, method: str = "GET") -> dict[str, Any] | None:
    if not github_token:
        return None
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=HEADERS, timeout=30.0)
            elif method == "POST":
                response = await client.post(url, headers=HEADERS, timeout=30.0)
            else:
                response = await client.request(method, url, headers=HEADERS, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
        except httpx.RequestError as e:
            return {"error": f"Network error: {e}"}
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}


@mcp.tool()
## 已知user，获取user的信息
async def get_users_info(user: str) -> str:
    if not github_token:
        return "GitHub Token not configured. Please set the GITHUB_TOKEN environment variable."

    url = f"{API_BASE}/users/{user}"
    data = await make_github_request(url)

    if not data:
        return f"Unable to fetch user info for '{user}'."

    if "error" in data:
        return f"Error fetching user info for '{user}': {data['error']}"

    return f"""
Username: {data.get('login', 'Unknown')}
Bio: {data.get('bio', 'N/A')}
Public Repos: {data.get('public_repos', 0)}
Repository URL: {data.get('repo_url', 'N/A')}
Profile: {data.get('html_url', 'N/A')}
"""


@mcp.tool()
## 已知owner，获取owner的所有仓库信息
async def get_users_repos_info(owner: str) -> str:
    if not github_token:
        return "GitHub Token not configured."

    url = f"{API_BASE}/users/{owner}/repos"
    data = await make_github_request(url)

    if not data:
        return f"Unable to fetch repository info for {owner}."

    if "error" in data:
        return f"Error: {data['error']}"

    if isinstance(data, str):
        return f"Unable to fetch repository info for {owner}."

    repos = []
    for dic in data[:5]:
        repo_text = f"""
ID: {dic.get('id', 'N/A')}
Name: {dic.get('name', 'N/A')}
Language: {dic.get('language', 'N/A')}
URL: {dic.get('html_url', 'N/A')}
"""
        repos.append(repo_text)

    return f"Some Repositories for {owner}:\n" + "\n---\n".join(repos)


@mcp.tool()
## 已知owner和repo，获取repo信息
async def get_repo_info(owner: str, repo: str) -> str:

    url = f"{API_BASE}/repos/{owner}/{repo}"
    data = await make_github_request(url)

    if not data or "message" == "NOT FOUND":
        return f"Unable to fetch repository info for {owner}/{repo}."

    return f"""
    FullName={data.get('full_name', 'N/A')}
    Created={data.get('created_at', 'N/A')}
    Updated={data.get('updated_at', 'N/A')}
    Language={data.get('language', 'N/A')}
    """


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
