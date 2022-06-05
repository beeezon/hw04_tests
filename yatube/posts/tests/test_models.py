from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текстcболепятнадцатьюсимволоами',
        )

    def test_correct_object_name_post(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name_post = post.text[:15]
        self.assertEqual(expected_object_name_post, str(post))

    def test_correct_object_name_group(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = PostModelTest.group
        expected_object_name_group = group.title
        self.assertEqual(expected_object_name_group, str(group))

    def test_help_text_post(self):
        """Проверяем, что help_text соответствует"""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

    def test_verbose_name(self):
        """Проверяем, что verbose_name соответствует"""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)
