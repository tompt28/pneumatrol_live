from django.urls import path
from . import views

# SET THE NAMESPACE!
app_name = 'ORWAapp'

# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
    path('',views.home, name = "home"),
    path('/OpenOrders', views.OpenOrders, name = "OpenOrders"),
    path('/PartTypes', views.PartTypes, name = "PartTypes"),
    path('/Approve/', views.Approve, name = "Approve"),
    path('/Approve/<part>', views.ApprovePart, name='ApprovePart'),
    path('/AddParts/completed/<order>', views.DonePaperwork, name='DonePaperwork'),
    path('/Completed/', views.Completed, name = "Completed"),
    path('/AllParts/', views.AllParts, name='AllParts'),
    path('/NewORWA/', views.NewORWA,name = "NewORWA"),
    path('/NewCustomer/', views.NewCustomer, name = "NewCustomer"),
    path('/Customers/', views.Customer, name = "Customers"),
    path('/AddParts/<order>', views.AddParts, name = "AddParts"),
    path('/AddType/', views.AddType, name = "AddType"),
    path('/Orders/<order>', views.OrderDetail, name='OrderDetail'),
    path('/Reject/<order>', views.Reject, name='Reject'),
    path('/Parts/<part>', views.PartDetail, name='PartDetail'),
    path('/AddType/', views.AddType, name = "AddType"),
    path('/AllParts/', views.AllParts, name='AllParts'),
    path('/Allocate', views.Allocate, name='Allocate'),
    path('/Allocate/<order>', views.AllocateDetail, name='Allocatedetail'),
    path('/EmailReminder/',views.EmailReminder, name='EmailReminder'),
    path('/IssueEmail/<order>',views.IssueEmail,name='IssueEmail'),
    path('/RejectEmail/<order>',views.RejectEmail,name='RejectEmail'),
]
