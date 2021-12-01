from django import forms
from django.contrib.auth.models import User
from django.core.validators import EmailValidator,ValidationError
from ORWAapp.models import Employee, SalesOrder, Customers, Parts, PartType
from datetime import *
from functools import partial

DateInput = partial(forms.DateInput, {'class': 'datepicker'})

class UserForm(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput(), required=True)
    Confirm_Password = forms.CharField(widget = forms.PasswordInput(), required=True,)
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'placeholder': '@pneumatrol.com'}))
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    
    class Meta():
        model = User
        fields = ('username','first_name','last_name', 'email', 'password')


    def clean_email(self):
        email_field = self.cleaned_data['email'].lower()
        domain = email_field.split('@')[1]
        domain_list = ["pneumatrol.com", "rosscontrols.com"]
        if domain not in domain_list:
            raise forms.ValidationError("Please enter an Email Address with a valid Pneumatrol or ross domain")
        return email_field

    def clean_password2(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('Confirm_Password')

        if not password2:
            raise forms.ValidationError("You must confirm your password")
        if password1 != password2:
            raise forms.ValidationError("Your passwords do not match")

class EmployeeForm(forms.ModelForm):
    
    class Meta():
        model = Employee
        fields = ("Role","Profile_pic")

class DateInput(forms.DateInput):
    input_type = 'date'

class NewORWAForm(forms.ModelForm):
    
    class Meta():
        model = SalesOrder
        fields ='__all__'
        exclude = ['issue_date',
                'reject_user',
                'reject_date',
                'reject_note',
                'entered_date',
                'allocated_to',
                ]
        widgets = {
                'order_date':DateInput(),
                }
    
    def clean_date(self):
        all_clean_data = super().clean()
        date1 = datetime.now()
        date2 = all_clean_data['order_date']

        if date2 > date1:
             raise forms.ValidationError("The cant be in the future")
    
    def clean_order(self):
        data = self.cleaned_data['order_number']
        data = data.upper()
        print(data)
        return data

        


class NoSO_Form(forms.ModelForm):

    
    class Meta():
        model = Parts
        fields ='__all__'
        exclude = ['sales_order',
                    'updated_code',
                    'approved_by',
                    'completed_date',
                    'approved_date',
                    'problem_parts'
                    ]
        widgets = {
                'start_date':DateInput(),
                'completed_date':DateInput(),
                }
    
    def clean_CD(self):
        cd = self.cleaned_data.get('completed_date',False)
        if not self.instance.completed_date == False:
            cd = datetime.now()
        return cd 



class NewCustomerForm(forms.ModelForm):

    class Meta():
        model = Customers
        fields = '__all__'
        
    def clean_Name(self):
        customer = self.cleaned_data.get('account_name')
        
        if customer:
            raise forms.ValidationError("This customer code already Exists!")
        return customer

class NewTypeForm(forms.ModelForm):

    class Meta():
        model = PartType
        fields = '__all__'
        
    def clean_Name(self):
        customer = self.cleaned_data.get('name')
        
        if customer:
            raise forms.ValidationError("This Part type already exists!")
        return customer

class AddPartForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AddPartForm, self).__init__(*args, **kwargs)
        # Making location required
        self.fields['problem_parts'].required = True
    
    class Meta():
        model = Parts
        fields =['part_code',
                'part_type',
                'updated_code',
                'start_date',
                'problem_parts',
                'size',
                'notes']
        widgets = {
                'start_date':DateInput(),
                }

    def clean_part(self):
        return self.cleaned_data['part_code'].upper()

    def clean_date(self):
        date1 = datetime.now()
        print(date1)
        date2 = self.cleaned_data['start_date']
        print(date2)
        if date2>date1:
             raise forms.ValidationError("The date can't be in the future!")
        return date2


class ApprovePartForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ApprovePartForm, self).__init__(*args, **kwargs)
        # Making location required
        self.fields['problem_parts_cleared'].required = True
    
    class Meta():
        model = Parts
        #fields = '__all__'
        fields =['problem_parts_cleared','notes']
        widgets = {
                'approved_date':DateInput(),
                }

    def clean_date(self):
        date1 = date.today()
        print(date1)
        date2 = self.cleaned_data['approved_date']
        print(date2)
        if date2>date1:
             raise forms.ValidationError("The date can't be in the future!")
        

class RejectForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(RejectForm, self).__init__(*args, **kwargs)
        # Making location required
        self.fields['reject_note'].required = True

    class Meta():
        model = SalesOrder
        fields = ['reject_date', 'reject_note',]
        widgets = {
                'reject_date':DateInput(),
                }


class AllocatedToForm(forms.ModelForm):

    class Meta():
        model = SalesOrder
        fields = ['allocated_to']

