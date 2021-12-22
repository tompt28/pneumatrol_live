#!/venv_django/bin/python3

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
        
        # SERVER_EMAIL = 'ORWA.Tracker@gmail.com'
        # MAIL_HOST ="smtp.gmail.com"
        # EMAIL_HOST_USER = 'ORWA.Tracker@gmail.com'
        # EMAIL_HOST_PASSWORD = 'koayxjvqriwnltoq'
        # EMAIL_PORT = 465

        SERVER_EMAIL = 'orwa@pneumatrol.com'
        MAIL_HOST = "192.168.0.253"
        EMAIL_PORT = 25
        
        salesdata = SalesOrder.objects.filter(issue_date__isnull=True).filter(reject_date__isnull=True)

        contextdict = {
        'SalesOrder':salesdata,
        }

        subject ='Weekly ORWA report'
        
        Report = []

        sendreminder = Employee.objects.filter(SMT = True)
        
        for user in sendreminder:
            finduser = User.objects.get(username = user)
            emailaddress = finduser.email
            Report.append(emailaddress)

        text_content = 'see live.pneumatrol.com'
        html_content  = render_to_string('ORWAapp/home/WeeklyReportEmail.html', contextdict)
        
        #create message
        message = MIMEMultipart()
        #add parts to message
        message["From"] = SERVER_EMAIL
        message["To"] =  ', '.join(Report)
        message["Subject"] = subject
        message.preamble = 'ORWA Report'

        #add body options
        part2 = MIMEText(html_content, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part2)

        #ORWA@Pneumatrol.com
        with smtplib.SMTP(MAIL_HOST, EMAIL_PORT) as server:
            #server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(SERVER_EMAIL, Report, message.as_string())
            server.quit()
            print("Successfully sent email")
