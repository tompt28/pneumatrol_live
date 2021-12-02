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

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username = username, password = password)

        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse("ORWAapp:home"))
    
            else:
                return HttpResponse("Account not active")
        else:
            print("somebody tried to log in and failed")
            print("Username: {} and password {}".format(username,password))
            return HttpResponse("invalid login details supplied")
    else:
        return render(request,"ORWAapp/login.html",{})

def home(request):
    user_group = request.user.groups.values_list('name',flat = True) # QuerySet Object
    user_group_as_list = list(user_group)   #QuerySet to `list`

    if user_group_as_list[0] == "ENG":
        role_dict = {'ENG':"Welcome to the Engineering homepage!"}

    elif user_group_as_list[0] == "ENM":
        role_dict = {'ENM':"Welcome to the Engineering manager homepage!"}

    elif user_group_as_list[0] == "SAL":
        role_dict = {'SAL':"Welcome to the Sales Homepage!"}

    elif user_group_as_list[0] == "SAM":
        role_dict = {'SAM':"Welcome to the Sales Manager homepage!"}
    else:
        print("NO ROLE")

    return render(request, 'ORWAapp/home.html', context = role_dict)

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

def Add_Without(request):
    user = request.user.username

    posted = False

    if request.method == "POST":
        NoSO = NoSO_Form(request.POST)
        if NoSO.is_valid():
            NoSO = NoSO.save(commit = False)
            posted = True
            NoSO.save()
        
        else:
            print(NoSO.errors)
    else:   
        NoSO = NoSO_Form()

    context = {
        'NoSO_Form':NoSO_Form,
        'insert_me':user,
        'posted':posted,
        }
    return render(request,'ORWAapp/home/AddWithout.html',context)

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


def Customer(request):
    user = request.user.username
    data = Customers.objects.all()
    context = {
        'Customers':data,
        'insert_me':user,
        }
    return render(request,'ORWAapp/home/Customers.html',context)


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


def Allocate(request):
    user = request.user.username
    AT = SalesOrder.objects.filter(issue_date__isnull = True).filter(allocated_to__isnull = True)
    print()
    context = {
    'AT':AT,
    'insert_me':user,
    }
    return render(request,'ORWAapp/home/Allocate.html',context)

def OpenOrders(request):
    user = request.user.username
    salesdata = SalesOrder.objects.filter(issue_date__isnull=True).filter(reject_date__isnull=True)
    context = {
    'SalesOrder':salesdata,
    'insert_me':user,
    }
    return render(request,'ORWAapp/home/OpenOrders.html',context)


def AddParts(request, order):
    added = False
    existing = False
    active = False
    user = request.user.username
    OrderDetail = SalesOrder.objects.get(order_number = order)
    print(request.user)
    
    pf = Parts(sales_order = OrderDetail)

    if request.method == "POST":
        add_part_form = AddPartForm(data = request.POST, instance=pf)  

        if add_part_form.is_valid():
            new = add_part_form.save(commit = False)
            new.sales_order = OrderDetail
            new.completed_by = request.user
            new.save()

            added = True
            print("added")

        else:
            print(add_part_form.errors)
            existing = True
    else:
        add_part_form = AddPartForm(request.POST, instance=pf)

    context = {
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


def ApprovePart(request, part):
    user = request.user.username
    pd = Parts.objects.get(part_code = part)
    so = pd.sales_order
    
    SO = SalesOrder.objects.filter( order_number = so )
    lines = so.ORWA_lines
    print("ORWA lines:", lines)

    approvecount = len([Parts.objects.filter(sales_order = so).filter(approved_by__isnull = True)])
    print("Part lines to approve:", approvecount) 

    added = False
    completed = False

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
            print(approvecount)
            if approvecount == 0:

                so.issue_date = date.today()
                so.save()
                print("ORWA Issued")
                   

    context = {
    'insert_me':user,
    'my_form':my_form,
    'pd':pd,
    'added':added,
    }
    return render(request,'ORWAapp/home/ApprovePart.html',context)

def PartDetail(request, part):
    p = Parts.objects.get(part_code = part)
    context = {
    'p': p
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

def OrderDetail(request, order):   

    od = SalesOrder.objects.get(order_number = order)
    pd = Parts.objects.filter(sales_order = od)


    user = request.user.username

    context = {
    'insert_me':user,
    'od': od,
    'pd':pd
    }
    return render(request, 'ORWAapp/home/OrderDetail.html', context)

def Reject(request, reject):
    od = SalesOrder.objects.get(order_number = reject)
    print(od)
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

    context = {
    'RejectForm':RejectForm,
    'insert_me':user,
    'od': od,
    'added':added,
    }
    return render(request, 'ORWAapp/home/Rejection.html', context)

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