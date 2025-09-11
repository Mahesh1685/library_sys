# users/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import StudentRegistrationForm
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.forms import AuthenticationForm

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! Awaiting librarian approval.')
            return redirect('home')
    else:
        form = StudentRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_approved:
                messages.error(request, "Your account is not approved yet.")
                return redirect('login')
            auth_login(request, user)
            if user.role=='librarian':
                return redirect('librarian_dashboard')
            elif user.role=='student':
                return redirect('student_profile')
            else:
                return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')