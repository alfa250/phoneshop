from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']



class CheckoutForm(forms.Form):
    full_name = forms.CharField(
    max_length=100,
    widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your full name'
    })
    )

    phone = forms.CharField(
    max_length=20,
    widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your phone number'
    })
    )

    address = forms.CharField(
    widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 3,
        'placeholder': 'Enter your delivery address'
    })
    )

    city = forms.CharField(
    max_length=100,
    widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your city'
    })
    )

    state = forms.CharField(
    max_length=100,
    widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your state'
    })
    )
