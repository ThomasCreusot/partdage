from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class LoginForm(forms.Form):
    """Represents a login form"""

    username = forms.CharField(max_length=100, label='Username')
    password = forms.CharField(max_length=50, widget=forms.PasswordInput, label='Password')
