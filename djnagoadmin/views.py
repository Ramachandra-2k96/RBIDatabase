# djnagoadmin/views.py
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect,render
from .forms import SuperuserAuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt


class CustomAdminLoginView(LoginView):
    template_name = 'adminlogin.html'
    authentication_form = SuperuserAuthenticationForm
    @csrf_exempt
    def form_valid(self, form):
        response = super().form_valid(form)
        return redirect('/admin/')
    
def dashboard_redirect(request):
    return redirect('/admin/')

@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to the desired page after successful registration
            return redirect('/login/')  # You can change '/login/' to the desired URL
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})
