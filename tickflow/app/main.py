from typing import List

from fastapi import FastAPI, HTTPException, status

from tickflow.core.client import InMemoryTaskService
from tickflow.core.models import Task, CreateTask, TaskId, UpdateTask

app = FastAPI()

task_service = InMemoryTaskService()


@app.post("/tasks/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: CreateTask) -> Task:
    return task_service.create_task(task)


@app.get("/tasks/", response_model=List[Task])
def read_tasks() -> List[Task]:
    return task_service.read_all_tasks()


@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: TaskId) -> Task:
    task = task_service.read_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    return task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: TaskId, task_update: UpdateTask) -> Task:
    updated_task = task_service.update_task(task_id, task_update)
    if updated_task:
        return updated_task

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


@app.delete("/tasks/{task_id}", response_model=Task)
def delete_task(task_id: TaskId) -> Task:
    deleted_task = task_service.delete_task(task_id)

    if deleted_task:
        return deleted_task

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
