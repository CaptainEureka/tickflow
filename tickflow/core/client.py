from typing import List, Optional, Protocol

from flusso.option import Nothing, Option, Some
from sqlalchemy import Table
from sqlalchemy.engine import Engine
from sqlalchemy.sql import delete, insert, select, update

from tickflow.core.models.models import CreateTask, Task, TaskId, UpdateTask


class ITaskService(Protocol):
    def read_task(self, task_id: TaskId) -> Option[Task]:
        ...

    def read_all_tasks(self) -> List[Task]:
        ...

    def create_task(self, task: Task) -> Task:
        ...

    def update_task(self, task_id: TaskId, task_update: UpdateTask) -> Optional[Task]:
        ...

    def delete_task(self, task_id: TaskId) -> Optional[Task]:
        ...


class InMemoryTaskService(ITaskService):
    def __init__(self) -> None:
        self.db: List[Task] = []

    def read_task(self, task_id: TaskId) -> Option[Task]:
        task = next(filter(lambda task: task.id == task_id, self.db), Nothing)
        return Some(task)

    def read_all_tasks(self) -> List[Task]:
        return self.db

    def create_task(self, task: CreateTask) -> Task:
        new_task = task.into(target_model_type=Task)
        self.db.append(new_task)
        return new_task

    def _save_task(self, task: Task) -> Option[Task]:
        new_db = [task if t.id == task.id else t for t in self.db]
        self.db = new_db
        return Some(task)

    def update_task(self, task_id: TaskId, task_update: UpdateTask) -> Option[Task]:
        task_option = self.read_task(task_id)

        return task_option.fmap(
            lambda task: (
                Task.model_validate(
                    {
                        **task_update.model_dump(exclude_unset=True, exclude_none=True),
                        **task.model_dump(
                            exclude=task_update.model_fields_set, by_alias=True
                        ),
                    }
                )
            )
        ).and_then(self._save_task)

    def delete_task(self, task_id: TaskId) -> Option[Task]:
        deleted_task = next(filter(lambda t: t.id == task_id, self.db), Nothing)
        self.db = [task for task in self.db if task.id != task_id]

        return Some(deleted_task)


class DbTaskService(ITaskService):
    def __init__(self, engine: Engine, tasks_table: Table):
        self.engine = engine
        self.tasks_table = tasks_table

    def create_task(self, task: Task) -> Task:
        # Use SQLAlchemy Core to insert a new task
        # Convert `task_data` to a format suitable for database insertion
        with self.engine.connect() as connection:
            connection.execute(insert(self.tasks_table).values(**task.model_dump()))
            return self.read_task(task.id)

    def read_task(self, task_id: int) -> Task:
        # Retrieve a task by ID using SQLAlchemy Core
        with self.engine.connect() as connection:
            result = connection.execute(
                select([self.tasks_table]).where(self.tasks_table.c.id == task_id)
            )
            return Task.model_validate(result.fetchone())

    def read_all_tasks(self) -> List[Task]:
        with self.engine.connect() as connection:
            result = connection.execute(select(self.tasks_table))

            return [Task.model_validate(row) for row in result.fetchall()]

    def update_task(self, task_id: TaskId, updated_task: UpdateTask) -> Task:
        # Update a task and return the updated task
        with self.engine.connect() as connection:
            connection.execute(
                update(self.tasks_table)
                .where(self.tasks_table.c.id == task_id)
                .values(**updated_task.model_dump())
            )
            return self.read_task(task_id)

    def delete_task(self, task_id: TaskId) -> None:
        # Delete a task by ID
        with self.engine.connect() as connection:
            connection.execute(
                delete(self.tasks_table).where(self.tasks_table.c.id == task_id)
            )
