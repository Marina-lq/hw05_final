from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect

from .forms import PostForm, CommentForm
from .models import Group, Post, Follow

User = get_user_model()

POSTS_PER_PAGE = 10


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'paginator': paginator
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    paginator = Paginator(group.posts.all(), 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    posts = group.posts.all()[:POSTS_PER_PAGE]
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
        'paginator': paginator
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    author = User.objects.get(username=username)
    posts = Post.objects.filter(author=author)
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    post_count = posts.count
    user = request.user
    following = user.is_authenticated and user_profile.following.exists()
    context = {
        'author': author,
        'page_obj': page_obj,
        'post_count': post_count,
        'following': following
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    post_count = Post.objects.filter(author=post.author).count()
    comments = post.comments.all()
    context = {
        'post': post,
        'post_count': post_count,
        'comments': comments,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/includes/post_create.html',
                               {'form': form}
                      )
    form.instance.author = request.user
    form.save()
    return redirect('post:profile', request.user)


@login_required
def post_edit(request, post_id):
    post = Post.objects.get(pk=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form = form.save(False)
        form.author = request.user
        form.save()
        return redirect('post:post_detail', post_id=post.id)
    return render(
        request,
        'posts/includes/post_create.html',
        {'form': form, 'post': post}
    )


@login_required
def add_comment(request, post_id):
    # Получите пост
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
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'paginator': paginator}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    profile_follow = Follow.objects.get(author=author,
                                        user=request.user)
    if Follow.objects.filter(pk=profile_follow.pk).exists():
        profile_follow.delete()
    return redirect('posts:profile', username=username)
