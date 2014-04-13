#coding=utf-8
from django.db import models


class ZoneManager(models.Model):
    username = models.CharField(max_length=20)
    is_creater = models.BooleanField()

    def __unicode__(self):
        return "ZoneManager : %s" % self.username


class Zone(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100)
    create_time = models.DateTimeField(auto_now_add=True)
    manager = models.ManyToManyField(ZoneManager)

    def __unicode__(self):
        return "Zone : %s" % self.name


class Reply(models.Model):
    username = models.CharField(max_length=20)
    create_time = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    def __unicode__(self):
        return "Reply : %s %s" % (self.username, self.create_time)


class Post(models.Model):
    zone_name = models.CharField(max_length=20)
    author = models.CharField(max_length=20)
    create_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    last_reply = models.DateTimeField(auto_now_add=True)
    reply = models.ManyToManyField(Reply, blank=True)

    def __unicode__(self):
        return "Post : %s %s" % (self.author, self.title)
