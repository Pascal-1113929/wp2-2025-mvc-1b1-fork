import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

CONNECTION = {"host": "127.0.0.1", "port": 2525}
# using docker run -p 4999:80 -p 2525:25 -p 110:110 rnwood/smtp4dev


def send_mail(subject, body, reciever):
    """
    :param subject: Email subject
    :param body: Email body in HTML format
    :param reciever: Email reciever

    This is a Fucntion to send an email connection:
    "host": "127.0.0.1", "port": 2525
    To use it do command: docker run -p 4999:80 -p 2525:25 -p 110:110 rnwood/smtp4dev
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = "noreply@hub.com"
    msg["To"] = reciever

    part = MIMEText(body, "html")
    msg.attach(part)
    print("Sending email...", CONNECTION["host"], CONNECTION["port"])

    with smtplib.SMTP(CONNECTION["host"], CONNECTION["port"]) as server:
        server.sendmail(msg["From"], [msg["To"]], msg.as_string())
