from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.conf import settings

from .forms import SignupForm, UserUpdateForm, ProfileDeleteForm

##########################################################
# 회원가입 처리

def signup_view(request):
    if request.method == "GET":
        return render(request, "accounts/signup.html", {"form": SignupForm()})
    else:  # POST
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, '회원가입이 완료되었습니다.')
            return redirect(reverse("main:home"))
        else:
            return render(request, "accounts/signup.html", {"form": form})

########################################################################
# 로그인 처리

def login_view(request):
    if request.method == "GET":
        return render(request, "accounts/login.html", {"form": AuthenticationForm()})
    else:  # POST
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, '아이디와 비밀번호를 모두 입력해주세요.')
            return render(request, "accounts/login.html", {"form": AuthenticationForm()})

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, '로그인 성공!')
            return redirect('main:home')
        else:
            messages.error(request, '아이디 또는 비밀번호가 일치하지 않습니다. 다시 입력해주세요.')
            return render(request, "accounts/login.html", {"form": AuthenticationForm()})

###############################################
# 로그아웃 처리

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, '로그아웃되었습니다.')
    return redirect('main:home')

#####################################################
# 회원정보 보기

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

#############################################################
# 회원정보 수정

@login_required
def user_update(request):
    if request.method == "GET":
        form = UserUpdateForm(instance=request.user)
        return render(request, "accounts/profile_update.html", {"form": form})
    else:
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, '프로필이 성공적으로 수정되었습니다.')
            return redirect(reverse("accounts:profile"))
        else:
            return render(request, 'accounts/profile_update.html', {'form': form})

##############################################################################
# 회원정보 탈퇴 --> 삭제 처리

@login_required
def profile_delete(request):
    CONFIRM_PHRASE = getattr(settings, 'ACCOUNT_DELETE_CONFIRMATION_PHRASE', "계정을 탈퇴합니다.")

    if request.method == 'POST':
        form = ProfileDeleteForm(request.POST)
        if form.is_valid():
            phrase = form.cleaned_data.get('confirmation_phrase')
            if phrase == CONFIRM_PHRASE:
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
