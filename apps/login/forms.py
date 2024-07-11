

from django import forms
from .models import CustomUser as User
from django.contrib.auth.forms import PasswordChangeForm


class LoginInfor(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    
    full_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Full Name",
                "class": "form-control"
            }
        ))
    
    name_bank = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Full Name",
                "class": "form-control"
            }
        ))
    
    bank_number = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Bank Number",
                "class": "form-control"
            }
        ))
    
    phone_number = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Phone Number",
                "class": "form-control"
            }
        ))
    class Meta:
        model = User
        fields = ['email', 'full_name', 'name_bank','bank_number', 'phone_number']

class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Old Password",
                "class": "form-control col"
            }
        ))
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "New Password",
                "class": "form-control col"
            }
        ))
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm New Password",
                "class": "form-control col"
            }
        ))
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.note_password = self.cleaned_data['new_password1']
        if commit:
            user.save()
        return user