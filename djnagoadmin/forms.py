from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate

class SuperuserAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_superuser:
            raise forms.ValidationError(
                'This is an admin-only area. Please log in with an admin account.'
            )

    def clean(self):
        cleaned_data = super().clean()

        # Check if the username and password are provided
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            # Authenticate the user to check for incorrect credentials
            user = authenticate(self.request, username=username, password=password)

            if user is None:
                raise forms.ValidationError(
                    'Incorrect username or password. Please try again.'
                )

            self.confirm_login_allowed(user)

        return cleaned_data
