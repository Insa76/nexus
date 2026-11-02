import asyncio
from email.message import EmailMessage
import aiosmtplib


async def send_email(
    smtp_host,
    smtp_port,
    username,
    password,
    to,
    subject,
    body
):

    msg = EmailMessage()
    msg["From"] = username
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    await aiosmtplib.send(
        msg,
        hostname=smtp_host,
        port=smtp_port,
        username=username,
        password=password,
        start_tls=True
    )

    return "Email enviado"