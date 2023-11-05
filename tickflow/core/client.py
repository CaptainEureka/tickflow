from typing import List, Optional, Protocol, Sequence
from uuid import UUID

from tickflow.core.models.models import CreateTask, Task, UpdateTask


class ITaskService(Protocol):
    def read_task(self, task_id: UUID) -> Optional[Task]:
        ...

    def read_all_tasks(self) -> Sequence[Task]:
        ...

    def create_task(self, task: Task) -> Task:
        ...

    def update_task(self, task_id: UUID, task_update: UpdateTask) -> Optional[Task]:
        ...

    def delete_task(self, task_id: UUID) -> Optional[Task]:
        ...


class InMemoryTaskService(ITaskService):
    def __init__(self) -> None:
        self.db: List[Task] = []

    def read_task(self, task_id: UUID) -> Optional[Task]:
        return next(filter(lambda task: task.id == task_id, self.db), None)

    def read_all_tasks(self) -> Sequence[Task]:
        return self.db

    def create_task(self, task: CreateTask) -> Task:
        new_task = task.into(target_model_type=Task)
        self.db.append(new_task)
        return new_task

    def update_task(self, task_id: UUID, task_update: UpdateTask) -> Optional[Task]:
        for ix, task in enumerate(self.db):
            if task.id == task_id:
                exclude_fields = task_update.model_fields_set
                old_task = self.db[ix].model_dump(exclude=exclude_fields, by_alias=True)
                updated_task_data = {
                    **task_update.model_dump(exclude_unset=True, exclude_none=True),
                    **old_task,
                }
                updated_task = Task.model_validate(updated_task_data)
                return updated_task

        return None

    def delete_task(self, task_id: UUID) -> Optional[Task]:
        for ix, task in enumerate(self.db):
            if task.id == task_id:
                return self.db.pop(ix)

        return None
