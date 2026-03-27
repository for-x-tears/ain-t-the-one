from unittest.mock import MagicMock
from uuid import uuid4
from app.services.task_service import TaskService
from app.schems import TaskCreate


def test_create_task():
    mock_repo = MagicMock()
    owner_id = uuid4()

    
    fake_task = MagicMock()
    fake_task.id = uuid4()
    fake_task.title = "Тестовая задача"
    fake_task.description = "описание"
    fake_task.completed = False
    fake_task.owner_id = owner_id
    mock_repo.create.return_value = fake_task

    
    service = TaskService(mock_repo)

    task_data = TaskCreate(
        title="Тестовая задача",
        description="описание",
        completed=False
    )

    result = service.create_task(task_data, owner_id=owner_id)

    
    mock_repo.create.assert_called_once_with(task_data, owner_id)

    
    
    
    assert result.title == "Тестовая задача"
    assert result.owner_id == owner_id