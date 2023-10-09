from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    CreateView, DetailView, UpdateView, DeleteView, ListView
)
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import Http404
from django.core.exceptions import PermissionDenied

from .forms import CommentForm, PostForm
from blog.models import Post, Category, Comment
from django.contrib.auth import get_user_model


User = get_user_model()


COUNT_POSTS = 10


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = COUNT_POSTS
    ordering = '-pub_date'
    queryset = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date').annotate(comment_count=Count('comment'))


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        if (
            post.author == self.request.user
            or post.is_published and post.pub_date <= timezone.now()
            and post.category.is_published
        ):
            return post
        else:
            raise Http404("Page not found.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comment.select_related('author')
        )
        return context


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True)
    post_list = Post.objects.filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'category': category, 'page_obj': page_obj}
    return render(request, template, context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user.username
        return reverse_lazy('blog:profile', kwargs={'username': username})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = '__all__'
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Проверка авторства
        if obj.author != self.request.user:
            raise PermissionDenied
        return obj


class RegistrationCreateView(LoginRequiredMixin, CreateView):
    model = User
    template_name = 'auth/registration.html'
    success_url = reverse_lazy('blog:index')


class ProfileDetailView(DetailView):
    model = User
    template_name = 'profile/profile_form.html'
    paginate_by = COUNT_POSTS
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        all_posts = Post.objects.filter(
            author=user).order_by('-pub_date').annotate(
                comment_count=Count('comment'))
        paginator = Paginator(all_posts, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'profile/edit_form.html'
    fields = ['first_name', 'last_name', 'username', 'email']
    success_url = reverse_lazy('blog:profile')

    def get_object(self, queryset=None):
        username = self.kwargs['username']
        return User.objects.get(username=username)

    def get_success_url(self):
        return reverse_lazy('blog:edit_profile',
                            kwargs={'username': self.request.user.username})


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


@login_required
def edit_comment(request, pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)

    if request.user != comment.author:
        return redirect('blog:post_detail', pk=pk)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', pk=pk)

    else:
        form = CommentForm(instance=comment)

    return render(request, 'posts/comment.html',
                  {'form': form, 'comment': comment, 'pk': pk})


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    post_id = comment.post.pk

    if request.user == comment.author:
        if request.method == 'POST':
            comment.delete()
            return redirect('blog:post_detail', pk=post_id)
    else:
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'posts/comment.html',
                  {'comment': comment, 'post_id': post_id})
