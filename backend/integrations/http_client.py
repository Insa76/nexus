import httpx


async def http_request(method, url, headers=None, body=None, timeout=10):

    async with httpx.AsyncClient(timeout=timeout) as client:

        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            json=body
        )

        response.raise_for_status()

        return {
            "status": response.status_code,
            "data": response.json() if "application/json" in response.headers.get("content-type","") else response.text
        }