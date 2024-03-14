from django import forms
from .models import Bank, Branch

class BranchForm(forms.ModelForm):
    bank = forms.ModelChoiceField(
        queryset=Bank.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='bank'
    )
    class Meta:
        model = Branch
        fields = ['name', 'location', 'contact_number', 'pin_code', 'managers_ssn','bank']

from django import forms
from django.contrib.auth.models import User
from .models import BankEmployee, Branch
import random
import time

class BankEmployeeForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')

    class Meta:
        model = BankEmployee
        fields = ['first_name', 'last_name', 'salary', 'position', 'address', 'ITFSCcode']

    def save(self, commit=True):
        # Generate a unique 16-digit ID for the employee
        employee_id = generate_unique_employee_id()

        # Check if the role is Manager
        # Check if the role is Manager
        if self.cleaned_data['position'] == 'manager':
            branch = self.cleaned_data['ITFSCcode']
            print(branch.ifsc_code)
            existing_manager = BankEmployee.objects.filter(position='manager', ITFSCcode=branch.ifsc_code).first()

            if existing_manager:
                # Update the existing Manager's details
                existing_manager.first_name = self.cleaned_data['first_name']
                existing_manager.last_name = self.cleaned_data['last_name']
                existing_manager.salary = self.cleaned_data['salary']
                existing_manager.address = self.cleaned_data['address']
                existing_manager.save()

                # Remove the existing Manager from the auth User table
                User.objects.filter(id=existing_manager.user_id).delete()

                # Use 'employee' here
                employee = existing_manager
            else:
                # Create a new Manager record
                employee = super().save(commit=False)
                user = User.objects.create_user(
                    username=str(employee_id),
                    password=str(employee_id),
                    first_name=self.cleaned_data['first_name'],
                    last_name=self.cleaned_data['last_name']
                )
                employee.user = user
                employee.employee_name = f"{user.first_name} {user.last_name}"
                while BankEmployee.objects.filter(employee_number=employee_id).exists():
                    employee_id = generate_unique_employee_id()
                employee.employee_number = employee_id

                if commit:
                    user.save()
                    employee.save()

                # Save the manager's_ssn field before saving the branch
                employee.save()
                branch.managers_ssn = employee
                branch.save()
        else:
            employee = super().save(commit=False)
            while BankEmployee.objects.filter(employee_number=employee_id).exists():
                    employee_id = generate_unique_employee_id()
            employee.employee_number = employee_id
            # For non-Manager roles, proceed with the regular save
            user = User.objects.create_user(
                username=str(employee_id),
                password=str(employee_id),
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name']
            )
            employee.user = user

            if commit:
                user.save()
                employee.save()

        return employee

def generate_unique_employee_id():
    # Generate a timestamp to ensure uniqueness
    timestamp = int(time.time() * 1000)  # Multiply by 1000 to get milliseconds
    # Generate a random 4-digit number
    random_number = random.randint(1000, 9999)
    # Combine timestamp and random number to create a unique ID
    unique_id = f"{timestamp}{random_number}"
    return unique_id



# forms.py

from django import forms
from .models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']  # Add other fields as needed
