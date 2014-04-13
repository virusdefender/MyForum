#coding=utf-8
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'forum.views.home', name='home'),
    # url(r'^forum/', include('forum.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r"^admin/", include(admin.site.urls)),

    #Account related
    url(r"^account/register/$", "Account.views.register", name="register"),
    url(r"^account/login/$", "Account.views.login", name="login"),
    url(r"^account/user_profile/$", "Account.views.user_profile", "user_profile"),
    url(r"^account/logout/$", "Account.views.logout", name="logout"),
    url(r"^account/change_password/$", "Account.views.change_password", name="change_password"),

    url(r"^user/(?P<username>\w+)/$", "Account.views.all_post", name="user_post_page1"),
    url(r"^user/(?P<username>\w+)/page/(?P<page_num>\d+)/$", "Account.views.all_post", name="user_post_page"),

    url(r"^upload_file/$", "Forum.views.upload_file", name="upload_file"),

    #Forum related
    url(r"^$", "Forum.views.index", name="index"),
    url(r"^forum/$", "Forum.views.index", name="forum_index"),
    url(r"^forum/page/(?P<page_num>\d+)/$", "Forum.views.index", name="forum_page"),
    url(r"^forum/zone/(?P<zone_id>\d+)/$", "Forum.views.zone_page", name="zone_index"),
    url(r"^forum/zone/(?P<zone_id>\d+)/page/(?P<page_num>\d+)/$", "Forum.views.zone_page", name="zone_page"),
    url(r"^forum/zone/(?P<zone_id>\d+)/post/$", "Forum.views.post_new", name="post_now"),
    url(r"^forum/post/(?P<post_id>\d+)/$", "Forum.views.post_page", name="post_page"),
    url(r"^forum/post/(?P<post_id>\d+)/reply/$", "Forum.views.reply_post", name="reply_post"),
    url(r"^forum/post/(?P<post_id>\d+)/edit/$", "Forum.views.edit_post", name="edit_post"),
    url(r"^forum/reply/delete_comment/$", "Forum.views.delete_comment", name="delete_comment"),
    url(r"^forum/post/delete/$", "Forum.views.delete_post", name="delete_post"),
    
    #message related
    url(r"^message/$", "Message.views.message_index"),
    url(r"^message/send_message/$", "Message.views.send_message_index"),
    url(r"^message/send_message_operation/$", "Message.views.send_message"),
    url(r"^message/read_message/(?P<message_id>\d+)/$", "Message.views.read_message"),
    url(r"^message/get_status/$", "Message.views.get_message_status"),
    url(r"^message/(?P<message_type>\w+)/(?P<page_num>\d+)/$", "Message.views.message_page"),
    url(r"^message/mark_read/$", "Message.views.mark_read"),
    url(r"^message/delete_all_message/$", "Message.views.delete_all_message"),
)
