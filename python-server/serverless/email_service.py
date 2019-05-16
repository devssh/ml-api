import smtplib
import os
import email_service

methods = {
    "register": {
        "url": "/register/<twemail>",
        "http_methods": ["POST"]
    }
}


def register(twemail):
    import uuid
    email_service.send_mail(twemail, "TW ML API registration", "",
                            "To complete registration use the code " + uuid.uuid4().hex)
    return "Check email to complete verification"


def send_mail(to_addrs, subject, extra, body):
    fromaddr = 'mlapi.tw@gmail.com'
    msg = "\r\n".join([
        "From: " + fromaddr,
        "To: " + to_addrs,
        "Subject: " + subject,
        extra,
        body
    ])
    username = os.environ['username']
    password = os.environ['password']
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(fromaddr, to_addrs, msg)
    server.quit()
    return "Mail sent to " + to_addrs
