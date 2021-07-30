from django.test import TestCase
from .models import Post, Comment
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from http import HTTPStatus
import json


class TestPost(TestCase):
    def _create_new_post(self, user, title, text):
        post = Post.objects.create(
            author=self.user, title=title, text=text, published_date=timezone.now()
        )
        return post

    def setUp(self):
        self.username = "Testuser"
        self.password = "Test123"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user.set_password(self.password)
        self.user.save()

    def test_post_list_should_return_200_ok(self):
        # Given : 새로운 Post 생성
        for _ in range(30):
            self._create_new_post(self.user, "title", "text")

        # When : Post 모두 조회
        response = self.client.get(reverse("post_list"))

        # Then : Post들이 잘 조회되는지 확인
        data = json.loads(response.json()["post_data"])

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(data), 30)

    def test_one_post_should_return_200_ok_and_instance_should_equal_given(self):
        # Given : get할 새로운 post 미리 생성
        post = self._create_new_post(self.user, "test_title", "test_text")

        # When : 생성한 post 조회
        response = self.client.get(reverse("post_detail", kwargs={"pk": post.pk}))

        # Then : 생성한 post 와 조회한 post를 비교
        post_data = json.loads(response.json()["post_data"])[0]["fields"]

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post_data["author"], self.user.pk)
        self.assertEqual(post_data["title"], post.title)
        self.assertEqual(post_data["text"], post.text)

    def test_not_exist_post_return_404_not_found(self):
        # Given : 존재하지 않는 post pk
        sample_pk = 1234

        # When : 존재하지 않는 post 조회
        response = self.client.get(reverse("post_detail", kwargs={"pk": sample_pk}))

        # The : NOTFOUND 반환
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_new_return_200_ok_and_instance_should_equal_given(self):
        # Given : 로그인 하고 난 후에 post 데이터 생성
        self.client.login(username=self.username, password=self.password)
        data = {"title": "test_title", "text": "test_text"}

        # When : post 생성 요청
        response = self.client.post(reverse("post_new"), data=data)

        # Then : 제대로 생성되었는지 확인
        post_data = json.loads(response.json()["post_data"])[0]
        post = post_data["fields"]

        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(post["author"], self.user.pk)
        self.assertEqual(post["title"], data["title"])
        self.assertEqual(post["text"], data["text"])
        self.assertIsNone(post["published_date"])

    def test_post_new_if_not_login_should_return_302_found(self):
        # Given : 로그인 안하고 post 데이터 생성
        data = {"title": "login_page_test", "text": "login_page_test_text"}

        # When : post 생성 요청
        response = self.client.post(reverse("post_new"), data=data)

        # Then : 제대로 redirect 되었는지 확인
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_new_wiht_bad_data_should_return_400_bad_request(self):
        # Given : 로그인 + 잘못된 형식의 데이터
        self.client.login(username=self.username, password=self.password)
        data = {"title": "there is no TEXT"}

        # When : post 생성 요청
        response = self.client.post(reverse("post_new"), data=data)

        # Then : Post 생성되지 않고, Badrequest 반환
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
