from sqlalchemy import Column, DateTime, Enum, Integer, MetaData, String, Table

from tickflow.core.models.models import TaskStatus

metadata = MetaData()

tasks_table = Table(
    "tasks",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, nullable=False),
    Column("title", String, nullable=False),
    Column("description", String, nullable=True),
    Column("status", Enum(TaskStatus), default=TaskStatus.TODO, nullable=False),
    Column("due_date", DateTime, nullable=True),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=True),
)
