from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist

from django.db import models
from django.utils.crypto import get_random_string
from django.utils.text import slugify

from django.contrib.auth.models import User
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.text import slugify

class Bank(models.Model):
    BANK_TYPE_CHOICES = [
        ('gov', 'Government'),
        ('private', 'Private'),
        ('cooperative', 'Cooperative'),
    ]
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=21, unique=True, editable=False)
    main_branch_address = models.TextField()
    owner_name = models.CharField(max_length=100)
    bank_type = models.CharField(max_length=20, choices=BANK_TYPE_CHOICES)
    customer_service_number = models.CharField(max_length=15)
    bank_email = models.EmailField()
    name_link = models.CharField(max_length=21, unique=True, editable=False)
    bank_user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, editable=False)
    password= models.CharField(max_length=12,editable=False)
    def save(self, *args, **kwargs):
        # Generate the code based on the specified format
        code_prefix = ''.join([word[0].upper() for word in self.name.replace(" ", "")][:2])
        random_digits = get_random_string(length=6, allowed_chars='0123456789')
        self.code = f'{code_prefix}{random_digits}'

        # Make the bank name unique case-insensitively
        self.name = self.name.capitalize()
        existing_banks = Bank.objects.filter(name__iexact=self.name)
        if self.pk:
            existing_banks = existing_banks.exclude(pk=self.pk)
        if existing_banks.exists():
            raise ValueError('Bank with this name already exists.')
        # Generate the name_link based on the name
        self.name_link = slugify(self.name)
        # Create a new user for the bank
        user_password = get_random_string(length=12)  # Generate a random password
        self.password=user_password
        user = User.objects.create_user(username=self.bank_email, email=self.bank_email, password=user_password)
        # Save the new user in the bank
        self.bank_user = user
        super(Bank, self).save(*args, **kwargs)
    def __str__(self):
        return self.name


class BankEmployee(models.Model):
    POSITION_CHOICES = [
        ('manager', 'Manager'),
        ('assistant_manager', 'Assistant Manager'),
        ('teller', 'Teller'),
        ('customer_service_rep', 'Customer Service Representative'),
        ('loan_officer', 'Loan Officer'),
        ('financial_analyst', 'Financial Analyst'),
        ('accountant', 'Accountant'),
        ('auditor', 'Auditor'),
        ('security_officer', 'Security Officer'),
        ('IT_specialist', 'IT Specialist'),
        ('marketing_specialist', 'Marketing Specialist'),
        ('human_resources', 'Human Resources'),
        ('operations_specialist', 'Operations Specialist'),
        ('cleaner', 'Cleaner'),
    ]
    USERNAME_FIELD = 'employee_number'
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='bank_employee')
    employee_name = models.CharField(max_length=100)
    employee_number = models.CharField(max_length=20, unique=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    position = models.CharField(max_length=60, choices=POSITION_CHOICES)
    address = models.TextField()
    ITFSCcode = models.ForeignKey("Branch", on_delete=models.CASCADE, to_field='ifsc_code', related_name='it_employees')

    def __str__(self):
        return f"{self.employee_name} - {self.employee_number} - {self.position}"

from django.db import models
from django.utils.crypto import get_random_string
from django.utils.text import slugify

class Branch(models.Model):
    ifsc_code = models.CharField(max_length=23, primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='branches_at_bank')
    location = models.CharField(max_length=255)
    managers_ssn = models.ForeignKey(BankEmployee,to_field='employee_number', on_delete=models.SET_NULL, null=True, blank=True)
    contact_number = models.CharField(max_length=15)
    pin_code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Check if the object is being created or updated
        is_new_object = not bool(self.pk)

        # If it's a new object, generate a unique IFSC code
        if is_new_object:
            # Generate a unique IFSC code by adding 2 random letters to the bank code
            random_letters = get_random_string(length=2, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            self.ifsc_code = f'{self.bank.code}{random_letters}'

        super(Branch, self).save(*args, **kwargs)
    def __str__(self):
        return f"{self.name}, {self.bank.name}"

    class Meta:
        unique_together = ('bank', 'ifsc_code')


from django.db import models
from django.utils.crypto import get_random_string
from django.utils.text import slugify

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, to_field='ifsc_code', related_name='accounts')
    account_number = models.CharField(max_length=16, unique=True, primary_key=True, editable=False)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Check if the instance is being created for the first time
        if not self.pk:
            # Generate a unique 16-digit account number
            self.account_number = get_random_string(length=16, allowed_chars='0123456789')

        super(Account, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Account - {self.account_number}"



import uuid

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('Credit', 'Credit'),
        ('Debit', 'Debit'),
        ('Transfer', 'Transfer'),
    )

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, default='Processing', null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transactions', null=True, blank=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transactions', null=True, blank=True)
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.transaction_id}"


from django.utils import timezone

from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='profile')
    contact_number = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    date_of_birth = models.DateField(null=True)
    age = models.IntegerField(null=True, editable=False)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    occupation = models.CharField(max_length=100, null=True)
    father_name = models.CharField(max_length=100, null=True)

    # Add a reverse relation to Account model
    accounts = models.ManyToManyField('Account', related_name='user_profiles')

    def save(self, *args, **kwargs):
        # Calculate age based on date_of_birth and current date
        if self.date_of_birth:
            today = timezone.now().date()
            age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            self.age = age

        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username



class ATMTransaction(Transaction):
    class Meta:
        proxy = True

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} (ATM)"

class OnlineTransaction(Transaction):
    class Meta:
        proxy = True

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} (Online)"


class Card(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, unique=True, related_name='card')
    card_number = models.CharField(max_length=16, unique=True)
    expiration_date = models.DateField()
    cvv = models.CharField(max_length=3)

    def __str__(self):
        return f"{self.account.user.username}'s Card - {self.card_number}"

class Loan(models.Model):
    LOAN_STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    repayment_schedule = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=LOAN_STATUS, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.account.user.username}'s Loan - {self.id}"
    