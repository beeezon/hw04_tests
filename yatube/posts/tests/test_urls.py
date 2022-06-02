# posts/tests/test_urls.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


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

    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_homepage(self):
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_error_404(self):
        """Проверка вызова несуществующей страницы."""
        response = self.guest_client.get('/error_404/')
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        html_1 = 'posts/create_post.html'
        html_2 = html_1
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test_slug/',
            'posts/profile.html': '/profile/TestUser/',
            'posts/post_detail.html': '/posts/1/',
            html_1: '/create/',
            html_2: '/posts/1/edit/',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_page_access_check(self):
        """Проверка доступности страниц неавторизаванным пользователем."""
        query_order = {
            '/': 200,
            '/group/test_slug/': 200,
            '/profile/TestUser/': 200,
            '/posts/1/': 200,
        }
        for request_page, reply in query_order.items():
            with self.subTest(url=reply):
                response = self.guest_client.get(request_page)
                self.assertEqual(response.status_code, reply)

    def test_unauthorized_user_check(self):
        """Проверка доступа неавторизованного пользователя."""
        query_order = {
            '/create/': '/auth/login/?next=/create/',
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/',
        }
        for request_page, reply in query_order.items():
            with self.subTest(url=reply):
                response = self.guest_client.get(request_page)
                self.assertRedirects(response, reply)
