#coding=utf-8
from django import forms


class RegisterFrom(forms.Form):
    username = forms.CharField(required=True, max_length=7)
    email = forms.EmailField(required=True, max_length=20)
    password = forms.CharField(required=True, min_length=6, max_length=30)
    password1 = forms.CharField(required=True, min_length=6, max_length=30)


class LoginForm(forms.Form):
    username = forms.CharField(required=True, max_length=15)
    password = forms.CharField(required=True, max_length=20)


class ChangePswForm(forms.Form):
    old_password = forms.CharField(max_length=20)
    password1 = forms.CharField(max_length=30)
    password2 = forms.CharField(max_length=30)