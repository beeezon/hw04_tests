from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Group, Post, User, Follow

NUMBER_DISPLAYED_OBJECTS = 10


@cache_page(20, key_prefix='index_page')
def index(request):
    post = Post.objects.all()
    page_obj = paginator(post, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts_list(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginator(posts, request)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_count = author.posts.count()
    posts = Post.objects.filter(author__username=username)
    page_obj = paginator(posts, request)
    is_follower = Follow.objects.filter(
        user=request.user,
        author=get_object_or_404(User, username=username)
    ).exists() if request.user.is_authenticated else False
    if is_follower:
        following = True
    else:
        following = False
    context = {
        'author': author,
        'post_list': posts_count,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    '''Выводим один конкретный пост.'''
    post = get_object_or_404(Post, pk=post_id)
    count_posts = post.author.posts.count()
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'count_posts': count_posts,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:profile', request.user.username)

    form = PostForm()
    contex = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', contex)


@login_required
def post_edit(request, post_id):
    editable_post = get_object_or_404(Post, pk=post_id)
    if request.user != editable_post.author:
        return HttpResponseRedirect(
            reverse('posts:post_detail', args=[post_id]))
    is_edit = True
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=editable_post,
    )
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(
            reverse('posts:post_detail', args=[post_id]))
    form = PostForm(instance=editable_post)
    contex = {
        'form': form,
        'is_edit': is_edit,
    }
    return render(request, 'posts/create_post.html', contex)


def paginator(post, request):
    paginator_object = Paginator(post, NUMBER_DISPLAYED_OBJECTS)
    page_number = request.GET.get('page')
    page_obj = paginator_object.get_page(page_number)
    return page_obj


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, pk=post_id)
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    '''Страница авторов, на которые подписан пользователь.'''
    post = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(post, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    '''Подписаться на автора.'''
    user = request.user
    author = User.objects.get(username=username)
    is_follower = Follow.objects.filter(user=user, author=author)
    if user != author and not is_follower:
        Follow.objects.create(user=user, author=author)
    return HttpResponseRedirect(reverse('posts:profile', args=[username]))


@login_required
def profile_unfollow(request, username):
    '''Отписка от автора.'''
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    if is_follower.exists():
        is_follower.delete()
    return HttpResponseRedirect(reverse(
        'posts:profile', kwargs={'username': author}))
