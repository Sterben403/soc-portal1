import httpx
import smtplib
from email.mime.text import MIMEText
from app.models.notification import Notification
from app.db.database import SessionLocal
from sqlalchemy.future import select

async def send_notification_event(event: str, message: str):
    async with SessionLocal() as db:
        result = await db.execute(select(Notification).where(Notification.event == event, Notification.is_active == True))
        notifs = result.scalars().all()

        for notif in notifs:
            if notif.channel == "email":
                await send_email(notif.target, message)
            elif notif.channel == "telegram":
                await send_telegram(notif.target, message)
            elif notif.channel == "webhook":
                await send_webhook(notif.target, message)

async def send_email(to: str, message: str):
    msg = MIMEText(message)
    msg['Subject'] = "SOC Уведомление"
    msg['From'] = "noreply@soc.com"
    msg['To'] = to

    with smtplib.SMTP("smtp.example.com", 587) as server:
        server.starttls()
        server.login("noreply@soc.com", "password")
        server.sendmail(msg['From'], [msg['To']], msg.as_string())

async def send_telegram(chat_id: str, message: str):
    async with httpx.AsyncClient() as client:
        await client.post(f"https://api.telegram.org/bot<token>/sendMessage", json={
            "chat_id": chat_id,
            "text": message
        })

async def send_webhook(url: str, message: str):
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"text": message})