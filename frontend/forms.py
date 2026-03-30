"""
Frontend Forms - User and Profile forms
"""
from django import forms
from django.contrib.auth.models import User
from bus.models import UserProfile

class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=False, label="Tên")
    last_name = forms.CharField(max_length=50, required=False, label="Họ")
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileUpdateForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=20, required=False, label="Số điện thoại")

    class Meta:
        model = UserProfile
        fields = ['phone_number']
