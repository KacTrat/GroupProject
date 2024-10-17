from django import forms
from django.contrib.auth.models import User
import re

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Password must contain at least one uppercase and one lowercase.")
        if not re.search(r'\d', password):
            raise forms.ValidationError("Password must contain at least one digits.")
        if not re.search(r'[@$!%*?&]', password):
            raise forms.ValidationError("Password needs to contain at least one from following: @$!%*?&")
        return password

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Hasła nie są zgodne.')
        return cd['password2']