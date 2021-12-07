from django.core.management.base import BaseCommand
from ORWAapp.models import SalesOrder
from django.contrib.auth.models import User
from django import template
from datetime import *
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings


class Command(BaseCommand):
    help = "Sends email reminder to users with outstanding ORWA's"

    def handle(self, *args, **kwargs):
        
        salesdata = SalesOrder.objects.filter(issue_date__isnull=True).filter(reject_date__isnull=True)
        userEmails = []
        for user in User.objects.all():
            userEmails.append(user.email)

        context = {
        'SalesOrder':salesdata,
        }

        subject ='Weekly ORWA list'
        sendfrom = settings.EMAIL_HOST_USER
        to = ['tomt@pneumatrol.com']

        #send_mail(subject,body,sendfrom,to,fail_silently=False,)
        
        text_content = 'see live.pneumatrol.com'
        html_content  = render_to_string('ORWAapp/home/EmailReminder.html', context)

        msg = EmailMultiAlternatives(subject, text_content, sendfrom, to)
        msg.attach_alternative(html_content, "text/html")
        #print(msg)
        msg.send()
