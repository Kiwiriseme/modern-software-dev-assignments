##可调用但是api失效
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("train_tickets")

API_BASE = "https://api.lolimi.cn/API/hc/api"
USER_AGENT = "train_tickets-app/1.0"


## 异步HTTP请求函数
async def make_train_tickets_request(url: str) -> dict[str, Any] | None:
    ## 设置请求头存储HTTP请求信息，标识应用和接受的响应格式
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    ## 异步发送GET请求
    ## 等待响应并检查状态码
    ## 解析JSON响应并返回
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


@mcp.tool()
async def get_train_tickets(departure: str, arrival: str, departtime: str) -> str:
    url = f"{API_BASE}?departure={departure}&arrival={arrival}&departtime={departtime}"
    data = await make_train_tickets_request(url)
    if not data:
        return "Unable to fetch train tickets."
    tickets = data["data"]
    ticket_list = []
    for ticket in tickets[:1]:
        ticket_data = f"""
    TrainNunber: {ticket['TrainNunber']}
    start: {ticket['start']}
    end: {ticket['end']}
    DepartTime: {ticket['DepartTime']}
    ArriveTime: {ticket['ArriveTime']}
    SeatList: {ticket['SeatList']}
    TimeDifference: {ticket['TimeDifference']}
    """
        ticket_list.append(ticket_data)
    return "\n---\n".join(ticket_list)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
