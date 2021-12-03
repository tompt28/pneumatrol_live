from django.db import models
from django import template
from django.contrib.auth.models import User, Group
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.validators import MaxValueValidator
import os

# Create your models here.

register = template.Library()

def update_filename(instance, filename):
	ext = filename.split('.')[-1]
	path = "sales_orders/"
	filename = "%s.%s" % (instance.order_number, ext)

	return os.path.join(path,filename)

def update_filename_complete(instance, filename):
	ext = filename.split('.')[-1]
	path = "completed_orders/"
	filename = "%s-done.%s" % (instance.order_number, ext)

	return os.path.join(path,filename)


class Employee(models.Model):

	user = models.OneToOneField(
		User, 
		on_delete = models.CASCADE,
		)
	 # ADDITIONAL
	
	Sales = 'SAL'
	Engineering = 'ENG'
	EngineeringManager = 'ENM'
	SalesManager ='SAM'

	Role = [
		(Engineering, 'Engineering'),
		(Sales, 'Sales'),
		(EngineeringManager, 'Enginering Manager'),
		(SalesManager, 'Sales Manager'),
	]
	Role = models.CharField(
	max_length=3,
	choices=Role,
	)

	Profile_pic = models.ImageField(
		upload_to = 'profile_pics/', 
		blank = True,
		)

	def __str__(self):
		return self.user.username


class Customers(models.Model):
	full_name = models.CharField(max_length=200,
								help_text='Customer Name',
								)
	account_name = models.CharField(max_length=6,
								unique=True,
								help_text='Account ref',
								)
	short_name = models.CharField(max_length=50,
								blank=True,
								null=True,
								)

	def __str__(self):
		return "%s: %s" % (self.account_name, self.short_name)

	class Meta:	
		verbose_name_plural = "Customer"


class SalesOrder(models.Model):

	#futuredate = datetime.now() + timedelta(days=7)
	
	#additional
	order_number = models.CharField(max_length = 8, unique = True)
	customer = models.ForeignKey(Customers,
									on_delete = models.CASCADE,
									)
	entered_date = models.DateField(null = True, blank = True)
	order_date = models.DateField(help_text = "date on the paperwork")
	issue_date = models.DateField(null = True, blank = True)
	ORWA_lines = models.IntegerField(null = False, help_text= "number of lines that are an ORWA")
	reject_user = models.ForeignKey(User, 
									on_delete = models.CASCADE,
									related_name='rejected_by',
									null=True,
									blank=True,

									)
	reject_date = models.DateField(null = True, blank = True)
	reject_note = models.TextField(max_length = 200,
								 	blank = True,
								 	)
	notes = models.TextField(blank = True)
	paperwork = models.FileField(upload_to = update_filename, 
									blank = False,
									)
	completed_paperwork = models.FileField(upload_to = update_filename_complete, 
									blank = True,
									)
	allocated_to = models.ForeignKey(User,
									on_delete = models.CASCADE,
									null = True,
									blank = True,
									)

	class Meta:	
		verbose_name_plural = "SalesOrders"

	def __str__(self):
	    return self.order_number

	

class PartType(models.Model):
	# This could be done as hardcoded list, but the aim was to leave this as
	# user-editable as possible
	name = models.CharField(max_length=20, unique=True)
	description = models.TextField(max_length=200, help_text="200 character max")

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = "Part Types"

class Parts(models.Model):
	# These are the standard fields common to all the new order processing
	part_code = models.CharField(max_length=22, unique=True)
	part_type = models.ForeignKey(PartType, on_delete=models.CASCADE)
	sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='salesorder')
	updated_code = models.BooleanField(default=False)
	start_date = models.DateField()
	completed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completedby', null=False, blank=True)
	completed_date = models.DateField(auto_now_add = True)
	approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approvedby', null=True, blank=True)
	approved_date = models.DateField(null=True, blank=True)
	problem_parts = models.BooleanField(default=False, verbose_name ="Problem parts checked")
	problem_parts_cleared = models.BooleanField(default = False)
	notes = models.TextField(blank=True)
	SMALL = 'S'
	MEDIUM = "M"
	LARGE = "L"
	HUGE = "H"
	SIZE_CHOICES = [
	    (SMALL, 'Small'),
	    (MEDIUM, 'Medium'),
	    (LARGE, 'Large'),
	    (HUGE, 'Huge'),
	]
	size = models.CharField(max_length=1, choices=SIZE_CHOICES, null = False)

	def __str__(self):
		return self.part_code

	class Meta:	
		verbose_name_plural = "Parts"

