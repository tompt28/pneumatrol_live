from django.core.management.base import BaseCommand
from ORWAapp.models import SalesOrder
from django.contrib.auth.models import User
from django import template
from datetime import *
from ORWAapp.models import *
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives, send_mail
import smtplib, ssl, email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Command(BaseCommand):
    help = "Sends email reminder to users with outstanding ORWA's"

    def handle(self, *args, **kwargs):
        
        SERVER_EMAIL = 'ORWA.Tracker@gmail.com'
        MAIL_HOST ="smtp.gmail.com"
        EMAIL_HOST_USER = 'ORWA.Tracker@gmail.com'
        EMAIL_HOST_PASSWORD = 'koayxjvqriwnltoq'
        EMAIL_PORT = 465

        # SERVER_EMAIL = 'orwa@pneumatrol.com'
        # MAIL_HOST = "192.168.0.253"
        # EMAIL_HOST_USER = 'orwa'
        # EMAIL_HOST_PASSWORD = 'Connect667_'
        # EMAIL_PORT = 25
        
        salesdata = SalesOrder.objects.filter(issue_date__isnull=True).filter(reject_date__isnull=True)

        contextdict = {
        'SalesOrder':salesdata,
        }

        subject ='Weekly ORWA list'
        
        Reminder = []

        sendreminder = Employee.objects.filter(ORWAReminder = True)
        
        for user in sendreminder:
            finduser = User.objects.get(username = user)
            emailaddress = finduser.email
            Reminder.append(emailaddress)

        text_content = 'see live.pneumatrol.com'
        html_content  = render_to_string('ORWAapp/home/EmailReminder.html', contextdict)
        
        #create message
        message = MIMEMultipart()
        #add parts to message
        message["From"] = SERVER_EMAIL
        message["To"] =  ', '.join(Reminder)
        message["Subject"] = subject
        message.preamble = 'ORWA Report'

        #add body options
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part2)
        #message.attach(part1)
        #message.attach(part2)

        #Gmail settings - ORWA.Tracker@gmail.com
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(MAIL_HOST, EMAIL_PORT, context = context) as server:
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(SERVER_EMAIL, Reminder, message.as_string())
            server.quit()
            print("Successfully sent email")

        #ORWA@Pneumatrol.com
        # with smtplib.SMTP(MAIL_HOST, EMAIL_PORT) as server:
        #     server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        #     server.sendmail(SERVER_EMAIL, to, message)
        #     server.quit()
        #     print("Successfully sent email")