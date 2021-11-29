from django.urls import path
from . import views

# SET THE NAMESPACE!
app_name = 'ORWAapp'

# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
    path('home/',views.home, name = "home"),
    path('home/OpenOrders/', views.OpenOrders, name = "OpenOrders"),
    path('home/PartTypes/', views.PartTypes, name = "PartTypes"),
    path('home/Approve/', views.Approve, name = "Approve"),
    path('home/Completed/', views.Completed, name = "Completed"),
    path('home/AllParts/', views.AllParts, name='AllParts'),
    path('home/NewORWA/', views.NewORWA,name = "NewORWA"),
    path('home/NewCustomer/', views.NewCustomer, name = "NewCustomer"),
    path('home/Customers/', views.Customer, name = "Customers"),
    path('home/AddParts/', views.AddParts, name = "AddParts"),
    path('home/AddType/', views.AddType, name = "AddType"),
    path('home/orders/<int:Order_id>/', views.OrderDetail, name='OrderDetail'),
    path('home/reject/<int:reject_id>/', views.Reject, name='Reject'),
    path('home/parts/<int:Part_id>/', views.PartDetail, name='PartDetail'),
    path('home/AddType/', views.AddType, name = "AddType"),
    path('home/AllParts/', views.AllParts, name='AllParts'),
    path('home/Approve/<int:Approve_id>', views.ApprovePart, name='ApprovePart'),
    path('home/Allocate', views.Allocate, name='Allocate'),
    path('home/Allocate/<int:Allocate_id>', views.AllocateDetail, name='Allocatedetail'),
    path('Search/',views.searchResults, name = "searchResults")

]
