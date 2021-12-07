from django.shortcuts import render, get_object_or_404
from ORWAapp.models import Customers, SalesOrder, Parts, PartType
from django.http import Http404, HttpResponseRedirect,HttpResponse,FileResponse
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django import template
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings

def EmailReminder(request):

    salesdata = SalesOrder.objects.filter(issue_date__isnull=True).filter(reject_date__isnull=True)
    userEmails = []
    for user in User.objects.all():
        userEmails.append(user.email)

    context = {
    'SalesOrder':salesdata,
    }

    subject ='Weekly ORWA list'
    sendfrom = settings.EMAIL_HOST_USER
    to = userEmails

    #send_mail(subject,body,sendfrom,to,fail_silently=False,)
    
    text_content = 'see live.pneumatrol.com'
    html_content  = render_to_string('ORWAapp/home/EmailReminder.html', context)

    msg = EmailMultiAlternatives(subject, text_content, sendfrom, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    return HttpResponseRedirect(reverse('ORWAapp:home'))
    #return render(request,'ORWAapp/home/EmailReminder.html',context)

def IssueEmail(request, order):

    salesdata = SalesOrder.objects.get(order_number = order)
    
    userEmails = []
    for user in User.objects.all():
        userEmails.append(user.email)
    
    context = {
    'salesdata':salesdata,
    }

    subject ="Issued ORWA :",order
    sendfrom = settings.EMAIL_HOST_USER
    

    #send_mail(subject,body,sendfrom,to,fail_silently=False,)
    
    text_content = 'Order issued. See pneumatrol live to view'
    html_content  = render_to_string('ORWAapp/home/IssueEmail.html', context)

    msg = EmailMultiAlternatives(subject, text_content, sendfrom, userEmails)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    return HttpResponseRedirect(reverse('ORWAapp:home'))
    #return render(request,'ORWAapp/home/IssueEmail.html',context)

if __name__ == '__main__':
    EmailReminder(request)