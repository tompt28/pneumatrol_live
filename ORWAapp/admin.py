from django.contrib import admin
from .models import Employee, User, SalesOrder, Customers,PartType,Parts

# Register your models here.
admin.site.register(Employee)
admin.site.register(SalesOrder)
admin.site.register(Customers)
admin.site.register(PartType)
admin.site.register(Parts)