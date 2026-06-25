from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import SignupForm, LoginForm


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Welcome, {user.first_name or user.username}!")
        return redirect('home')
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request.POST or None, request=request)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f"Welcome back, {user.first_name or user.username}!")
        return redirect('home')
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


def home_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_doctor():
        return redirect('doctor_dashboard')
    return redirect('patient_dashboard')
