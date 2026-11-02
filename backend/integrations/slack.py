import httpx


async def send_slack(webhook_url, message):

    async with httpx.AsyncClient() as client:

        res = await client.post(
            webhook_url,
            json={"text": message}
        )

        res.raise_for_status()

        return "Slack enviado"