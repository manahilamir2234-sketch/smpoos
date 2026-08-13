"""
Simulated email delivery for SMPOOS notifications.

The assessment brief requires notification delivery via in-system alerts
and email. This module records outbound email events so the prototype can
demonstrate the delivery path without connecting to a live SMTP server.
"""

from datetime import datetime


_EMAIL_LOG = []


def send_notification_email(recipient_email: str, subject: str, body: str) -> dict:
    """
    Simulate sending an email alert.

    Returns a delivery record that is also stored in the in-memory log.
    """
    record = {
        "timestamp": datetime.now().isoformat(),
        "recipient": recipient_email,
        "subject": subject,
        "body": body,
        "status": "simulated_sent",
    }
    _EMAIL_LOG.append(record)
    return record


def get_email_log():
    """Return a copy of the simulated email delivery log."""
    return list(_EMAIL_LOG)
