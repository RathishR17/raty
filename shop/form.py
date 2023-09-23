from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms
from .models import Customer

class CustomUserForm(UserCreationForm):
    username=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter User Name'}))
    email= forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email Id'}))
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}))
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your confirm password'}))
    class Meta:
        model=User
        fields=['username','email','password1','password2']

class CustomerProfileForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your Name'}))
    locality = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your Area'}))
    city = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your City'}))
    mobile = forms.CharField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Your Mobile'}))
    state = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your State'}))
    zipcode = forms.CharField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your ZipCode'}))

    class Meta:
        model = Customer
        fields = ['name', 'locality', 'city', 'mobile', 'state','zipcode']
