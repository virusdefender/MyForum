#coding:utf-8
from django.contrib import admin
from Message.models import Message


class MessageAdmin(admin.ModelAdmin):
    list_display = ("to_user", "from_user", "subject", "status")


admin.site.register(Message, MessageAdmin)