import socket
from email.mime.text import MIMEText
from functools import lru_cache
from typing import Any, Dict

from aiosmtplib import SMTP, SMTPAuthenticationError, SMTPConnectError, SMTPException
from jinja2 import Environment, FileSystemLoader, select_autoescape
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings


class EmailHandler:
    def __init__(
        self,
        smtp_host: str = settings.smtp_host,
        smtp_port: int = settings.smtp_port,
        smtp_username: str = settings.smtp_username,
        smtp_password: str = settings.smtp_password,
        email_from: str = settings.email_from,
        template_path: str = settings.email_templates_path,
    ) -> None:
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.email_from = email_from
        self.env = Environment(
            loader=FileSystemLoader(template_path),
            autoescape=select_autoescape(["html", "xml"]),
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (SMTPException, socket.gaierror, TimeoutError, ConnectionRefusedError)
        ),
        reraise=True,
    )
    async def send_email(self, to: str, subject: str, html_content: str) -> None:
        msg = MIMEText(html_content, "html", "utf-8")
        msg["Subject"] = subject
        msg["From"] = self.email_from
        msg["To"] = to

        try:
            smtp = SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                timeout=10,
                start_tls=self.smtp_port == 587,
                use_tls=self.smtp_port == 465,
            )
            try:
                await smtp.connect()
                await smtp.login(self.smtp_username, self.smtp_password)
                await smtp.send_message(msg)
            finally:
                if smtp.is_connected:
                    await smtp.quit()
        except SMTPAuthenticationError as exc:
            logger.error(f"[SMTP] Authentication failed while sending to {to}: {type(exc).__name__}: {exc}")
            raise
        except SMTPConnectError as exc:
            logger.error(f"[SMTP] Could not connect while sending to {to}: {type(exc).__name__}: {exc}")
            raise
        except SMTPException as exc:
            logger.error(f"[SMTP] SMTP error while sending to {to}: {type(exc).__name__}: {exc}")
            raise
        except (socket.gaierror, ConnectionRefusedError, TimeoutError) as exc:
            logger.error(f"[SMTP] Network error while sending to {to}: {type(exc).__name__}: {exc}")
            raise
        except Exception as exc:
            logger.exception(f"[SMTP] Unexpected error while sending to {to}: {type(exc).__name__}: {exc}")
            raise

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        template = self.env.get_template(template_name)
        return template.render(**context)


@lru_cache
def get_email_handler() -> EmailHandler:
    return EmailHandler()


email_handler = get_email_handler()
