from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow


@cache_page(20, key_prefix=settings.PAGE)
def index(request):
    title = 'Последние обновления на сайте'
    template = 'posts/index.html'
    posts = Post.objects.all()
    paginator = Paginator(posts, settings.PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, settings.PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    template = 'posts/profile.html'
    posts = Post.objects.filter(author=author.id)
    paginator = Paginator(posts, settings.PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    count = posts.count()
    following = (request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=author).exists())
    context = {
        'author': author,
        'page_obj': page_obj,
        'count': count,
        'following': following
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comments = post.comments.all().select_related('author')
    template = 'posts/post_detail.html'
    count = Post.objects.filter(author__username=post.author).count()
    context = {
        'post': post,
        'count': count,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required()
def post_create(request):
    template = 'posts/create_post.html'
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('posts:profile', request.user.username)
        return render(request, template, {'form': form})
    form = PostForm()
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    if request.user.id == post.author.id:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            post = form.save()
            return redirect('posts:post_detail', post.id)
        context = {
            'form': form,
            'post': post,
            'is_edit': is_edit
        }
        return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    follow_posts = Post.objects.filter(author__following__user=request.user)
    template = 'posts/follow.html'
    paginator = Paginator(follow_posts, settings.PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    if request.user.is_authenticated:
        if request.user == User.objects.get(username=username):
            return redirect(f'/profile/{username}/')
        else:
            if Follow.objects.filter(
                    user=request.user,
                    author=User.objects.get(username=username)
            ):
                return redirect(f'/profile/{username}/')
            else:
                Follow.objects.create(
                    user=request.user,
                    author=User.objects.get(username=username)
                )
                return redirect(f'/profile/{username}/')
    return redirect('/auth/login/')


@login_required
def profile_unfollow(request, username):
    follower = User.objects.get(username=username)
    Follow.objects.filter(user=request.user, author=follower).delete()
    return redirect('posts:follow_index')
