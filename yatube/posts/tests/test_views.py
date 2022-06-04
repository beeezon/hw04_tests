from audioop import reverse

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


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
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.post_2 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )
        cls.post_count = len(Post.objects.all())

    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

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
        first_object = response.context['page_obj'][0]
        test_contex = {
            first_object.text: self.post_1.text,
            first_object.author: self.post_1.author,
            first_object.pub_date: self.post_1.pub_date,
            first_object.group.slug: self.post_1.group.slug,
        }
        for request, contex in test_contex.items():
            with self.subTest(contex=contex):
                self.assertEqual(request, contex)

    def test_group_list(self):
        """Шаблон group_lis сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}))
        first_object = response.context['page_obj'][0].text
        group_post = self.post_1.text
        self.assertEqual(group_post, first_object)

    def test_profile(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'TestUser'}))
        first_object_1 = response.context['author']
        first_object_2 = response.context['page_obj'][0]
        first_object_3 = response.context['post_list']
        test_contex = {
            first_object_1.username: self.user.username,
            first_object_2.author: self.post_1.author,
            first_object_2.pub_date: self.post_1.pub_date,
            first_object_2.text: self.post_1.text,
            first_object_3: self.post_count
        }
        for request, contex in test_contex.items():
            with self.subTest(contex=contex):
                self.assertEqual(request, contex)

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
