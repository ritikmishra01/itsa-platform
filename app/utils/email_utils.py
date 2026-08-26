import smtplib
import threading
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

logger = logging.getLogger(__name__)

def _send_async_email(app_config, to_email, subject, html_body):
    try:
        host = app_config.get('SMTP_HOST')
        port = app_config.get('SMTP_PORT', 587)
        user = app_config.get('SMTP_USERNAME')
        password = app_config.get('SMTP_PASSWORD')
        use_tls = app_config.get('SMTP_USE_TLS', True)
        from_name = app_config.get('EMAIL_FROM_NAME', 'ITSA Platform')
        from_address = app_config.get('EMAIL_FROM_ADDRESS', 'noreply@itsa.edu')

        if not host or not user or not password or password == 'dummy_app_password':
            logger.info(f"[EMAIL MOCK] Email to {to_email} with subject '{subject}' logged (SMTP not configured).")
            return

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{from_name} <{from_address}>"
        msg['To'] = to_email

        part = MIMEText(html_body, 'html')
        msg.attach(part)

        server = smtplib.SMTP(host, port, timeout=10)
        if use_tls:
            server.starttls()
        server.login(user, password)
        server.sendmail(from_address, [to_email], msg.as_string())
        server.quit()
        logger.info(f"Email sent successfully to {to_email}")
    except Exception as e:
        logger.warning(f"Failed to send email to {to_email}: {e}")


def send_email(to_email, subject, html_body):
    """Dispatches email asynchronously in a background thread."""
    if not to_email:
        return
    app_config = {
        'SMTP_HOST': current_app.config.get('SMTP_HOST'),
        'SMTP_PORT': current_app.config.get('SMTP_PORT'),
        'SMTP_USERNAME': current_app.config.get('SMTP_USERNAME'),
        'SMTP_PASSWORD': current_app.config.get('SMTP_PASSWORD'),
        'SMTP_USE_TLS': current_app.config.get('SMTP_USE_TLS'),
        'EMAIL_FROM_NAME': current_app.config.get('EMAIL_FROM_NAME'),
        'EMAIL_FROM_ADDRESS': current_app.config.get('EMAIL_FROM_ADDRESS')
    }
    thread = threading.Thread(target=_send_async_email, args=(app_config, to_email, subject, html_body))
    thread.daemon = True
    thread.start()
