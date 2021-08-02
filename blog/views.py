import datetime

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import Post, Comment
from .form import PostForm, CommentForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from http import HTTPStatus
from django.http import JsonResponse, QueryDict
from django.forms import model_to_dict
import json


def date_converter(data):
    if isinstance(data, datetime.datetime):
        return data.__str__()


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    post_data = json.dumps([model_to_dict(post) for post in posts], default=date_converter)
    return JsonResponse({"post_data": post_data}, status=HTTPStatus.OK)


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return JsonResponse({"post_data": model_to_dict(post)}, status=HTTPStatus.OK)


@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            post_data = model_to_dict(post)
            return JsonResponse({'post_data': post_data}, status=HTTPStatus.CREATED)
        else:
            return JsonResponse({"message": "invalid Data"}, status=HTTPStatus.BAD_REQUEST)
    else:
        return JsonResponse({"message": "NOT POST"}, status=HTTPStatus.OK)


@require_http_methods(["PUT"])
def post_edit(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return JsonResponse(data={}, status=404)
    request_body = json.loads(request.body.decode("utf-8").replace("'", '"'))

    try:
        post.title = request_body["title"]
        post.text = request_body["text"]
    except KeyError:
        return JsonResponse(data={}, status=400)
    else:
        post.save()
    return JsonResponse(data={}, status=200)


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
