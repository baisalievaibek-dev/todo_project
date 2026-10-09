from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Task


class TaskApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="intern", password="test-password"
        )
        self.client.force_authenticate(user=self.user)

    def test_task_crud(self):
        created = self.client.post(
            "/api/tasks/",
            {"title": "Read docs", "description": "DRF", "completed": False},
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        task_id = created.data["id"]
        self.assertIn("created_at", created.data)

        retrieved = self.client.get(f"/api/tasks/{task_id}/")
        self.assertEqual(retrieved.status_code, status.HTTP_200_OK)

        updated = self.client.patch(
            f"/api/tasks/{task_id}/", {"completed": True}, format="json"
        )
        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        self.assertTrue(updated.data["completed"])

        deleted = self.client.delete(f"/api/tasks/{task_id}/")
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=task_id).exists())

    def test_list_filters_by_status_and_is_paginated(self):
        Task.objects.bulk_create(
            [
                Task(title=f"Task {index}", completed=index % 2 == 0)
                for index in range(12)
            ]
        )

        response = self.client.get("/api/tasks/?completed=true&page_size=2")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 6)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertTrue(all(task["completed"] for task in response.data["results"]))

    def test_status_filter_accepts_boolean_like_values(self):
        Task.objects.bulk_create(
            [
                Task(title=f"Task {index}", completed=index % 2 == 0)
                for index in range(4)
            ]
        )

        response = self.client.get("/api/tasks/?completed=TRUE")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(task["completed"] for task in response.data["results"]))

    def test_invalid_status_filter_returns_bad_request(self):
        response = self.client.get("/api/tasks/?completed=sometimes")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/tasks/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_session_login_can_access_api(self):
        self.client.force_authenticate(user=None)

        self.assertTrue(
            self.client.login(username="intern", password="test-password")
        )
        response = self.client.get("/api/tasks/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_can_be_obtained_and_used(self):
        self.client.force_authenticate(user=None)
        token_response = self.client.post(
            "/api/token/", {"username": "intern", "password": "test-password"}
        )
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token_response.data['token']}"
        )
        response = self.client.get("/api/tasks/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)