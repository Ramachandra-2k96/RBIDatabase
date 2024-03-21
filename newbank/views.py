from datetime import timedelta, timezone
from decimal import Decimal
from django.shortcuts import render
from django.db.models import Count
from django.http import HttpResponse
from django.db.models import Sum
from django.db.models import F
from neo4j import Transaction
from .models import Bank, BankEmployee, Branch, UserProfile
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from .models import Bank, BankEmployee, Branch

@csrf_exempt
def bank_admin(request, bank_id):
    bank_code = bank_id.replace('/', '')
    try:
        # Retrieve bank instance
        bank = Bank.objects.get(code=bank_code)
    except Bank.DoesNotExist:
        # Log or print a message to identify the issue
        print(f"Bank with code '{bank_code}' does not exist.")
        # You might want to handle this case appropriately, such as returning an error response.

    # Pie Chart for Employees according to their job roles
    employee_data = BankEmployee.objects.filter(ITFSCcode__bank_id=bank.id).values('position').annotate(count=Count('position'))
    employee_labels = [entry['position'] for entry in employee_data]
    employee_counts = [entry['count'] for entry in employee_data]

    # Pie Chart for Customers of the bank
    customer_data = Branch.objects.filter(bank_id=bank.id).annotate(total_customers=Count('accounts__user'))

    branch_labels = [entry.name for entry in customer_data]
    branch_customer_counts = [entry.total_customers for entry in customer_data]

    # Retrieve all branches related to the bank
    all_branches = Branch.objects.filter(bank_id=bank.id)

    context = {
        'bank': bank,
        'employee_labels': employee_labels,
        'employee_counts': employee_counts,
        'branch_labels': branch_labels,
        'branch_customer_counts': branch_customer_counts,
        'all_branches': all_branches,  # Add this line to include all branches in the context
    }

    return render(request, 'bank_admin.html', context)


@csrf_exempt
def custom_login(request):
    if request.method == 'POST':
        # Get the username and password from the form
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        # Check if authentication was successful
        if user is not None:
            # Log the user in
            login(request, user)
            # Redirect to a success page or home page
            return redirect('dashboard')
        else:
            # Return an error message or handle invalid credentials
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    # If the request method is GET, render the login form
    return render(request, 'login.html')


@csrf_exempt
def bank_login(request):
    if request.method == 'POST':
        # Get the username and password from the form
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        # Check if authentication was successful
        if user is not None:
            # Log the user in
            if Bank.objects.filter(bank_email=username).count() > 0:
                bank = Bank.objects.get(bank_email=username)
                login(request, user)
                return redirect('bank', bank_id=bank.code)
            else:
                return render(request, 'login.html', {'error': 'Invalid username or password'})
        else:
            # Return an error message or handle invalid credentials
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    # If the request method is GET, render the login form
    return render(request, 'login.html')


def landing(request):
    return render(request, 'index.html')

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('landing')

from django.db.models import Count, Sum
from django.shortcuts import render
from django.utils import timezone
from .models import Branch, Transaction, UserProfile, User
@login_required
@csrf_exempt
def branch_details(request, branch_ifsc):
    try:
        # Retrieve branch instance
        branch = Branch.objects.get(ifsc_code=branch_ifsc)
        accounts = Account.objects.filter(branch=branch)
        user_profiles  = [account.user for account in accounts]
        # Pie Chart for Customer Salaries
        result = UserProfile.objects.filter(user__accounts__branch__ifsc_code=branch_ifsc) \
            .values('salary') \
            .annotate(count=Count('salary')) \
            .order_by('salary')
        # Extract salary values and counts into separate variables
        salary_labels = [float(entry['salary']) for entry in result]
        salary_counts = [entry['count'] for entry in result]
        # Pie Chart for Total Transactions by Customers
        transaction_data = Transaction.objects.filter(account__branch__ifsc_code=branch_ifsc, status='Completed').values('account__user__accounts__account_number').annotate(total_amount=Sum('amount'))
        transaction_labels = [f"Account Number: {entry['account__user__accounts__account_number']}" for entry in transaction_data]

        transaction_amounts = [float(entry['total_amount']) for entry in transaction_data]        
        user_transaction=Transaction.objects.filter(account__branch=branch)
        seven_days_ago = timezone.now() - timedelta(days=7)
        new_user_data = Account.objects.filter(
            created_at__gte=seven_days_ago,
            created_at__lte=timezone.now(),
            branch__ifsc_code=branch_ifsc
        ).values('created_at__date').annotate(count=Count('created_at__date'))
        
        new_user_labels = [entry['created_at__date'].strftime('%Y-%m-%d') for entry in new_user_data]
        new_user_counts = [entry['count'] for entry in new_user_data]

        context = {
            "user_transaction":user_transaction[::-1],
            "users_with_accounts":user_profiles[::-1],
            'branch': branch,
            'salary_labels': salary_labels,
            'salary_counts': salary_counts,
            'transaction_labels': transaction_labels,
            'transaction_amounts': transaction_amounts,
            'new_user_labels': new_user_labels,
            'new_user_counts': new_user_counts,
        }
        return render(request, 'branch_details.html', context)

    except Branch.DoesNotExist:
        # Handle branch not found
        return render(request, 'branch_not_found.html')


from django.shortcuts import render, redirect
from .forms import BranchForm
from .models import Bank, Branch
@login_required
@csrf_exempt
def add_branch(request):
    if request.method == 'POST':
        form = BranchForm(request.POST)

        if form.is_valid():
            # Retrieve the Bank instance based on the provided bank code
            bank_code = form.cleaned_data['bank']
            try:
                bank = Bank.objects.get(name=bank_code)
                # Create a new Branch instance and assign the Bank instance
                branch = form.save(commit=False)
                branch.bank = bank
                branch.save()
                return redirect('bank', bank_id=bank.code) 
            except Bank.DoesNotExist:
                # Handle the case where the Bank does not exist
                error_message = f"Bank with code '{bank_code}' does not exist."
                return render(request, 'new_branch.html', {'form': form, 'error_message': error_message})
    else:
        form = BranchForm()

    return render(request, 'new_brach.html', {'form': form})


from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import UserProfile, Account, Branch
from datetime import datetime
@login_required
@csrf_exempt
def register_and_create_account(request, ifsc_code):
    if request.method == 'POST':
        # Extract user information from the form
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        contact_number = request.POST['contact_number']
        address = request.POST['address']
        date_of_birth_str = request.POST['date_of_birth']
        salary = request.POST.get('salary', None)
        occupation = request.POST.get('occupation', None)
        father_name = request.POST.get('father_name', None)

        try:
            # Parse the date_of_birth string into a date object
            date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
        except ValueError:
            # Handle invalid date format
            return render(request, 'registration.html', {'error': 'Invalid date format'})

        try:
            # Validate user age
            today = datetime.now().date()
            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            if age < 10:
                raise ValidationError("User must be at least 10 years old.")
            
            # Validate salary
            if salary is not None and float(salary) < 30000:
                raise ValidationError("Salary must be at least 30000.")
        

            # Create a new user
            password = date_of_birth_str  # Using date_of_birth as the initial password
            user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)

            # Create user profile
            user_profile = UserProfile.objects.create(
                user=user,
                contact_number=contact_number,
                address=address,
                date_of_birth=date_of_birth,
                salary=salary,
                occupation=occupation,
                father_name=father_name
            )

            # Create a bank account
            branch = Branch.objects.get(ifsc_code=ifsc_code)
            account = Account.objects.create(user=user, branch=branch)

            # Store account number as username in the User table
            user.username = account.account_number
            user.save()
            user_profile.save()
            account.save()
            # Redirect to the branch details page

            return redirect('branch_details', branch_ifsc=ifsc_code)

        except ValidationError as e:
            return render(request, 'registration.html', {'error': str(e)})

        except IntegrityError as e:
            return render(request, 'registration.html', {'error': str(e)})

    return render(request, 'registration.html')


# views.py

from django.shortcuts import render
from django.views import View
from .models import Transaction
from django.db.models import Q
@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    template_name = 'dashboard.html'
    def get(self, request, *args, **kwargs):
        # Load user data (replace with your actual logic)
        user = request.user
        user_data=UserProfile.objects.get(user=user)
        account=Account.objects.get(user=user)
        balence=account.balance
        # Load user transactions (replace with your actual logic)
        transactions = Transaction.objects.filter(account__user=request.user).order_by('-timestamp')
        # Separate credit and debit transactions
        credit_transactions = [float(transaction.amount) for transaction in transactions.filter(Q(transaction_type='Credit') | Q(transaction_type='Transfer'), status='Completed')]
        debit_transactions = [float(transaction.amount) for transaction in transactions.filter(transaction_type='Debit', status='Completed')]
        context = {
            'user_data': user_data,
            'balence':balence,
            'user_transaction':transactions,
            'credit_transactions': credit_transactions,
            'debit_transactions': debit_transactions,
        }

        return render(request, self.template_name, context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from decimal import Decimal
from .models import Account, Transaction

@login_required
@csrf_exempt
def make_transfer(request):
    if request.method == 'POST':
        recipient_username = request.POST.get('recipient_username')
        amount = Decimal(request.POST.get('amount', '0.0'))
        try:
            # Get sender's account
            sender_account = Account.objects.get(user=request.user)
            # Get recipient's user and account
            try:
                recipient_user = User.objects.get(username=recipient_username)
                recipient_account = Account.objects.get(user=recipient_user)

                # Check if the sender is trying to send money to himself
                if sender_account == recipient_account:
                    transaction = Transaction.objects.create(
                        account=sender_account,
                        transaction_type='Transfer',
                        amount=amount,
                        sender=request.user,
                        recipient=recipient_user,
                        status='Failed - Cannot transfer to yourself'
                    )
                    return redirect('dashboard')
            except User.DoesNotExist:
                # Handle recipient user not found
                transaction = Transaction.objects.create(
                    account=sender_account,
                    transaction_type='Transfer',
                    amount=amount,
                    sender=request.user,
                    recipient_username=recipient_username,
                    status='Failed - Recipient not found'
                )
                return redirect('dashboard')

            # Perform validation and check if the sender has sufficient balance
            if sender_account.balance >= amount:
                # Create a transfer transaction for sender (Debit)
                sender_transaction = Transaction.objects.create(
                    account=sender_account,
                    transaction_type='Debit',
                    amount=amount,
                    sender=request.user,
                    recipient=recipient_user,
                    status='Processing'
                )

                # Create a transfer transaction for recipient (Credit)
                recipient_transaction = Transaction.objects.create(
                    account=recipient_account,
                    transaction_type='Credit',
                    amount=amount,
                    sender=request.user,
                    recipient=recipient_user,
                    status='Processing'
                )

                # Update account balances
                sender_account.balance -= amount
                sender_account.save()

                recipient_account.balance += amount
                recipient_account.save()

                sender_transaction.status = 'Completed'
                sender_transaction.save()

                recipient_transaction.status = 'Completed'
                recipient_transaction.save()

                return redirect('dashboard')
            else:
                # Handle insufficient balance
                transaction = Transaction.objects.create(
                    account=sender_account,
                    transaction_type='Transfer',
                    amount=amount,
                    sender=request.user,
                    recipient=recipient_user,
                    status='Failed - Insufficient balance'
                )
                return redirect('dashboard')

        except Account.DoesNotExist:
            # Handle sender account not found
            return HttpResponse("Your account is not found.")

    return render(request, 'make_transfer.html')

from django.shortcuts import render, redirect
from .forms import BankEmployeeForm
from .models import Branch
@login_required
@csrf_exempt
def add_employee(request, ifsc_code):
    branch = Branch.objects.get(ifsc_code=ifsc_code)
    if request.method == 'POST':
        form = BankEmployeeForm(request.POST)
        if form.is_valid():
            print("Form data before saving:", form.cleaned_data)
            employee = form.save(commit=False)
            employee.ITFSCcode = branch
            employee.save()
            print("Employee data after saving:", employee.__dict__)
            return redirect('branch_details', branch_ifsc=ifsc_code)
        else:
            print(form.errors)
    else:
        form = BankEmployeeForm()

    return render(request, 'add_employee.html', {'form': form})


# views.py

from django.shortcuts import render, redirect
from .models import User  # Import your User model
from .forms import UserForm  # Import the form you'll create for updating user data
@login_required
@csrf_exempt
def update_user(request, user_id):
    user = User.objects.get(id=user_id)
    b=Account.objects.get(user=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('branch_details', branch_ifsc=b.branch_id)  # Redirect to user detail page
    else:
        form = UserForm(instance=user)
    return render(request, 'update_user.html', {'form': form})


