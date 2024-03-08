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

# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import BankEmployee

class BankEmployeeForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')

    class Meta:
        model = BankEmployee
        fields = ['first_name', 'last_name', 'salary', 'position', 'address', 'ITFSCcode']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        # Set the employee_name based on first_name and last_name
        user.employee_name = f"{user.first_name} {user.last_name}"

        if commit:
            user.save()
        return user



