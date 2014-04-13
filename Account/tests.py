#coding=utf-8
import json
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client


class UserRegisterTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_with_correct_info(self):
        respose = self.client.post(reverse("register"), {"username": "test",
                                                         "email": "test@qq.com",
                                                         "password": "111111",
                                                         "password1": "111111"})
        self.assertEqual(json.loads(respose.content)["status"], "success")

    def test_register_with_invalid_username(self):
        respose = self.client.post(reverse("register"), {"username1": "test111111111111",
                                                         "email": "test@qq.com",
                                                         "password": "111111",
                                                         "password1": "111111"})
        self.assertEqual(json.loads(respose.content)["status"], "error")

        respose = self.client.post(reverse("register"), {"username1": "@@##$$",
                                                         "email": "test@qq.com",
                                                         "password": "111111",
                                                         "password1": "111111"})
        self.assertEqual(json.loads(respose.content)["status"], "error")


    def test_register_the_same_username(self):
        self.client.post(reverse("register"), {"username": "test",
                                               "email": "test@qq.com",
                                               "password": "111111",
                                               "password1": "111111"})
        respose = self.client.post(reverse("register"), {"username": "test",
                                                         "email": "test@qq.com",
                                                         "password": "111222",
                                                         "password1": "111222"})
        self.assertEqual(json.loads(respose.content)["status"], "error")

    def test_register_the_same_email(self):
        self.client.post(reverse("register"), {"username": "test",
                                               "email": "test@qq.com",
                                               "password": "111111",
                                               "password1": "111111"})
        respose = self.client.post(reverse("register"), {"username": "test1",
                                                         "email": "test@qq.com",
                                                         "password": "111222",
                                                         "password1": "111222"})
        self.assertEqual(json.loads(respose.content)["status"], "error")

    def test_register_with_invalid_email(self):
        respose = self.client.post(reverse("register"), {"username": "test1",
                                                         "email": "test.qq.com",
                                                         "password": "111111",
                                                         "password1": "111111"})
        self.assertEqual(json.loads(respose.content)["status"], "error")

    def test_register_with_different_psw(self):
        respose = self.client.post(reverse("register"), {"username": "test1",
                                                         "email": "test@qq.com",
                                                         "password": "1111112",
                                                         "password1": "111111"})
        self.assertEqual(json.loads(respose.content)["status"], "error")


class UserLoginTest(TestCase):
    def setUp(self):
        self.user = User(username="testuser")
        self.user.set_password("111111")
        self.user.save()
        self.client = Client()

    def test_login_with_correct_info(self):
        respose = self.client.post(reverse("login"), {"username": "testuser",
                                                      "password": "111111"})
        self.assertEqual(json.loads(respose.content)["status"], "success")

    def test_login_with_error_info(self):
        respose = self.client.post(reverse("login"), {"username": "testuser1",
                                                      "password": "111111"})
        self.assertEqual(json.loads(respose.content)["status"], "error")