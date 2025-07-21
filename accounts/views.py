# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, SignupForm, UserUpdateForm, ProfileDeleteForm
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request, 
                username=form.cleaned_data['username'], 
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                messages.success(request, '로그인 성공!')
                return redirect('main:home')
            else:
                messages.error(request, '아이디 또는 비밀번호가 일치하지 않습니다. 다시 입력해주세요.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, '로그아웃되었습니다.')
    return redirect('main:home')

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '회원가입이 완료되었습니다.')
            return redirect('main:home')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

@login_required
def profile_update(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필이 성공적으로 수정되었습니다.')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'accounts/profile_update.html', {'form': form})

@login_required
def profile_delete(request):
    if request.method == 'POST':
        form = ProfileDeleteForm(request.POST)
        if form.is_valid():
            phrase = form.cleaned_data.get('confirmation_phrase')
            if phrase == "계정을 탈퇴합니다.":
                user = request.user
                logout(request)
                user.delete()
                messages.success(request, "계정이 탈퇴되었습니다.")
                return redirect('welcome')
            else:
                messages.error(request, "문장은 정확하게 입력해주세요.")
    else:
        form = ProfileDeleteForm()
    return render(request, 'accounts/delete_account.html', {'form': form})