from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('این ایمیل قبلاً ثبت شده است.')
        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام کاربری'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'رمز عبور'})
    )