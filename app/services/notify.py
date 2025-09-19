import httpx
import smtplib
import logging
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.models.notification import Notification
from app.db.database import SessionLocal
from sqlalchemy.future import select
import os
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

class NotificationService:
    """Enhanced notification service with retries, timeouts, and logging."""
    
    def __init__(self):
        self.timeout = httpx.Timeout(30.0)
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
    
    async def send_notification_event(self, event: str, message: str):
        """Send notification to all active subscribers for the event."""
        async with SessionLocal() as db:
            result = await db.execute(
                select(Notification).where(
                    Notification.event == event, 
                    Notification.is_active == True
                )
            )
            notifs = result.scalars().all()
            
            tasks = []
            for notif in notifs:
                if notif.channel == "email":
                    tasks.append(self._send_email_with_retry(notif.target, message))
                elif notif.channel == "telegram":
                    tasks.append(self._send_telegram_with_retry(notif.target, message))
                elif notif.channel == "webhook":
                    tasks.append(self._send_webhook_with_retry(notif.target, message))
            
            # Send all notifications concurrently
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"Failed to send notification {i}: {result}")
    
    async def _send_email_with_retry(self, to: str, message: str) -> bool:
        """Send email with retry logic."""
        for attempt in range(self.max_retries):
            try:
                await self._send_email(to, message)
                logger.info(f"Email sent successfully to {to}")
                return True
            except Exception as e:
                logger.warning(f"Email attempt {attempt + 1} failed to {to}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"Failed to send email to {to} after {self.max_retries} attempts")
                    return False
    
    async def _send_email(self, to: str, message: str):
        """Send email using SMTP."""
        msg = MIMEMultipart()
        msg['Subject'] = "SOC Portal Notification"
        msg['From'] = os.getenv("SMTP_FROM", "noreply@soc-portal.com")
        msg['To'] = to
        
        text_part = MIMEText(message, 'plain', 'utf-8')
        msg.attach(text_part)
        
        # Use aiosmtplib for async SMTP
        import aiosmtplib
        await aiosmtplib.send(
            msg,
            hostname=os.getenv("SMTP_HOST", "localhost"),
            port=int(os.getenv("SMTP_PORT", "587")),
            username=os.getenv("SMTP_USER"),
            password=os.getenv("SMTP_PASS"),
            use_tls=False,
            start_tls=True,
            timeout=self.timeout.timeout
        )
    
    async def _send_telegram_with_retry(self, chat_id: str, message: str) -> bool:
        """Send Telegram message with retry logic."""
        for attempt in range(self.max_retries):
            try:
                await self._send_telegram(chat_id, message)
                logger.info(f"Telegram message sent successfully to {chat_id}")
                return True
            except Exception as e:
                logger.warning(f"Telegram attempt {attempt + 1} failed to {chat_id}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                else:
                    logger.error(f"Failed to send Telegram to {chat_id} after {self.max_retries} attempts")
                    return False
    
    async def _send_telegram(self, chat_id: str, message: str):
        """Send message via Telegram Bot API."""
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not configured")
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            
            result = response.json()
            if not result.get("ok"):
                raise Exception(f"Telegram API error: {result.get('description')}")
    
    async def _send_webhook_with_retry(self, url: str, message: str) -> bool:
        """Send webhook with retry logic."""
        for attempt in range(self.max_retries):
            try:
                await self._send_webhook(url, message)
                logger.info(f"Webhook sent successfully to {url}")
                return True
            except Exception as e:
                logger.warning(f"Webhook attempt {attempt + 1} failed to {url}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                else:
                    logger.error(f"Failed to send webhook to {url} after {self.max_retries} attempts")
                    return False
    
    async def _send_webhook(self, url: str, message: str):
        """Send webhook notification."""
        payload = {
            "text": message,
            "timestamp": asyncio.get_event_loop().time(),
            "source": "soc_portal"
        }
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SOC-Portal/1.0"
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()

# Global notification service instance
notification_service = NotificationService()

# Backward compatibility
async def send_notification_event(event: str, message: str):
    """Legacy function for backward compatibility."""
    await notification_service.send_notification_event(event, message)