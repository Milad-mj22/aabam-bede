from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import SystemSetting
from .forms import RegisterForm, LoginForm
from .models import User


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        settings_obj = SystemSetting.get_settings()
        user = form.save(commit=False)

        if settings_obj.registration_mode == SystemSetting.RegistrationMode.AUTO:
            user.status = User.Status.ACTIVE
            messages.success(self.request, 'ثبت‌نام با موفقیت انجام شد. وارد شوید.')
        else:
            user.status = User.Status.ACTIVE
            messages.info(
                self.request,
                'ثبت‌نام انجام شد. حساب شما در انتظار تأیید مدیر است.'
            )

        user.save()
        return redirect(self.success_url)


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        user = form.get_user()
        if user.status == User.Status.PENDING:
            messages.warning(self.request, 'حساب شما هنوز تأیید نشده است.')
            return redirect('accounts:login')
        if user.status in [User.Status.REJECTED, User.Status.SUSPENDED]:
            messages.error(self.request, 'حساب شما غیرفعال است.')
            return redirect('accounts:login')
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'accounts/profile.html'
    fields = ['first_name', 'last_name', 'email', 'phone', 'avatar']
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'پروفایل با موفقیت به‌روزرسانی شد.')
        return super().form_valid(form)