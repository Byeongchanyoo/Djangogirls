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
        return JsonResponse(data={}, status=HTTPStatus.NOT_FOUND)
    request_body = json.loads(request.body.decode("utf-8").replace("'", '"'))

    try:
        post.title = request_body["title"]
        post.text = request_body["text"]
    except KeyError:
        return JsonResponse(data={}, status=HTTPStatus.BAD_REQUEST)
    else:
        post.save()
    return JsonResponse(data={}, status=HTTPStatus.OK)
