from email.headerregistry import Group

from django.contrib import admin

from .models import Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Создаем админ зону для постов."""
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'
    list_editable = ('group',)


class GroupAdmin(admin.ModelAdmin):
    """Создаем админ зону для групп."""
    list_display = ('title', 'slug', 'description')
    search_fields = ('title',)
    empty_value_display = '-пусто-'


admin.site.register(Group, GroupAdmin)
