from django import forms
from django import forms
from django.utils.translation import gettext_lazy as _

from django.contrib.auth import get_user_model
from django.forms import PasswordInput
from account.forms import SignupForm, LoginForm, LoginEmailForm
from django.conf import settings

from . models import Profile

class AccountForm(SignupForm):
    first_name = forms.CharField(
        label=_("First Name"),
        max_length=120,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter your first name *',
                'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary'
                }
        ),
        required=True
    )

    last_name = forms.CharField(
        label=_("Last Name"),
        max_length=120,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter your last name *',
                'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary'
                }
        ),
        required=True
    )

    gender = forms.ChoiceField(
        label=_("Gender"),
        widget=forms.RadioSelect(
            attrs={
                'class': 'flex cursor-pointer select-none items-center space-x-4 text-sm font-medium text-black dark:text-white'
            }
        ),
        choices=(('M', 'Male'), ('F', 'Female')),
        required=True
    )

   

    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        # manually changing the place holder of signup form field of password_confirm
        self.fields['password_confirm'].widget = forms.PasswordInput(attrs={'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary', 'placeholder': 'Confirm Password'})
        self.fields['email'].widget = forms.TextInput(attrs={'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary', 'placeholder': 'Enter your email'})

        del self.fields["username"]
    
    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data['password_confirm']
        if(not password == password2):
            raise forms.ValidationError('password not match!')
        return password2

    def clean_email(self):
        email = self.cleaned_data.get("email")
        user = get_user_model().objects.filter(email=email).first()
        if user:
            raise forms.ValidationError('Email address already in use.')
        return email
    
class SignupForm(AccountForm):
        def __init__(self, *args, **kwargs):
            super(SignupForm, self).__init__(*args, **kwargs)


class LoginEmailForm(LoginForm):

    email = forms.CharField(
        label=_("Email"),
        max_length=120,
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'Enter your email *',
                'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary'
                }
        ),
        required=True
    )
    
    password = forms.CharField(
        label=_("Password"),
        max_length=120,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Enter your password *',
                'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary'
                }
        ),
        required=True
    )

    authentication_fail_message = _("The email address and/or password you specified are not correct.")
    identifier_field = "email"

    def __init__(self, *args, **kwargs):
        super(LoginEmailForm, self).__init__(*args, **kwargs)
        field_order = ["email", "password", "remember"]
