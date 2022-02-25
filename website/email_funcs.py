import smtplib
from website import cred_web
from email.message import EmailMessage


def itoven_send_email_str(to, subject, message):
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(cred_web.username, cred_web.password)
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = subject
    msg['To'] = to
    msg['From'] = cred_web.username
    server.send_message(msg)
    server.quit()
