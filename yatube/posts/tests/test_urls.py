from django.test import Client, TestCase
from django.http import HttpResponseRedirect
from django.urls import reverse
from ..models import Group, Post, User
from http import HTTPStatus
from django.urls import include


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адреса
        cls.user = User.objects.create_user(username='TestUser')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
        )
        cls.public_set = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/TestUser/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
        }
        cls.private_set = {
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        cls.forwarding = {
            '/create/': f"{reverse('users:login')}?next=/create/",
            '/posts/1/edit/': f"{reverse('users:login')}?next=/posts/1/edit/",
        }

    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authorized_user_templates(self):
        """Проверка соответствующих шаблонов авторизованного пользователя."""
        for url, sample in self.public_set.items():
            with self.subTest(sample=sample):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, sample)

    def test_guest_user_templates(self):
        """Проверка соответствующих шаблонов гостевого пользователя."""
        for url, sample in self.private_set.items():
            with self.subTest(sample=sample):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, sample)

    def test_page_access_check(self):
        """Проверка доступности страниц неавторизаванным пользователем."""
        for url, reply in self.public_set.items():
            with self.subTest(reply=reply):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unauthorized_user_check(self):
        """Проверка доступа неавторизованного пользователя."""
        for url, reply in self.forwarding.items():
            with self.subTest(reply=reply):
                response = self.guest_client.get(url)
                self.assertRedirects(response, reply)

    def test_error_404(self):
        """Проверка вызова несуществующей страницы."""
        response = self.guest_client.get('/error_404/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_homepage(self):
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
