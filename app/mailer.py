import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl

smtp_host = os.getenv("SMTP_HOST", "")
smtp_port = os.getenv("SMTP_PORT", "")
smtp_user = os.getenv("SMTP_USER", "")
smtp_addr = os.getenv("SMTP_ADDR", "")
smtp_pass = os.getenv("SMTP_PASS", "")
smtp_starttls = os.getenv("SMTP_STARTTLS", "")


if smtp_starttls.lower() == "true":
    smtp = smtplib.SMTP(smtp_host, smtp_port)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
    smtp.ehlo()
    smtp.starttls(context=ctx)
    smtp.ehlo()
else:
    smtp = smtplib.SMTP_SSL(smtp_host, smtp_port)


async def send_email(to: str, subject: str, body: str):
    smtp.connect(smtp_host, smtp_port)
    smtp.login(smtp_user, smtp_pass)
    msg = MIMEMultipart()
    msg["From"] = smtp_addr
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    smtp.sendmail(smtp_addr, to, msg.as_string())
    smtp.quit()
    del msg


async def send_email_html(to: str, subject: str, body: str):
    smtp.connect(smtp_host, smtp_port)
    smtp.login(smtp_user, smtp_pass)
    msg = MIMEMultipart()
    msg["From"] = smtp_addr
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))
    smtp.sendmail(smtp_addr, to, msg.as_string())
    smtp.quit()
    del msg
