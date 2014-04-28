#coding=utf-8
import json
import re
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib import auth
from django.shortcuts import render, redirect
from Account.utils import user_exist
from Forum.models import Post
from Message.models import Message


def message(status, content):
    response_json = {"status": status, "content": content}
    return HttpResponse(json.dumps(response_json))


def register(request):
    if request.method == "POST":
        username = request.POST.get("username", " ").strip()
        email = request.POST.get("email", " ").strip()
        password = request.POST.get("password", " ").strip()
        password1 = request.POST.get('password1', " ").strip()

        if not (3 <= len(username) <= 10):
            return message("error", u"用户名只能是3-10个字符")

        r = re.compile(r"[A-Za-z0-9\u4e00-\u9fa5]+")
        if not r.match(username):
            return message("error", u"用户名只能是中英文字母和数字")

        username_is_exist = User.objects.filter(username=username).exists()
        if username_is_exist:
            return message("error", u"用户名已经存在")

        r = re.compile(r"[^@]+@[^@]+\.[^@]+")
        if not r.match(email):
            return message("error", u"请检查邮箱格式")

        email_is_exist = User.objects.filter(email=email).exists()
        if email_is_exist:
            return message("error", u"邮箱已经存在")

        if password != password1:
            return message("error", u"两个密码不一致")

        if len(password) < 6:
            return message("error", u"密码太短")

        User.objects.create_user(username=username, password=password, email=email)
        next = request.POST.get("next", "/")
        response_json = {"status": "success", "redirect": next}
        return HttpResponse(json.dumps(response_json))

    else:
        next = request.GET.get("next", "/")
        return render(request, "Account/register_form.html", {"next": next})


def login(request):
    if request.method == "POST":
        username = request.POST.get("username", "-1")
        password = request.POST.get("password", "-1")
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
        old_password = request.POST.get("old_password")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        if password1 == password2:
            if len(password1) < 6:
                return message("error", u"密码过短")
            if auth.authenticate(username=request.user.username, password=old_password):
                user = User.objects.get(username=request.user.username)
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
