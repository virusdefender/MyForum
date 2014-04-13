#coding=utf-8
from django.contrib import admin
from Forum.models import Zone, Reply, Post, ZoneManager


class ZoneAdmin(admin.ModelAdmin):
    list_display = ("name", )


class ReplyAdmin(admin.ModelAdmin):
    list_display = ("username", )


class PostAdmin(admin.ModelAdmin):
    list_display = ("author", )


class ZoneManagerAdmin(admin.ModelAdmin):
    list_display = ("username", "is_creater")


admin.site.register(Zone, ZoneAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(ZoneManager, ZoneManagerAdmin)