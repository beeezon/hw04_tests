from django import forms
from django.forms import Select, Textarea

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

        widgets = {
            'text': Textarea(attrs={
                'class': "form-control",
                'name': "text",
                'required id': "id_text",
                'cols': "40",
                'rows': "10",
            }),
            'group': Select(attrs={
                'class': "form-control",
                'name': "group",
                'id': "id_group",
            })
        }
