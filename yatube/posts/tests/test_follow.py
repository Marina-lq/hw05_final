
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.test import Client, TestCase

from posts.models import Follow


class CommentTest(TestCase):

    def setUp(self):
        self.client_auth = Client()
        self.user1 = User.objects.create_user(username="sarah")
        self.user2 = User.objects.create_user(username="james")
        self.client_auth.force_login(self.user1)

        self.client_unauth = Client()

    def test_auth_user_can_subscribe(self):
        response_get_profile = self.client_auth.get(
            reverse('posts:profile', args=(self.user2,)))
        self.assertIn("Подписаться", response_get_profile.content.decode())
        self.assertNotIn("Отписаться", response_get_profile.content.decode())

        response_subscribe = self.client_auth.post(reverse
                                                   ('posts:profile_follow',
                                                    args=(self.user2,)),
                                                   follow=True)

        is_follow = Follow.objects.filter(user=self.user1,
                                          author=self.user2).count()
        self.assertEqual(is_follow, 1)

        self.assertIn("Отписаться", response_subscribe.content.decode())

    def test_auth_user_can_unsubscribe(self):
        Follow.objects.create(user=self.user1, author=self.user2)
        is_follow = Follow.objects.filter(user=self.user1,
                                          author=self.user2).count()
        self.assertEqual(is_follow, 1)
        response_unsubscribe = self.client_auth.post(
            reverse('posts:profile_unfollow',
                    args=(self.user2,)), follow=True)
        self.assertIn("Подписаться", response_unsubscribe.content.decode())

        follow_obj = Follow.objects.filter(user=self.user1,
                                           author=self.user2).count()
        self.assertEqual(follow_obj, 0)
