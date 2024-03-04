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
