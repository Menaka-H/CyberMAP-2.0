# utils/alerting.py - CyberMAP 2.0 Email Alerting for Continuous Monitoring
#
# Sends an email notification when a drift event is detected during
# continuous monitoring. Credentials are read from a local .env file,
# never hardcoded, and .env is excluded from version control.

import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
ALERT_RECIPIENT = os.getenv("ALERT_RECIPIENT")


def is_email_configured():
    """Returns True if all required email settings are present."""
    return bool(GMAIL_ADDRESS and GMAIL_APP_PASSWORD and ALERT_RECIPIENT)


def build_drift_alert_email(endpoint_name, drift_events):
    """
    Builds the subject and body text for a drift alert email.
    Kept separate from the send function so the message can be
    previewed in the UI without actually sending it.
    """
    subject = f"CyberMAP Alert: {len(drift_events)} posture change(s) detected on {endpoint_name}"

    lines = [
        f"CyberMAP Continuous Monitoring detected the following change(s)",
        f"on endpoint: {endpoint_name}",
        "",
    ]
    for event in drift_events:
        lines.append(f"Check: {event['check']}")
        lines.append(f"  Previous: {event['previous_status']} (at {event['previous_time']})")
        lines.append(f"  Current:  {event['current_status']} (at {event['current_time']})")
        lines.append("")

    lines.append("This is an automated alert from CyberMAP 2.0.")
    lines.append("Log in to the platform to review full details and take action.")

    body = "\n".join(lines)
    return subject, body


def send_drift_alert(endpoint_name, drift_events, timeout_seconds=10):
    """
    Sends a drift alert email via Gmail SMTP. Returns a dict:
    {"sent": bool, "error": str or None}

    Never raises - any failure (missing config, network error, auth
    failure) is caught and returned so the calling page can display
    it gracefully without crashing the monitoring workflow.
    """
    if not is_email_configured():
        return {
            "sent": False,
            "error": "Email alerting is not configured. Add GMAIL_ADDRESS, "
                     "GMAIL_APP_PASSWORD, and ALERT_RECIPIENT to the .env file.",
        }

    subject, body = build_drift_alert_email(endpoint_name, drift_events)

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = ALERT_RECIPIENT
        msg.set_content(body)

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=timeout_seconds) as server:
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        return {"sent": True, "error": None}

    except Exception as e:
        return {"sent": False, "error": str(e)}
