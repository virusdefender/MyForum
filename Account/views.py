#coding=utf-8
import json
import re
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib import auth
from django.shortcuts import render, redirect
from Account.forms import RegisterFrom, LoginForm, ChangePswForm
from Account.utils import user_exist
from Forum.models import Post
from Message.models import Message


def register(request):
    if request.method == "POST":
        form = RegisterFrom(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            password1 = form.cleaned_data["password1"]
            username_is_exist = User.objects.filter(username=username).exists()
            if username_is_exist:
                response_json = {"status": "error", "content": u"用户名已经存在"}
                return HttpResponse(json.dumps(response_json))
            r = re.compile(u"[A-Za-z0-9\u4e00-\u9fa5]+")
            if not r.match(username):
                response_json = {"status": "error", "content": u"用户名只能是中英文字母和数字"}
                return HttpResponse(json.dumps(response_json))
            email_is_exist = User.objects.filter(email=email).exists()
            if email_is_exist:
                response_json = {"status": "error", "content": u"邮箱已经存在"}
                return HttpResponse(json.dumps(response_json))
            if password != password1:
                response_json = {"status": "error", "content": u"两个密码不一致"}
                return HttpResponse(response_json)
            User.objects.create_user(username=username, password=password, email=email)
            next = request.POST.get("next", "/")
            response_json = {"status": "success", "redirect": next}
            return HttpResponse(json.dumps(response_json))
        else:
            response_json = {"status": "error", "content": u"表单数据错误，检查一下你的输入"}
            return HttpResponse(json.dumps(response_json))
    else:
        next = request.GET.get("next", "/")
        return render(request, "Account/register_form.html", {"next": next})


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.logout(request)
                auth.login(request, user)
                next = request.POST.get("next", "/")
                #if next == "" or "/register/":
                #next = "/"
                response_json = {"status": "success", "redirect": next}
                return HttpResponse(json.dumps(response_json))
            else:
                response_json = {"status": "error", "content": u"用户名或密码错误，仔细看看~"}
                return HttpResponse(json.dumps(response_json))
        else:
            response_json = {"status": "error", "content": u"表单数据错误，检查一下你的输入"}
            return HttpResponse(json.dumps(response_json))
    else:
        next = request.GET.get("next", "/")
        return render(request, "Account/login_form.html", {"next": next})


@login_required(login_url="/account/login/")
def user_profile(request):
    username = request.GET.get("username", request.user.username)
    if not user_exist(username):
        raise Http404
    #post = Post.objects.filter(author=request.user.username)
    new_message = Message.objects.filter(to_user=request.user.username, status=False).exists()
    return render(request, "Account/user_profile.html", {"new_message": new_message})


def logout(request):
    auth.logout(request)
    return redirect("index")


@login_required(login_url="/account/login/")
def change_password(request):
    if request.method == "POST":
        form = ChangePswForm(request.POST)
        if form.is_valid():
            username = request.user.username
            old_password = form.cleaned_data["old_password"]
            password1 = form.cleaned_data["password1"]
            password2 = form.cleaned_data["password2"]
            if password1 == password2:
                if auth.authenticate(username=username, password=old_password):
                    user = User.objects.get(username=username)
                    user.set_password(password1)
                    user.save()
                    auth.logout(request)
                    response_json = {"status": "success", "redirect": "/account/login/"}
                    return HttpResponse(json.dumps(response_json))
                else:
                    response_json = {"status": "error", "content": u"老密码是错误的~~"}
                return HttpResponse(json.dumps(response_json))
            else:
                response_json = {"status": "error", "content": u"两个密码不一样啊~"}
                return HttpResponse(json.dumps(response_json))
        else:
            response_json = {"status": "error", "content": u"表单数据错误，看看你是不是全填上了~"}
            return HttpResponse(json.dumps(response_json))
    else:
        return render(request, "Account/change_password.html")


def all_post(request, username, page_num=1):
    if not user_exist(username):
        raise Http404
    posts = Post.objects.filter(author=username).order_by("-create_time")
    page_info = Paginator(posts, 10)
    total_page = page_info.num_pages
    if int(page_num) > total_page:
        raise Http404
    return render(request, "Account/user_all_post.html", {"posts": page_info.page(page_num),
                                                          "page_num": unicode(page_num),
                                                          "total_page": unicode(total_page),
                                                          "pre_page": unicode(int(page_num) - 1),
                                                          "next_page": unicode(int(page_num) + 1),
                                                          "username": username})
