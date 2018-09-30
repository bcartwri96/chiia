# module responsible for interfacing with a front facing API to
# our email system

# import libs
import sendgrid
import models as ml
import os
from sendgrid.helpers.mail import *

# define basic functionality for all emails
def basic(t, f):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(f)
    to_email = Email(t)
    return sg, from_email, to_email


# send an email to a particular user programatically
def send_user(u_id, subj, content, html):
    u = ml.User.query.get(u_id)
    sg, f, t = basic(str(u.email), "test@example.com")
    content = Content("text/plain", content)
    mail = Mail(f, subj, t, content)
    response = sg.client.mail.send.post(request_body=mail.get())

    return response.status_code


# ==========================
# testing functionality
# ==========================

def send_test():
    # using SendGrid's Python Library
    # https://github.com/sendgrid/sendgrid-python

    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("test@example.com")
    to_email = Email("test@example.com")
    subject = "Sending with SendGrid is Fun"
    content = Content("text/plain", "and easy to do anywhere, even with Python")
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)
