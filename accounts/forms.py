from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

# from .forms import SignupForm, LoginForm, ProfileUpdateForm, ProfileDeleteForm
# import accounts.forms as account_forms


#회원가입 
class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password1", "password2")


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, label="아이디")
    password = forms.CharField(widget=forms.PasswordInput, label="비밀번호")


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(required=False, label="이름")
    email = forms.EmailField(required=True, label="이메일")

    class Meta:
        model = get_user_model()
        fields = ("first_name", "email")


class ProfileDeleteForm(forms.Form):
    confirm_text = forms.CharField(
        label="확인 문구",
        help_text='정확하게 "계정을 탈퇴합니다." 를 입력해주세요.'
    )

    def clean_confirm_text(self):
        confirm = self.cleaned_data.get("confirm_text")
        if confirm != "계정을 탈퇴합니다.":
            raise forms.ValidationError("문장을 정확하게 입력해주세요.")
        return confirm