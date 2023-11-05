import datetime as dt
import uuid
from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Annotated, List, NewType, Optional, Self, Type, TypeVar

from pydantic import BaseModel, Field, ValidationError, computed_field

T = TypeVar("T", bound=BaseModel)

UserId = NewType("UserId", int)
TaskId = NewType("TaskId", uuid.UUID)

AnnotatedTaskId = Annotated[
    TaskId,
    Field(default_factory=uuid.uuid4, alias="taskId", validate_default=True),
]
AnnotatedUserId = Annotated[UserId, Field(..., alias="userId")]


class ConvertibleModel(BaseModel, ABC):
    @abstractmethod
    def into(self: Self, target_model_type: Type[T]) -> T:
        ...

    def _validate_and_convert(self: Self, target_model_type: Type[T]) -> T:
        try:
            return target_model_type.model_validate(
                self.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)
            )
        except ValidationError as err:
            raise ValueError(
                f"Data validation failed during conversion: {err}"
            ) from err


class TaskStatus(StrEnum):
    TODO = "todo"
    DONE = "done"
    IN_PROGRESS = "in_progress"
    # BLOCKED = "blocked"
    # ARCHIVED = "archived"
    # REVIEW = "review"


class Task(ConvertibleModel):
    id: AnnotatedTaskId
    user_id: AnnotatedUserId
    description: str = Field(...)
    title: str = Field(...)
    status: TaskStatus = Field(default=TaskStatus.TODO)
    due_date: Optional[dt.datetime] = Field(None, alias="dueDate")
    created_at: Optional[dt.datetime] = Field(
        default_factory=dt.datetime.now, alias="createdAt"
    )
    updated_at: Optional[dt.datetime] = Field(None, alias="updatedAt")

    def into(self: Self, target_model_type: Type[T]) -> T:
        return self._validate_and_convert(target_model_type)


class CreateTask(ConvertibleModel):
    user_id: AnnotatedUserId
    description: str = Field(...)
    title: str = Field(...)
    status: Optional[TaskStatus] = Field(default=None)
    due_date: Optional[dt.datetime] = Field(None, alias="dueDate")

    def into(self: Self, target_model_type: Type[T]) -> T:
        return self._validate_and_convert(target_model_type)


class UpdateTask(BaseModel):
    description: Optional[str] = Field(None)
    title: Optional[str] = Field(None)
    status: Optional[TaskStatus] = Field(None)
    due_date: Optional[dt.datetime] = Field(None, alias="dueDate")

    @computed_field(alias="updatedAt")
    @property
    def updated_at(self) -> dt.datetime:
        return dt.datetime.now()


class User(ConvertibleModel):
    id: AnnotatedUserId
    username: str = Field(..., alias="userName")
    created_at: Optional[dt.datetime] = Field(
        default_factory=dt.datetime.now, alias="createdAt"
    )
    tasks: List[Task]

    def into(self: Self, target_model_type: Type[T]) -> T:
        return self._validate_and_convert(target_model_type)
