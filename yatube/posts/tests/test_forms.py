from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.form = PostFormTests()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        '''При отправке валидной формы со страницы создания поста
        create_post создаётся новая запись в базе данных.'''
        post_count = Post.objects.count()
        form_data = {
            'text': 'Новый текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        '''Проверяем редрект на страницу profile.'''
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'TestUser'}))
        '''Проверяем изменение общего кол-ва постов.'''
        self.assertEqual(Post.objects.count(), post_count + 1)
        '''Проверяем пост в БД с наличием нужных полей.'''
        self.assertTrue(
            Post.objects.filter(
                text='Новый текст',
                group='1'
            ).exists()
        )

    def test_post_edit(self):
        '''Редактирование ранее созданного поста
        функцией post_edit проходит корректно.'''
        post_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': '1'}))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                text='Измененный текст',
                group='1'
            ).exists()
        )
