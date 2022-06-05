from audioop import reverse

from django.test import TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PaginatorViewsTest(TestCase):

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

        cls.post_list = [
            Post.objects.create(
                text=f"Тестовый текст {i}",
                author=cls.user,
                group=cls.group
            ) for i in range(13)
        ]

    def test_first_page_contains_ten_records(self):
        '''Проверка вывода 10 постов. Корректная работа paginatora'''
        test_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username})

        ]
        for response in test_list:
            with self.subTest(response=response):
                response = self.client.get(response)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        '''Проверка вывода оставшихся 3 постов. Корректная работа paginatora'''
        test_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username})

        ]
        for response in test_list:
            with self.subTest(response=response):
                response = self.client.get(response + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
