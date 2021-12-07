from django.shortcuts import render, get_object_or_404
from ORWAapp.forms import *
from django.db.models import Q
from ORWAapp.models import Customers, SalesOrder, Parts, PartType
from django.http import Http404, HttpResponseRedirect,HttpResponse,FileResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User, Group
from django import template
from datetime import *
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings

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
    username = request.user.username
    
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

    username = request.user.username
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

    user = request.user.username
 
    posted = False

    if request.method == "POST":
        new_ORWA_form = NewORWAForm(request.POST, request.FILES)
        if new_ORWA_form.is_valid():
            ORWA = new_ORWA_form.save(commit = False)
            if 'paperwork' in request.FILES:
                ORWA.paperwork = request.FILES['paperwork']

            ORWA.entered_date = date.today()
            ORWA.save()
            posted = True
        else:
            return HttpResponse("invalid details supplied")
            print(new_ORWA_form.errors)
            posted = False

    context = {
        'NewORWAForm':NewORWAForm,
        'insert_me':user,
        'posted':posted,
        }

    return render(request,'ORWAapp/home/NewORWA.html',context)


def Customer(request):
    user = request.user.username
    data = Customers.objects.all()
    context = {
        'Customers':data,
        'insert_me':user,
        }
    return render(request,'ORWAapp/home/Customers.html',context)


def NewCustomer(request):
    user = request.user.username
    added = False

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
        new_Customer_form = NewCustomerForm()
    
    context = {
        'NewCustomerForm':NewCustomerForm,
        'insert_me':user,
        'added':added,
        }

    return render(request,'ORWAapp/home/NewCustomer.html',context)


def PartTypes(request):
    user = request.user.username
    data = PartType.objects.all()
    context = {
        'insert_me':user,
        'Parts':data,
        }
    return render(request,'ORWAapp/home/PartTypes.html',context)


def Completed(request):
    user = request.user.username
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
    user = request.user.username
    
    partdata = Parts.objects.filter(
        approved_date__isnull=True
        )

    context = {
    'Parts':partdata,
    'insert_me':user,
    }
    return render(request,'ORWAapp/home/Approve.html',context)

def ApprovePart(request, part):
    user = request.user.username
    pd = Parts.objects.get(part_code = part)
    so = pd.sales_order
    SO = SalesOrder.objects.filter( order_number = so )
    salesorder = SO[0]
    # lines = so.ORWA_lines
    # approvecount = [Parts.objects.filter(sales_order = so).filter(approved_by__isnull = True)]
    # print("ORWA lines:", lines)
    # print(len(approvecount))
    # print("Part lines to approve:", approvecount) 
    # #od = SalesOrder.objects.get(order_number = order)
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
    user = request.user.username
    AT = SalesOrder.objects.filter(issue_date__isnull = True).filter(allocated_to__isnull = True)
    print()
    context = {
    'AT':AT,
    'insert_me':user,
    }
    return render(request,'ORWAapp/home/Allocate.html',context)

def AllocateDetail(request, order):

    od = SalesOrder.objects.get(order_number = order)    
    user = request.user.username
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

    user = request.user.username
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
 
    user = request.user.username
    user_group = request.user.groups.values_list('name',flat = True) # QuerySet Object
    user_group_as_list = list(user_group)   #QuerySet to `list`
    DEPT = user_group_as_list[0]
    alladd = False   
    edit = False

    if DEPT == "ENG" or DEPT == "ENM":
        edit = True

    od = SalesOrder.objects.get(order_number = order)
    pd = Parts.objects.filter(sales_order = od)
    partadded = len(pd)
    
    lines = od.ORWA_lines
    print("ORWA lines:", lines)
    print("Part lines:", partadded)
    approvecount = Parts.objects.filter(sales_order = od).filter(approved_by__isnull = True)
    print("Part lines to approve:", len(approvecount))

    if lines == partadded:
        alladd = True

    context = {
    'alladd':alladd,
    'insert_me':user,
    'od': od,
    'pd':pd,
    'edit': edit,
    }
    return render(request, 'ORWAapp/home/OrderDetail.html', context)

def AddParts(request, order):
    
    added = False
    existing = False
    alladd = False
    user = request.user.username
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
    user = request.user.username
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
    user = request.user.username
    ap = Parts.objects.all()
    context = {
    'insert_me':user,
    'ap': ap,
    }
    return render(request, 'ORWAapp/home/AllParts.html', context)


def DonePaperwork(request, order):

    od = SalesOrder.objects.get(order_number = order)
    orderid = od.pk
    print(orderid)   
    user = request.user.username
    added = False
    a = get_object_or_404(SalesOrder,pk=od.id)
    print(a)

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
    user = request.user.username
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

    return render(request,'ORWAapp/home/EmailReminder.html',context)

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

@login_required
def searchResults(request):
   
    user = request.user.username

    
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