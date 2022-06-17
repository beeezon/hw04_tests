import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
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

    def test_image_upload(self):
        '''Корректная загрузка изображения на странице.'''
        post_count = Post.objects.count()
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
        form_data = {
            'text': 'Добавляем картинку к форме',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'TestUser'}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Добавляем картинку к форме',
                group='1',
                image='posts/small.gif'
            ).exists()
        )

    def test_add_comment(self):
        '''Проверка создания комментария авторизованным пользователем.'''
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Комментарий к посту',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True,
        )
        '''Проверяем редрект на страницу profile.'''
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': '1'}))
        '''Проверяем изменение общего кол-ва постов.'''
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        '''Проверяем пост в БД с наличием нужных полей.'''
        self.assertTrue(
            Comment.objects.filter(
                text='Комментарий к посту',
            ).exists()
        )
        '''Проверяем попытку добавления комментария
        неавторизованного пользователя.'''

    def test_add_comment_error(self):
        '''Проверка создания комментария неавторизованным пользователем.'''
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Комментарий к посту',
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True,
        )
        '''Проверяем изменение общего кол-ва постов.'''
        self.assertNotEqual(Comment.objects.count(), comments_count + 1)
