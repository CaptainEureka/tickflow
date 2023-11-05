import datetime as dt
from typing import Any, Dict
from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient

from tickflow.core.models.models import TaskId, TaskStatus


@pytest.mark.integ
class TestCreateTask:
    @pytest.fixture(scope="class")
    def created_task(self, test_client: TestClient) -> httpx.Response:
        task_data = {
            "userId": 1,
            "description": "Finish writing tests",
            "title": "Write Tests",
            "dueDate": dt.datetime.now().timestamp(),
        }
        response = test_client.post("/tasks/", json=task_data)
        print(response.json())
        return response

    def test_create_task_success(self, created_task):
        assert created_task.status_code == 201

    def test_create_task_user_id(self, created_task):
        assert created_task.json()["userId"] == 1

    def test_create_task_description(self, created_task):
        assert created_task.json()["description"] == "Finish writing tests"

    def test_create_task_title(self, created_task):
        assert created_task.json()["title"] == "Write Tests"

    def test_create_task_status(self, created_task):
        assert created_task.json()["status"] == TaskStatus.TODO


class TestReadTask:
    @pytest.fixture(scope="class")
    def existing_task_id(self, test_client: TestClient):
        # Create a task and return its ID
        # In a real test, you might want to insert the task directly into the test database
        # and return the ID of that task
        task_data = {
            "userId": 1,
            "description": "Task to read",
            "title": "Read Task",
            "status": TaskStatus.TODO,
        }
        response = test_client.post("/tasks/", json=task_data)
        assert response.status_code == 201
        return response.json()["taskId"]

    def test_read_task_response_code(self, test_client: TestClient, existing_task_id):
        response = test_client.get(f"/tasks/{existing_task_id}")
        assert response.status_code == 200

    def test_read_task_content(self, test_client: TestClient, existing_task_id):
        response = test_client.get(f"/tasks/{existing_task_id}")
        assert "taskId" in response.json()
        assert response.json()["taskId"] == existing_task_id

    def test_read_task_not_found(self, test_client: TestClient):
        non_existent_task_id = uuid4()
        response = test_client.get(f"/tasks/{non_existent_task_id}")
        assert response.status_code == 404


class TestReadAllTasks:
    @pytest.fixture(scope="class")
    def read_all_tasks(self, test_client) -> httpx.Response:
        return test_client.get("/tasks/")

    def test_read_all_tasks_success(self, read_all_tasks: httpx.Response):
        assert read_all_tasks.status_code == 200

    def test_read_all_tasks_body(self, read_all_tasks: httpx.Response):
        assert isinstance(read_all_tasks.json(), list)


class TestUpdateTask:
    @pytest.fixture
    def task_data(self) -> Dict[str, Any]:
        return {
            "userId": 1,
            "description": "Task to update",
            "title": "Update Task",
            "status": TaskStatus.TODO,
        }

    @pytest.fixture
    def task_to_update(self, task_data: Dict[str, Any], test_client: TestClient) -> str:
        # Create a task and return its ID and the original data
        response = test_client.post("/tasks/", json=task_data)
        assert response.status_code == 201
        task = response.json()
        return task["taskId"]

    def test_update_task_response_code(
        self, test_client: TestClient, task_to_update: str
    ):
        update_task = {
            "title": "Updated Title",
        }
        response = test_client.put(f"/tasks/{task_to_update}", json=update_task)
        assert response.status_code == 200

    def test_update_task_content(self, test_client: TestClient, task_to_update: str):
        update_task = {"title": "Updated Title"}
        response = test_client.put(f"/tasks/{task_to_update}", json=update_task)
        assert response.json()["title"] == "Updated Title"


class TestDeleteTask:
    @pytest.fixture
    def task_data(self) -> Dict[str, Any]:
        return {
            "userId": 1,
            "description": "Task to delete",
            "title": "Delete Task",
            "status": TaskStatus.TODO,
        }

    @pytest.fixture(scope="function")
    def existing_task_id(self, task_data: Dict[str, Any], test_client: TestClient):
        # Create a task and return its ID
        # In a real test, you might want to insert the task directly into the test database
        # and return the ID of that task
        response = test_client.post("/tasks/", json=task_data)
        assert response.status_code == 201
        return response.json()["taskId"]

    def test_delete_task_response_code(
        self, test_client: TestClient, existing_task_id: TaskId
    ):
        response = test_client.delete(f"/tasks/{existing_task_id}")
        assert response.status_code == 200

    def test_delete_task_not_found(self, test_client: TestClient):
        non_existent_task_id = uuid4()
        response = test_client.delete(f"/tasks/{non_existent_task_id}")
        assert response.status_code == 404

    def test_delete_task_content(
        self, test_client: TestClient, existing_task_id: TaskId
    ):
        _ = test_client.delete(f"/tasks/{existing_task_id}")

        # Verify that the task no longer exists
        get_response = test_client.get(f"/tasks/{existing_task_id}")
        assert get_response.status_code == 404
