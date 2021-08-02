from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Post, Comment
from .form import PostForm, CommentForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from http import HTTPStatus
from django.http import JsonResponse
import json


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    post_data = json.dumps([post.make_json() for post in posts])
    return JsonResponse({"post_data": post_data}, status=HTTPStatus.OK)


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return JsonResponse({"post_data": post.make_json()}, status=HTTPStatus.OK)


@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            post_data = post.make_json()
            return JsonResponse({'post_data': post_data}, status=HTTPStatus.CREATED)
        else:
            return JsonResponse({"message": "invalid Data"}, status=HTTPStatus.BAD_REQUEST)
    else:
        return JsonResponse({"message": "NOT POST"}, status=HTTPStatus.OK)



@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})


@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})


def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)


@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('post_list')


def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('post_detail', pk=comment.post.pk)
