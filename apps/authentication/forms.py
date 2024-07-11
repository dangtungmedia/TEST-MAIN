# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from apps.login.models import CustomUser as User


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
    
class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control"
            }
        ))

    note_password = forms.CharField(
        widget=forms.TextInput(  # Change widget to TextInput for note
            attrs={
                "placeholder": "Note Password",
                "class": "form-control"
            }
        ), required=False  
    )
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2','note_password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.note_password = self.cleaned_data['password1']  # Assign password1 to note_password
        if commit:
            user.save()
        return user