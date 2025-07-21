# main/views.py
# from .forms import UserChangeForm
# from django.shortcuts import render, redirect
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from django.contrib.auth import login, logout
# from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def home_view(request):
    return render(request, 'main/home.html')