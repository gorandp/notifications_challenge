import ssl
from asyncio import sleep
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
# from email.header import Header
# from email.utils import formataddr

from app.core.channel import ChannelType
from app.core.channel_strategy import IChannelStrategy
from app.core.logger import LoggerConfig
from app.interface.channel_strategies.email_mock_server import (
    EmailMockServer,
    SMTP_DEBUG_SERVER,
)


EMAIL_REGEX = re.compile(r"^[\w\d\._-]+(\+\w+)?@([\w-]+\.)+[\w-]{2,4}$")


class EmailChannel(IChannelStrategy):
    strategy_type = ChannelType.EMAIL.value

    def __init__(self, channel):
        self.channel = channel
        self.server = None
        self.logger = LoggerConfig.get_logger(__name__)

    async def _connect(self):
        context = ssl.create_default_context()
        for _ in range(5):
            if self.channel.resource_url == SMTP_DEBUG_SERVER:
                # Debug mode
                server = EmailMockServer(
                    self.channel.resource_url,
                    self.channel.port_url,
                )
            else:
                # Normal mode
                server = smtplib.SMTP(
                    self.channel.resource_url,
                    self.channel.port_url,
                )
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            try:
                server.login(
                    self.channel.credential_user,
                    self.channel.credential_pass,
                )
                self.server = server
                break
            except smtplib.SMTPAuthenticationError as e:
                # Authentication is wrong
                self.logger.error(f"{type(e).__name__}: {e}")
            except Exception as e:
                self.logger.error(f"Unknown error | {type(e).__name__}: {e}")
            server.quit()
            self.logger.info("Sleeping 30s")
            await sleep(30)
        else:
            raise RuntimeError("Couldn't connect to SMTP server")
        # self.sender_email = formataddr(
        #     (
        #         str(Header(self.channel.sender_name, 'utf-8')),
        #         self.channel.credential_user
        #     )
        # )

    async def _close(self):
        if self.server is None:
            return
        try:
            self.server.quit()
        except Exception as e:
            self.logger.error(f"Unknown error | {type(e).__name__}: {e}")

    async def send(self, notification):
        await self._connect()
        await self.validate_notification(notification)
        message = self._build_message_(
            notification.title,
            notification.content,
            self.channel.credential_user,
            notification.recipient,
        )
        for _ in range(5):
            try:
                self.server.sendmail(
                    from_addr=self.channel.credential_user,
                    to_addrs=[notification.recipient],
                    msg=message.as_string(),
                )
                break
            except Exception as e:
                self.logger.error(
                    f"Message not sent, sleeping 30s. {type(e).__name__}: {e}"
                )
            await sleep(30)
        else:
            raise RuntimeError("Can't send email")
        await self._close()

    def _build_message_(
        subject: str,
        content: str,
        email_from: str,
        email_to: str,
    ) -> MIMEMultipart:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = email_from
        message["To"] = email_to

        content_l = [
            "<!DOCTYPE html>",
            "<html><head>",
            "<style>",
            ".content { font-family: Montserrat, sans-serif; }",
            # ".footer { font-family: Montserrat, sans-serif; }",
            "</style>",
            "</head>",
            '<body><div class="content">',
            content,
            "</div></body>",
            # "<div class=\"footer\">"
            # "Notification sent via ..."
            # "</div>",
            "</html>",
        ]
        html_content = "\n".join(content_l)

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText("Mail content is HTML only", "plain")
        part2 = MIMEText(html_content, "html")

        message.attach(part1)
        message.attach(part2)

        return message

    @classmethod
    def validate_notification(cls, notification):
        if len(notification.title) > 900:
            raise ValueError("Title is too long")
        if len(notification.recipient) > 320:
            raise ValueError("Recipient lenght is too long")
        if not EMAIL_REGEX.match(notification.recipient):
            raise ValueError("Recipient email format is not valid")
        if notification.channel_type != cls.strategy_type:
            raise ValueError("Wrong channel")
