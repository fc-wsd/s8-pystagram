from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotFound
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

#from photos.models import Post
from .models import Post
from .models import Tag
from .models import Comment
from .models import Category
from .forms import PostForm
from .forms import CommentForm

@login_required
def create_post(request):
    # if not request.user.is_authenticated():
    #     raise Exception('누구세요?')

    if request.method == 'GET':
        form = PostForm()
    elif request.method == 'POST':
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            tag_text = form.cleaned_data.get('tagtext', '')
            tags = tag_text.split(',')
            for _tag in tags:
                _tag = _tag.strip()
                tag, _ = Tag.objects.get_or_create(name=_tag, defaults={'name': _tag})
                post.tags.add(tag)

            return redirect('photos:view', pk=post.pk)

    ctx = {
        'form': form,
    }
    return render(request, 'edit_post.html', ctx)


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'edit_post.html'

# create_post = PostCreateView.as_view()

@login_required
def edit_post(request, pk):
    if request.method == 'GET':
        post = get_object_or_404(Post, pk=pk)
        form = PostForm(instance=post)
    elif request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = get_object_or_404(Post, pk=pk)
            category = Category(request.POST.get('category'))
            post.category = category
            post.content = request.POST.get('content')
            post.image = request.POST.get('image')
            post.user = request.user
            post.save()

            tag_text = form.cleaned_data.get('tagtext', '')
            tags = tag_text.split(',')
            for _tag in tags:
                _tag = _tag.strip()
                tag, _ = Tag.objects.get_or_create(name=_tag, defaults={'name': _tag})
                post.tags.add(tag)

            return redirect('photos:view', pk=post.pk)

    ctx = {
        'form': form,
    }
    return render(request, 'edit_post.html', ctx)


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'GET':
        return redirect(post)
    elif request.method == 'POST':
        if request.user != post.user:
            return HttpResponseForbidden()
        post.delete()
        return redirect('photos:list')


from pystagram.sample_exceptions import HelloWorldError

def list_posts(request):
    raise HelloWorldError('으악, 뭔가 문제가 있다.')

    page = request.GET.get('page', 1)
    per_page = 2

    posts = Post.objects \
                .all() \
                .order_by('-created_at', '-pk')

    pg = Paginator(posts, per_page)
    try:
        contents = pg.page(page)
    except PageNotAnInteger:
        contents = pg.page(1)
    except EmptyPage:
        contents = []

    ctx = {
        'posts': contents,
    }
    return render(request, 'list.html', ctx)


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'list.html'
    paginate_by = 2
    # queryset = Post.objects.order_by('-created_at')

    def get_queryset(self):
        return Post.objects.order_by('-created_at')


# list_posts = PostListView.as_view()


@login_required
def view_post(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return HttpResponseNotFound()

    if request.method == 'GET':
        form = CommentForm()
    elif request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect(post)
    ctx = {
        'post': post,
        'comment_form': form,
    }
    return render(request, 'view.html', ctx)


@login_required
def delete_comment(request, pk):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()

    return redirect(comment.post)
