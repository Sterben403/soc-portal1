import aiosmtplib
from email.message import EmailMessage
import os


async def send_email_with_attachment(to_email: str, subject: str, body: str, filename: str, file_bytes: bytes, mime_type: str):
    message = EmailMessage()
    message["From"] = os.getenv("SMTP_FROM")
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    message.add_attachment(
        file_bytes,
        maintype=mime_type.split("/")[0],
        subtype=mime_type.split("/")[1],
        filename=filename,
    )

    await aiosmtplib.send(
        message,
        hostname=os.getenv("SMTP_HOST"),
        port=int(os.getenv("SMTP_PORT", 587)),
        username=os.getenv("SMTP_USER"),
        password=os.getenv("SMTP_PASS"),
        use_tls=False,
        start_tls=True,
    )