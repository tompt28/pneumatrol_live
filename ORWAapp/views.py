from django.shortcuts import render, get_object_or_404
from ORWAapp.forms import *
from django.db.models import Q
from ORWAapp.models import Customers, SalesOrder, Parts, PartType, Employee
from django.http import Http404, HttpResponseRedirect,HttpResponse,FileResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User, Group
from django import template
import os
from datetime import *
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings
import smtplib, ssl, email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders
from os.path import basename

# Create your views here.
def index(request):
    return render(request,'ORWAapp/index.html')

@login_required
def user_logout(request):

    logout(request)
    return HttpResponseRedirect(reverse('index'))

def register(request):

    registered = False

    if request.method == "POST":
        user_form = UserForm(data = request.POST)
        profile_form = EmployeeForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            
            user = user_form.save()
            user.set_password(user.password)

            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'profile_pic' in request.FILES:
                profile.profile_pic = request.FILES['profile_pic']

            user_group = profile.Role
            set_group = Group.objects.get(name=user_group)
            set_group.user_set.add(user)

            profile.save()

            registered = True
        else:
            print(user_form.errors,profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = EmployeeForm()

    context = {'user_form':user_form,
            'profile_form':profile_form,
            'registered':registered,
            }

    return render(request,'ORWAapp/register.html',context)


def user_login(request):

    NoUser = False

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username = username, password = password)

        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse("HomeTopLevel"))
    
            else:
                return HttpResponse("Account not active")
        else:
            print("somebody tried to log in and failed")
            print("Username: {} and password {}".format(username,password))
            NoUser = True

    context = {
            'NoUser':NoUser
             }
    
    return render(request,"ORWAapp/login.html",context)

def HomeTopLevel(request):
    username = request.user.first_name
    
    user_group = request.user.groups.values_list('name',flat = True) # QuerySet Object
    user_group_as_list = list(user_group)   #QuerySet to `list`
    DEPT = user_group_as_list[0]
    if user_group_as_list[0] == "ENG":
        role_dict = {'ENG':"Welcome to the Engineering toolbox"}

    elif user_group_as_list[0] == "ENM":
        role_dict = {'ENM':"Welcome to the Engineering manager toolbox!"}

    elif user_group_as_list[0] == "SAL":
        role_dict = {'SAL':"Welcome to the Sales toolbox!"}

    elif user_group_as_list[0] == "SAM":
        role_dict = {'SAM':"Welcome to the Sales Manager toolbox!"}
    else:
        print("NO ROLE")


    context = {
        'username':username,
        'DEPT':DEPT
        }
    context = {**context, **role_dict}

    return render(request,'HomeTopLevel.html', context)

def home(request):

    username = request.user.first_name
    user_group = request.user.groups.values_list('name',flat = True) # QuerySet Object
    user_group_as_list = list(user_group)   #QuerySet to `list`

    if user_group_as_list[0] == "ENG":
        role_dict = {'ENG':"Welcome to the Engineering ORWA homepage"}

    elif user_group_as_list[0] == "ENM":
        role_dict = {'ENM':"Welcome to the Engineering manager ORWA homepage!"}

    elif user_group_as_list[0] == "SAL":
        role_dict = {'SAL':"Welcome to the Sales ORWA Homepage!"}

    elif user_group_as_list[0] == "SAM":
        role_dict = {'SAM':"Welcome to the Sales Manager ORWA homepage!"}
    else:
        print("NO ROLE")

    context = {'username':username}
    context = {**context, **role_dict}
    
    return render(request, 'ORWAapp/home.html', context)

def NewORWA(request):

    firstname = request.user.first_name
    posted = False

    context = {'insert_me': firstname}

    #Gmail settings
    # SERVER_EMAIL = 'ORWA.Tracker@gmail.com'
    # MAIL_HOST ="smtp.gmail.com"
    # EMAIL_HOST_USER = 'ORWA.Tracker@gmail.com'
    # EMAIL_HOST_PASSWORD = 'koayxjvqriwnltoq'
    # EMAIL_PORT = 465

    #ORWA@pneumatrol settings
    SERVER_EMAIL = 'orwa@pneumatrol.com'
    MAIL_HOST = "192.168.0.253"
    EMAIL_HOST_USER = 'orwa'
    EMAIL_HOST_PASSWORD = 'Connect667_'
    EMAIL_PORT = 25
    
    Engstaff = Employee.objects.filter(Role = 'ENG')
    EngMan = Employee.objects.filter(Role = 'ENM')
    
    NewORWAemails = []
    
    for user in Engstaff:
        finduser = User.objects.get(username = user)
        emailaddress = finduser.email
        NewORWAemails.append(emailaddress)

    for user in EngMan:
        findman = User.objects.get(username = user)
        emailaddress = findman.email
        NewORWAemails.append(emailaddress)

    if request.method == "POST":
        new_ORWA_form = NewORWAForm(request.POST, request.FILES)
        if new_ORWA_form.is_valid():
            ORWA = new_ORWA_form.save(commit = False)
            if 'paperwork' in request.FILES:
                ORWA.paperwork = request.FILES['paperwork']

            ORWA.entered_date = date.today()
            ORWA.save()
            posted = True

            salesdata = SalesOrder.objects.filter(order_number = ORWA.order_number)   

            contextdict = {
            'SalesOrder':salesdata,
            'insert_me':user,
            'posted':posted,
            }

            subject =['New ORWA', ORWA.order_number]
            text_content = 'see live.pneumatrol.com'
            html_content  = render_to_string('ORWAapp/home/EmailReminder.html', contextdict)
            
            #create message
            message = MIMEMultipart()
            #add parts to message
            message["From"] = SERVER_EMAIL
            message["To"] =  ', '.join(NewORWAemails)
            message["Subject"] = ', '.join(subject)


            filename = os.path.join(settings.MEDIA_ROOT, str(salesdata[0].paperwork))

            with open(filename, 'rb') as f:
                part = MIMEApplication(f.read(), Name=basename(filename))

                part['Content-Disposition'] = 'attachment; filename="{}"'.format(basename(filename))
                message.attach(part)

            #add body options
            part2 = MIMEText(html_content, "html")

            # Add HTML/plain-text parts to MIMEMultipart message
            message.attach(part2)

            #Gmail settings - ORWA.Tracker@gmail.com

            # context = ssl.create_default_context()
            # with smtplib.SMTP_SSL(MAIL_HOST, EMAIL_PORT, context = context) as server:
            #     server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            #     server.sendmail(SERVER_EMAIL, NewORWAemails, message.as_string())
            #     server.quit()
            #     print("Successfully sent email")

            #ORWA@Pneumatrol.com
            with smtplib.SMTP(MAIL_HOST, EMAIL_PORT) as server:
                server.sendmail(SERVER_EMAIL, NewORWAemails, message.as_string())
                server.quit()
                print("Successfully sent email")


        else:
            return render(request,'ORWAapp/home/Error.html', context)
            print(new_ORWA_form.errors)
            posted = False

             

    context = {
        'NewORWAForm':NewORWAForm,
        'insert_me':firstname,
        'posted':posted,
        }

    return render(request,'ORWAapp/home/NewORWA.html',context)


def Customer(request):
    user = request.user.first_name
    data = Customers.objects.all()
    context = {
        'Customers':data,
        'insert_me':user,
        }
    return render(request,'ORWAapp/home/Customers.html',context)


def NewCustomer(request):
    user = request.user.first_name
    added = False
    context = {
        'insert_me':user,
        }
    if request.method == "POST":
        new_Customer_form = NewCustomerForm(data = request.POST)

        if new_Customer_form.is_valid():
            new = new_Customer_form.save(commit = False)
            new.added_by = user
            new.save()

            added = True
            print("added")

        else:
            print(new_Customer_form.errors)
    else:
        print(new_Customer_form.errors)
        return render(request,'ORWAapp/home/Error.html', context)
    
    context = {
        'NewCustomerForm':NewCustomerForm,
        'insert_me':user,
        'added':added,
        }

    return render(request,'ORWAapp/home/NewCustomer.html',context)


def PartTypes(request):
    user = request.user.first_name
    data = PartType.objects.all()
    context = {
        'insert_me':user,
        'Parts':data,
        }
    return render(request,'ORWAapp/home/PartTypes.html',context)


def Completed(request):
    user = request.user.first_name
    reject_data = SalesOrder.objects.filter(reject_user__isnull = False)
    issue_data = SalesOrder.objects.filter(issue_date__isnull = False)   

    context = {
        #'data' : data,
        'reject_data':reject_data,
        'issue_data':issue_data,
        'insert_me':user,
        }
    return render(request,'ORWAapp/home/Completed.html',context)


def Approve(request):
    user = request.user.first_name
    
    partdata = Parts.objects.filter(
        approved_date__isnull=True
        )

    context = {
    'Parts':partdata,
    'insert_me':user,
    }
    return render(request,'ORWAapp/home/Approve.html',context)

def ApprovePart(request, part):

    user = request.user.first_name
    pd = Parts.objects.get(part_code = part)
    so = pd.sales_order
    SO = SalesOrder.objects.filter( order_number = so )
    salesorder = SO[0]
    partdata = Parts.objects.filter(sales_order = so)
    partadded = len(partdata)
    lines = so.ORWA_lines
    print("ORWA lines:", lines)
    print("Part lines:", partadded)
    approvecount = Parts.objects.filter(sales_order = so).filter(approved_by__isnull = True).count()
    print("Part lines to approve:", approvecount)

    added = False
    issued = False

    my_form = ApprovePartForm(instance = pd)

    if request.method == "POST":
        
        approve_part_form = ApprovePartForm(data = request.POST, instance = pd)

        if approve_part_form.is_valid():

            new = ApprovePartForm(data = request.POST, instance = pd)
            new = approve_part_form.save(commit = False)
            new.approved_date = date.today()
            new.approved_by = request.user
            new.save()

            added = True
            print("added")

            approvecount -= 1 
            
            if approvecount == 0 and lines == partadded:
                so.issue_date = date.today()
                so.save()
                print("ORWA Issued")
                issued = True
            else:
                pass
                  
    context = {
    'insert_me':user,
    'salesorder':salesorder,
    'issued': issued,
    'my_form':my_form,
    'pd':pd,
    'added':added,
    }
    return render(request,'ORWAapp/home/ApprovePart.html',context)


def Allocate(request):
    user = request.user.first_name
    AT = SalesOrder.objects.filter(issue_date__isnull = True).filter(allocated_to__isnull = True)
    print()
    context = {
    'AT':AT,
    'insert_me':user,
    }
    return render(request,'ORWAapp/home/Allocate.html',context)

def AllocateDetail(request, order):

    od = SalesOrder.objects.get(order_number = order)    
    user = request.user.first_name
    Allocated = False

    if request.method == "POST":
        allocate_form  = AllocatedToForm(data = request.POST, instance = od)

        if allocate_form.is_valid():
            new = allocate_form.save(commit = False)
            new.save()
            Allocated = True
            print("added")
            return HttpResponseRedirect(reverse("ORWAapp:Allocate"))
        else:
            print(allocate_form.errors)
            
    else:
        allocate_form = AllocatedToForm()

    context = {
    'od':od,
    'AllocatedToForm':AllocatedToForm,
    'Allocated':Allocated,
    'insert_me':user,
    }
    return render(request,'ORWAapp/home/Allocatedetail.html',context)


def OpenOrders(request):

    user = request.user.first_name
    noORWA = False
    
    salesdata = SalesOrder.objects.filter(issue_date__isnull=True).filter(reject_date__isnull=True)
    if not salesdata:
        noORWA = True
    
    context = {
    'noORWA': noORWA,
    'SalesOrder':salesdata,
    'insert_me':user,
    }

    return render(request,'ORWAapp/home/OpenOrders.html',context)

def OrderDetail(request, order):
 
    user = request.user.first_name
    user_group = request.user.groups.values_list('name',flat = True) # QuerySet Object
    user_group_as_list = list(user_group)   #QuerySet to `list`
    DEPT = user_group_as_list[0]
    alladd = False   
    edit = False
    issued = False
    comppaperwork = False


    if DEPT == "ENG" or DEPT == "ENM":
        edit = True

    od = SalesOrder.objects.get(order_number = order)
    pd = Parts.objects.filter(sales_order = od)
    partadded = len(pd)

    if od.issue_date:
        issued = True

    if od.completed_paperwork:
        comppaperwork = True

    lines = od.ORWA_lines
    print("ORWA lines:", lines)
    print("Part lines:", partadded)
    approvecount = Parts.objects.filter(sales_order = od).filter(approved_by__isnull = True)
    print("Part lines to approve:", len(approvecount))

    if lines == partadded:
        alladd = True

    context = {
    'issued':issued,
    'alladd':alladd,
    'insert_me':user,
    'comppaperwork':comppaperwork,
    'od': od,
    'pd':pd,
    'edit': edit,
    }
    return render(request, 'ORWAapp/home/OrderDetail.html', context)

def AddParts(request, order):
    
    added = False
    existing = False
    alladd = False
    user = request.user.first_name
    od = SalesOrder.objects.get(order_number = order)
    pd = Parts.objects.filter(sales_order = od)
    partadded = len(pd)
    lines = od.ORWA_lines
    print("ORWA lines:", lines)
    print("Part lines:", partadded)
    approvecount = Parts.objects.filter(sales_order = od).filter(approved_by__isnull = True)
    print("Part lines to approve:", len(approvecount))

   
    pf = Parts(sales_order = od)

    if request.method == "POST":
        add_part_form = AddPartForm(data = request.POST, instance=pf)  

        if add_part_form.is_valid():
            new = add_part_form.save(commit = False)
            new.sales_order = od
            new.completed_by = request.user
            new.save()

            added = True
            print("added")

            pd = Parts.objects.filter(sales_order = od)
            partadded = len(pd)
            lines = od.ORWA_lines
            print("ORWA lines:", lines)
            print("Part lines:", partadded)
            
            if lines == partadded:
                alladd = True 

        else:
            print(add_part_form.errors)
            existing = True
    else:
        add_part_form = AddPartForm(request.POST, instance=pf)

    context = {
    'alladd':alladd,
    'insert_me' : user,
    'order' : order,
    'AddPartForm' : AddPartForm,
    'added' : added,
    'existing' : existing,
    }
    return render(request,'ORWAapp/home/AddParts.html',context)


def AddType(request):
    user = request.user.first_name
    added = False

    if request.method == "POST":
        add_type_form = NewTypeForm(data = request.POST)

        if add_type_form.is_valid():
            new = add_type_form.save(commit = False)
            new.save()

            added = True
            print("added")

        else:
            print(add_type_form.errors)

    context = {
    'insert_me':user,
    'NewTypeForm':NewTypeForm,
    'added':added,
    }
    return render(request,'ORWAapp/home/AddType.html',context)

def PartDetail(request, part):
    p = Parts.objects.get(part_code = part)
    SO = SalesOrder.objects.get(order_number = p.sales_order)
    
    context = {
    'p': p,
    'SO': SO
    }
    return render(request, 'ORWAapp/home/PartDetail.html', context)

def AllParts(request):
    user = request.user.first_name
    ap = Parts.objects.all()
    context = {
    'insert_me':user,
    'ap': ap,
    }
    return render(request, 'ORWAapp/home/AllParts.html', context)


def DonePaperwork(request, order):

    od = SalesOrder.objects.get(order_number = order)
    user = request.user.first_name
    added = False

    if request.method == "POST":
        form  = CompletedPaperworkForm(request.POST, request.FILES, instance = a)

        if form.is_valid():
            new = form.save(commit = False)
            new.save()

            added = True
            print("added")

        else:
            print(CompletedPaperworkForm.errors)
            
    else:
        form = CompletedPaperworkForm(instance = a)

    context = {
    'order':order,
    'od':od,
    'CompletedPaperworkForm':CompletedPaperworkForm,
    'added':added,
    'insert_me':user,
    }
    return render(request,'ORWAapp/home/DonePaperwork.html',context)


def Reject(request, order):

    
    od = SalesOrder.objects.get(order_number = order)
    print(od)
    info = SalesOrder.objects.get(pk=od.id)
    print(info.id)
    od = get_object_or_404(SalesOrder, pk=info.id)
    user = request.user.first_name
    added = False

    if request.method == "POST":

        reject_form = RejectForm(data = request.POST, instance = od)

        if reject_form.is_valid():

            new = reject_form.save(commit = False)
            new.reject_user = request.user
            new.save()
            added = True
            print("Rejected")

        else:
            print(reject_form.errors)
    else:
        reject_form= RejectForm()

    context = {
    'RejectForm':RejectForm,
    'info':info,
    'insert_me':user,
    'od': od,
    'added':added,
    }
    return render(request, 'ORWAapp/home/Rejection.html', context)


def EmailReminder(request):

    salesdata = SalesOrder.objects.filter(issue_date__isnull=True).filter(reject_date__isnull=True)
    
    context = {
    'SalesOrder':salesdata,
    }

    return render(request,'ORWAapp/home/EmailReminder.html',context)

def IssueEmail(request, order):

    # gmail setttings 
    # SERVER_EMAIL = 'ORWA.Tracker@gmail.com'
    # MAIL_HOST ="smtp.gmail.com"
    # EMAIL_HOST_USER = 'ORWA.Tracker@gmail.com'
    # EMAIL_HOST_PASSWORD = 'koayxjvqriwnltoq'
    # EMAIL_PORT = 465

    #ORWA@pneumatrol settings
    SERVER_EMAIL = 'orwa@pneumatrol.com'
    MAIL_HOST = "192.168.0.253"
    EMAIL_PORT = 25

    salesdata = SalesOrder.objects.get(order_number = order)   
    sendreminder = Employee.objects.filter(IssueEmails = True)

    issueEmails = []
    
    for user in sendreminder:
        finduser = User.objects.get(username = user)
        emailaddress = finduser.email
        issueEmails.append(emailaddress)

    contextdict = {
    'salesdata':salesdata,
    }

    subject =['Issued ORWA', order]
    text_content = 'see live.pneumatrol.com'
    html_content  = render_to_string('ORWAapp/home/IssueEmail.html', contextdict)
    
    #create message
    message = MIMEMultipart()
    #add parts to message
    message["From"] = SERVER_EMAIL
    message["To"] =  ', '.join(issueEmails)
    message["Subject"] = ', '.join(subject)


    filename = os.path.join(settings.MEDIA_ROOT, str(salesdata.completed_paperwork))

    with open(filename, 'rb') as f:
        part = MIMEApplication(f.read(), Name=basename(filename))

        part['Content-Disposition'] = 'attachment; filename="{}"'.format(basename(filename))
        message.attach(part)

    #add body options
    part2 = MIMEText(html_content, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part2)

    # Gmail settings - ORWA.Tracker@gmail.com
    # context = ssl.create_default_context()
    # with smtplib.SMTP_SSL(MAIL_HOST, EMAIL_PORT, context = context) as server:
    #     server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
    #     server.sendmail(SERVER_EMAIL, issueEmails, message.as_string())
    #     server.quit()
    #     print("Successfully sent email") 

    #ORWA@Pneumatrol.com
    with smtplib.SMTP(MAIL_HOST, EMAIL_PORT) as server:
        server.sendmail(SERVER_EMAIL, issueEmails, message.as_string())
        server.quit()
        print("Successfully sent email")

    return HttpResponseRedirect(reverse('ORWAapp:home'))


@login_required
def searchResults(request):
   
    user = request.user.first_name

    if request.method == 'GET':
       SI = request.GET.get('search_input')
       print(SI) 

    if not SI:
        return HttpResponseRedirect(reverse('home'))
    else:
   
        ONresults = SalesOrder.objects.filter(order_number__icontains = SI)
        print(ONresults)
        if not ONresults:
            ONresults = None

        PCresults = Parts.objects.filter(part_code__icontains = SI)        
        print(PCresults)
        if not PCresults:
            PCresults = None

        SOno = Parts.objects.filter(sales_order__order_number__contains = SI)
        print(SOno)
        if not SOno:
            SOno = None

    context = {'insert_me':user,
    'SI':SI,
    'SOno':SOno,
    'ONresults': ONresults,
    'PCresults':PCresults,
    'SOno':SOno,
    }

    return render(request, 'ORWAapp/search.html', context)