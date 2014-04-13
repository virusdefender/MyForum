#coding:utf-8
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseForbidden
from Message.forms import MessageForm
from Message.models import Message
from Account.utils import user_exist
from django.core.paginator import Paginator


@login_required(login_url="/account/login/")
def send_message(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/account/login/?next=" + request.META.get('HTTP_REFERER', "/"))
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            to_user = form.cleaned_data["to_user"]
            subject = form.cleaned_data["subject"]
            content = form.cleaned_data["content"]
            if not user_exist(to_user):
                response_json = {"status": "error", "content": "收件人账号不存在"}
                return HttpResponse(json.dumps(response_json))
            Message.objects.create(to_user=to_user, from_user=request.user.username, subject=subject, content=content)
            response_json = {"status": "success", "redirect": "/message/"}
            return HttpResponse(json.dumps(response_json))
        else:
            response_json = {"status": "error", "content": "表单数据错误"}
            return HttpResponse(json.dumps(response_json))
    else:
        raise Http404


@login_required(login_url="/account/login/")
def read_message(request, message_id):
    system_message = False
    try:
        received_msg = Message.objects.get(id=message_id, to_user=request.user.username)
        if received_msg.from_user == "system":
            system_message = True
    except Message.DoesNotExist:
        try:
            sent_msg = Message.objects.get(id=message_id, from_user=request.user.username)
        except Message.DoesNotExist:
            raise Http404
        msg_type = "sent"
        return render(request, "Message/message_detail.html",
                      {"type": msg_type, "info": sent_msg, "system_message": system_message})
    msg_type = "received"
    received_msg.status = True
    received_msg.save()
    return render(request, "Message/message_detail.html",
                  {"type": msg_type, "info": received_msg, "system_message": system_message})


@login_required(login_url="/account/login/")
def message_index(request):
    unread_message = Message.objects.filter(to_user=request.user.username, status=False).order_by("-create_time")
    #sent = Message.objects.filter(from_user=request.user.username).order_by("-create_time")
    return render(request, "Message/message_index.html", {"unread_message": unread_message, "unread_message_num": len(unread_message)})


@login_required(login_url="/login/")
def message_page(request, message_type, page_num):
    if "csrftoken" in request.COOKIES:
        token = request.COOKIES["csrftoken"]
    else:
        return HttpResponseForbidden("Invalid Token")
    if not (message_type == "received" or message_type == "sent"):
        raise Http404
    if message_type == "received":
        received = Message.objects.filter(to_user=request.user.username).order_by("-create_time")
        page_info = Paginator(received, 15)
        total_page = page_info.num_pages
        if int(page_num) > total_page:
            raise Http404
        return render(request, "Message/message_page.html", {"type": "received",
                                                             "info": page_info.page(page_num),
                                                             "total_page": unicode(total_page),
                                                             "pre_page": unicode(int(page_num) - 1),
                                                             "page_num": unicode(page_num),
                                                             "next_page": unicode(int(page_num) + 1),
                                                             "token": token})
    else:
        sent = Message.objects.filter(from_user=request.user.username).order_by("-create_time")
        page_info = Paginator(sent, 15)
        total_page = page_info.num_pages
        if int(page_num) > total_page:
            raise Http404
        return render(request, "Message/message_page.html", {"type": "sent",
                                                             "info": page_info.page(page_num),
                                                             "total_page": unicode(total_page),
                                                             "pre_page": unicode(int(page_num) - 1),
                                                             "page_num": unicode(page_num),
                                                             "next_page": unicode(int(page_num) + 1)})


@login_required(login_url="/account/login/")
def send_message_index(request):
    to_user = request.GET.get("to_user", "")
    reply = request.GET.get("reply", "")
    return render(request, "Message/send_message.html", {"to_user": to_user, "reply": reply})


def get_message_status(request):
    if request.user.is_authenticated():
        status = Message.objects.filter(to_user=request.user.username, status=False).exists()
        if status:
            response_json = {"status": "new_message"}
        else:
            response_json = {"status": "no_new_message"}
    else:
        response_json = {"status": "no_new_message"}
    return HttpResponse(json.dumps(response_json))


@login_required(login_url="/account/login/")
def mark_read(request):
    token = request.GET.get("token", "")
    if "csrftoken" in request.COOKIES:
        if token != request.COOKIES["csrftoken"]:
            return HttpResponseForbidden("Invalid Token")
    else:
        return HttpResponseForbidden("Invalid Token")
    message = Message.objects.filter(to_user=request.user.username, status=False)
    message.update(status=True)
    return HttpResponse("success")


@login_required(login_url="/account/login/")
def delete_all_message(request):
    token = request.GET.get("token", "")
    if "csrftoken" in request.COOKIES:
        if token != request.COOKIES["csrftoken"]:
            return HttpResponseForbidden("Invalid Token")
    else:
        return HttpResponseForbidden("Invalid Token")
    Message.objects.filter(to_user=request.user.username).delete()
    return HttpResponse("success")