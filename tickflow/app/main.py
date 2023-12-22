from typing import List

from fastapi import FastAPI, HTTPException, status
from flusso.option import Nothing, Some

from tickflow.core.client import DbTaskService, InMemoryTaskService
from tickflow.core.models import CreateTask, Task, TaskId, UpdateTask
from tickflow.database.dependencies import get_database, get_tasks_table

app = FastAPI()

# task_service = InMemoryTaskService()
task_service = DbTaskService


@app.post("/tasks/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: CreateTask) -> Task:
    return task_service.create_task(task)


@app.get("/tasks/", response_model=List[Task])
def read_tasks() -> List[Task]:
    return task_service.read_all_tasks()


@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: TaskId) -> Task:
    match task_service.read_task(task_id):
        case Some(task):
            return task
        case Nothing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: TaskId, task_update: UpdateTask) -> Task:
    match task_service.update_task(task_id, task_update):
        case Some(updated_task):
            return updated_task
        case Nothing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )


@app.delete("/tasks/{task_id}", response_model=Task)
def delete_task(task_id: TaskId) -> Task:
    match task_service.delete_task(task_id):
        case Some(deleted_task):
            return deleted_task
        case Nothing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )
