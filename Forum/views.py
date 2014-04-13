#coding=utf-8
import time
import json
import re
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.core.paginator import Paginator
from Forum.models import Zone, Post, Reply
from Forum.utils import is_manager
from Account.utils import user_exist
from Message.models import Message


@login_required(login_url="/account/login")
def index(request, page_num=1):
    posts = Post.objects.order_by("-last_reply")
    page_info = Paginator(posts, 10)
    total_page = page_info.num_pages
    if int(page_num) > total_page:
        raise Http404
    return render(request, "Forum/index.html", {"posts": page_info.page(page_num),
                                                "page_num": unicode(page_num),
                                                "total_page": unicode(total_page),
                                                "pre_page": unicode(int(page_num) - 1),
                                                "next_page": unicode(int(page_num) + 1), })


#一个zone的帖子列表
@login_required(login_url="/account/login/")
def zone_page(request, zone_id, page_num=1):
    try:
        zone = Zone.objects.get(id=zone_id)
    except Zone.DoesNotExist:
        raise Http404
    posts = Post.objects.filter(zone_name=zone.name)
    page_info = Paginator(posts, 10)
    total_page = page_info.num_pages
    if int(page_num) > total_page:
        raise Http404
    return render(request, "Forum/zone.html", {"zone": zone,
                                               "posts": page_info.page(page_num),
                                               "page_num": unicode(page_num),
                                               "total_page": unicode(total_page),
                                               "pre_page": unicode(int(page_num) - 1),
                                               "next_page": unicode(int(page_num) + 1), })


#一个帖子的详情和回复
@login_required(login_url="/account/login/")
def post_page(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise Http404
    zone = Zone.objects.get(name=post.zone_name)
    if (not (request.user.is_staff
             or request.user.username == post.author
             or is_manager(zone.id, request.user.username))):
        edit = False
        delete = False
    else:
        edit = True
        delete = True
    if "csrftoken" in request.COOKIES:
        token = request.COOKIES["csrftoken"]
    else:
        delete = False
        token = None
    return render(request, "Forum/post.html",
                  {"post": post, "zone": zone, "edit": edit, "delete": delete, "token": token})


#回复一个帖子
@login_required(login_url="/account/login/")
def reply_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DOesNotExist:
        raise Http404
    content = request.POST.get("content", " ").strip()
    if len(content) < 3:
        response_json = {"status": "error", "content": "再多写几个字吧"}
        return HttpResponse(json.dumps(response_json))
    reply = Reply.objects.create(username=request.user.username, content=content)
    post.reply.add(reply)
    post.last_reply = reply.create_time
    post.save()

    r = re.compile(u"@[A-Za-z0-9\u4e00-\u9fa5]+")
    username_list = filter(user_exist, map(lambda m: m[1:], r.findall(unicode(reply.content))))

    for username in username_list:
        Message.objects.create(to_user=username, from_user="system",
                               subject=u"有人在帖子中@了你",
                               content=u"""<p>帖子标题 <a href='/forum/post/%s/'>%s</a>， 点击查看<p>
                                           <blockquote>
                                           <p>%s</p>
                                           </blockquote>
                                        """ % (post.id, post.title, reply.content))
    Message.objects.create(to_user=post.author, from_user="system",
                           subject=u"有人回复了你的帖子",
                           content=u"""<p>帖子标题 <a href='/forum/post/%s/'>%s</a>， 点击查看<p>
                                       <blockquote>
                                       <p>%s</p>
                                       </blockquote>
                                    """ % (post.id, post.title, reply.content))

    response_json = {"status": "success", "time": time.strftime('%Y-%m-%d %X', time.localtime()),
                     "username": reply.username, "content": reply.content}
    return HttpResponse(json.dumps(response_json))


#发表新帖子
@login_required(login_url="/account/login/")
def post_new(request, zone_id):
    try:
        zone = Zone.objects.get(id=zone_id)
    except Zone.DoesNotExist:
        raise Http404
    if request.method == "GET":
        return render(request, "Forum/post_new.html", {"zone_id": zone_id, "zone_name": zone.name})
    else:
        title = request.POST.get("title", " ").strip()
        content = request.POST.get("content", " ").strip()
        if len(title) < 3 or len(content) < 5:
            response_json = {"status": "error", "content": "再多写几个字吧"}
            return HttpResponse(json.dumps(response_json))
        post = Post.objects.create(zone_name=zone.name, author=request.user.username, title=title, content=content)
        response_json = {"status": "success", "redirect": "/forum/post/%s/" % post.id}
        return HttpResponse(json.dumps(response_json))


#编辑一个帖子
@login_required(login_url="/account/login/")
def edit_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise Http404
    zone = Zone.objects.get(name=post.zone_name)
    #判断是不是本人 管理员或者版主
    if (not (request.user.is_staff
             or request.user.username == post.author
             or is_manager(zone.id, request.user.username))):
        raise Http404
    if request.method == "GET":
        return render(request, "Forum/edit.html", {"post": post})
    else:
        title = request.POST.get("title", " ").strip()
        content = request.POST.get("content", " ").strip()
        if len(title) < 3 or len(content) < 5:
            response_json = {"status": "error", "content": "再多写几个字吧"}
            return HttpResponse(json.dumps(response_json))
        post.title = title
        post.content = content
        post.save()
        response_json = {"status": "success", "redirect": "/forum/post/%s/" % post.id}
        return HttpResponse(json.dumps(response_json))


@login_required(login_url="/account/login")
def delete_comment(request):
    comment_id = request.GET.get("id", "-1")
    token = request.GET.get("token", "")
    try:
        reply = Reply.objects.get(id=comment_id)
    except Reply.DoesNotExist:
        raise Http404
    post = reply.post_set.all()[0]
    zone = Zone.objects.get(name=post.zone_name)
    if (not (request.user.is_staff
             or request.user.username == post.author
             or is_manager(zone.id, request.user.username))):
        raise Http404
    if "csrftoken" in request.COOKIES:
        if token != request.COOKIES["csrftoken"]:
            return HttpResponseForbidden("Invalid Token")
    else:
        return HttpResponseForbidden("Invalid Token")
    post.reply.remove(reply)
    return HttpResponse("success")


@login_required(login_url="/account/login/")
def delete_post(request):
    post_id = request.GET.get("post_id", "-1")
    token = request.GET.get("token", None)
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise Http404
    zone = Zone.objects.get(name=post.zone_name)

    if (not (request.user.is_staff
             or request.user.username == post.author
             or is_manager(zone.id, request.user.username))):
        raise Http404
    if "csrftoken" in request.COOKIES:
        if token != request.COOKIES["csrftoken"]:
            return HttpResponseForbidden("Invalid Token")
    else:
        return HttpResponseForbidden("Invalid Token")
    post.delete()
    return HttpResponse("success")


def save_file(file_obj):
    import sae.storage

    domain_name = "file"
    s = sae.storage.Client()
    obj = sae.storage.Object(file_obj.read())
    url = s.put(domain_name, str(time.time()) + file_obj.name, obj)
    return url


@login_required(login_url="/account/login/")
def upload_file(request):
    if request.method == "GET":
        return render(request, "Forum/upload_file.html")
    else:
        file_obj = request.FILES.get("upload", None)
        if file_obj:
            file_url = save_file(file_obj)
            return render(request, "Forum/upload_file.html", {"file_url": file_url})
        else:
            raise Http404
