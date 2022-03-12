from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post
from posts.models import Group

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Заголовок группы',
            slug='group-slag',
        )
        number_of_posts = 13
        for cls.post in range(number_of_posts):
            cls.post = Post.objects.create(
                author=cls.user,
                group=cls.group,
                text='Тестовый текст',
            )

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_contains_ten_records(self):
        templates_pages_names = [
            reverse('post:index'),
            reverse('post:profile', kwargs={'username':
                                            self.user.username})
        ]
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_post_group_page_contains_ten_records(self):
        response = self.client.get(reverse('post:group_posts',
                                           kwargs={'slug': self.group.slug}))
        self.assertEqual(len(response.context['page_obj']), 3)
