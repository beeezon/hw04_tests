import shutil
import tempfile
import time
from audioop import reverse

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адреса
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.outcast_group = Group.objects.create(
            title='Плохая группа',
            slug='outcast_slug',
            description='просто описание',
        )

        cls.post_1 = Post.objects.create(
            text='Тестовый текст 1',
            author=cls.user,
            group=cls.group,
        )
        time.sleep(0.1)
        cls.post_2 = Post.objects.create(
            text='Тестовый текст 2',
            author=cls.user,
            group=cls.group
        )
        time.sleep(0.1)

        small_gif = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post_image = Post.objects.create(
            text='Тестовый текст 3, c картинкой',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )
        cls.post_count = len(Post.objects.all())

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.authorized_client = Client()

        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        sample_post_create = 'posts/create_post.html'
        sample_post_edit = 'posts/create_post.html'
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list', kwargs={
                'slug': 'test_slug'}),
            'posts/profile.html': reverse('posts:profile', kwargs={
                'username': 'TestUser'}),
            'posts/post_detail.html': reverse('posts:post_detail', kwargs={
                'post_id': '1'}),
            sample_post_create: reverse('posts:post_create'),
            sample_post_edit: reverse('posts:post_edit', kwargs={
                'post_id': '1'}),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][2].text
        index_post = self.post_1.text
        self.assertEqual(index_post, first_object)

    def test_group_list(self):
        """Шаблон group_lis сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}))
        first_object = response.context['page_obj'][2].text
        group_post = self.post_1.text
        self.assertEqual(group_post, first_object)

    def test_profile(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'TestUser'}))
        first_object = response.context['page_obj'][2].text
        profile_post = self.post_1.text
        self.assertEqual(profile_post, first_object)

    def test_group_check_in(self):
        '''Проверка наличия групп в нужных шаблонах'''
        templates = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={'username': 'TestUser'})
        ]
        for index in templates:
            response = self.guest_client.get(index)
            self.assertIn(self.post_1, response.context['page_obj'])

    def test_group_check_not_in(self):
        '''Проверка отсутствия групп в ненужных шаблонах'''
        templates = reverse('posts:group_list', kwargs={'slug': 'test_slug'})
        response = self.guest_client.get(templates)
        self.assertNotIn(self.group, response.context['page_obj'])

    def test_image_index(self):
        '''Проверка вывода в контекст изображений на главной странице.'''
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0].image
        index_post = self.post_image.image
        self.assertEqual(index_post, first_object)

    def test_image_profile(self):
        '''Проверка вывода в контекст изображений на страницы профайла.'''
        response = self.authorized_client.get(reverse('posts:profile', kwargs={
            'username': 'TestUser'}))
        first_object = response.context['page_obj'][0].image
        image_profile_post = self.post_image.image
        self.assertEqual(image_profile_post, first_object)

    def test_image_group_list(self):
        '''Проверка вывода в контекст изображений на страницы группы.'''
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}))
        first_object = response.context['page_obj'][0].image
        image_group_list = self.post_image.image
        self.assertEqual(image_group_list, first_object)

    def test_image_post_detail(self):
        '''Проверка вывода в контекст изображений
        на страницы отдельного поста.'''
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '3'}))
        first_object = response.context['post'].image
        index_post = self.post_image.image

        self.assertEqual(index_post, first_object)

    def test_kesh(self):
        '''Тестирование кеша главной страницы.'''
        response = self.authorized_client.get(reverse('posts:index'))
        print(response)
