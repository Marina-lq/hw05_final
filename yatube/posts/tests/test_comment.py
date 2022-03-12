

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


from posts.models import Post
from posts.models import Comment

User = get_user_model()

class PostFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()
        self.post = Post.objects.create(
        author=self.user,
        text='Тестовый текст',
        )

    def test_create_comment(self): 
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый текст',
             'author': self.user,         
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment',args=[self.post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                     kwargs={
                    'post_id': self.post.pk}))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
               author=self.user,
               post=self.post.pk
            ).exists())
