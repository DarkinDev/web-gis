"""
Frontend Forms - User and Profile forms
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from bus.models import UserProfile, Review

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

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(max_length=50, required=True, label="Tên")
    last_name = forms.CharField(max_length=50, required=True, label="Họ")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, f'{i} sao') for i in range(1, 6)],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Đánh giá"
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Viết nhận xét của bạn...'}),
        label="Nhận xét"
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']


