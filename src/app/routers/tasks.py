from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_async_session
from ..models import Project, Task
from ..schemas import CreateTask, ResponseTask, UpdateTask, StatusEnum, RolesUser
from ..auth import get_current_user, has_permission

router = APIRouter()

@router.post(
    "/projects/{project_id}/tasks",
    response_model=ResponseTask)

async def create_task(
    project_id:int,
    data:CreateTask,
    session:AsyncSession=Depends(get_async_session),
    current_user=Depends(get_current_user)
):

    result = await session.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )

    existing_project = result.scalar_one_or_none()
    if existing_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    task = Task(
        title=data.title,
        description=data.description,
        status=data.status.value,
        project_id=project_id
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task

@router.get(
    "/projects/{project_id}/tasks",
    response_model=list[ResponseTask])

async def get_tasks(
    project_id:int,
    status:StatusEnum | None = None,
    session:AsyncSession=Depends(get_async_session),
    current_user=Depends(get_current_user)
):

    role = current_user.role
    if role== RolesUser.Admin:
        check = has_permission(role, "task", "read_any")
        if not check:
            raise HTTPException(status_code=403, detail="Forbidden")
        
        project_result = await session.execute(
            select(Project).where(
                Project.id == project_id,
            )
        )
        
    else:   
        project_result = await session.execute(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == current_user.id
            )
        )

    existing_project = project_result.scalar_one_or_none()

    if existing_project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    if status:
        task_result = await session.execute(
            select(Task).where(
                Task.project_id == project_id,
                Task.status== status.value 
            )
        )

    else:
        task_result = await session.execute(
            select(Task).where(
                Task.project_id == project_id,
            )
        )

    tasks = task_result.scalars().all()

    return tasks


@router.get(
    "/projects/{project_id}/tasks/{task_id}",
    response_model=ResponseTask)

async def get_task_by_id(
    project_id:int,
    task_id:int,
    session:AsyncSession=Depends(get_async_session),
    current_user=Depends(get_current_user)
):

    role = current_user.role
    if role== RolesUser.Admin:
        check = has_permission(role, "task", "read_any")
        if not check:
            raise HTTPException(status_code=403, detail="Forbidden")
        
        project_result = await session.execute(
            select(Project).where(
                Project.id == project_id,
            )
        )
        
    else:   
        project_result = await session.execute(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == current_user.id
            )
        )

    existing_project = project_result.scalar_one_or_none()

    if existing_project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    task_result = await session.execute(
        select(Task).where(
            Task.id == task_id,
            Task.project_id == project_id
        )
    )

    task = task_result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
    )

    return task


@router.patch(
    "/projects/{project_id}/tasks/{task_id}",
    response_model=ResponseTask)

async def update_task(
    project_id:int,
    task_id:int,
    data:UpdateTask,
    session:AsyncSession=Depends(get_async_session),
    current_user=Depends(get_current_user),

):
    role = current_user.role
    if role== RolesUser.Admin:
        check = has_permission(role, "task", "update_any")
        if not check:
            raise HTTPException(status_code=403, detail="Forbidden")
        
        project_result = await session.execute(
            select(Project).where(
                Project.id == project_id,
            )
        )
        
    else:   
        project_result = await session.execute(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == current_user.id
            )
        )

    existing_project = project_result.scalar_one_or_none()

    if existing_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await session.execute(
        select(Task).where(
            Task.id == task_id,
            Task.project_id == project_id
        )
    )

    existing_task = result.scalar_one_or_none()

    if existing_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = data.model_dump(
        exclude_unset=True,
        mode="json"
    )
    
    for field, value in update_data.items():
        setattr(existing_task, field, value)

    await session.commit()
    await session.refresh(existing_task)

    return existing_task


@router.delete(
    "/projects/{project_id}/tasks/{task_id}")

async def delete_task(
    project_id:int,
    task_id:int,
    session:AsyncSession=Depends(get_async_session),
    current_user=Depends(get_current_user)
):
    role = current_user.role
    if role== RolesUser.Admin:
        check = has_permission(role, "task", "delete_any")
        if not check:
            raise HTTPException(status_code=403, detail="Forbidden")
        
        project_result = await session.execute(
            select(Project).where(
                Project.id == project_id,
            )
        )
        
    else:   
        project_result = await session.execute(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == current_user.id
            )
        )

    existing_project = project_result.scalar_one_or_none()

    if existing_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await session.execute(
        select(Task).where(
            Task.id == task_id,
            Task.project_id == project_id
        )
    ) 

    existing_task = result.scalar_one_or_none()

    if existing_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await session.delete(existing_task)    
    await session.commit()

    return {"message":"task deleted"}