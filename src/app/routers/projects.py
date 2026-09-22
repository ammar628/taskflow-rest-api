from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db import get_async_session
from ..models import Project
from ..schemas import CreateProject, ResponseProject, UpdateProject, RolesUser
from ..auth import get_current_user, has_permission

router = APIRouter()

@router.post(
    "/projects",
    response_model=ResponseProject)

async def create_project(
    data:CreateProject,
    session:AsyncSession=Depends(get_async_session),
    current_user=Depends(get_current_user)
):

    project = Project(
        title=data.title,
        description=data.description,
        user_id=current_user.id
    )

    session.add(project)
    await session.commit()
    await session.refresh(project)

    return project

@router.get(
    "/projects",
    response_model=list[ResponseProject])

async def Get_project(
    session:AsyncSession=Depends(get_async_session),
    current_user=Depends(get_current_user)
):

    role = current_user.role
    if role == RolesUser.Admin:
        check = has_permission(role, "project", "read_any")
        if not check:
            raise HTTPException(status_code=403, detail="Forbidden")
        result = await session.execute(
            select(Project)
        )
    else:
        result = await session.execute(select(Project).where(Project.user_id == current_user.id))

    existing_project = result.scalars().all()

    return existing_project


@router.get(
    "/projects/{project_id}",
    response_model=ResponseProject)

async def get_project(
    project_id:int,
    session:AsyncSession=Depends(get_async_session),
    current_user=Depends(get_current_user)
):
    role = current_user.role
    if role== RolesUser.Admin:
        check = has_permission(role, "project", "read_any")
        if not check:
            raise HTTPException(status_code=403, detail="Forbidden")
        result = await session.execute(
            select(Project).where(
                Project.id == project_id,
            )
        )
    else:
        result = await session.execute(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == current_user.id
            )
        )

    existing_project = result.scalar_one_or_none()
    if existing_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return existing_project

@router.patch(
    "/projects/{project_id}",
    response_model=ResponseProject)

async def update_project(
    project_id:int,
    data:UpdateProject,
    session:AsyncSession=Depends(get_async_session),
    current_user=Depends(get_current_user),

):
    role = current_user.role
    if role== RolesUser.Admin:
        check = has_permission(role, "project", "update_any")
        if not check:
            raise HTTPException(status_code=403, detail="Forbidden")
        result = await session.execute(
            select(Project).where(
                Project.id == project_id,
            )
        )
    else:
        result = await session.execute(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == current_user.id
            )
        )

    existing_project = result.scalar_one_or_none()

    if existing_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(existing_project, field, value)

    await session.commit()
    await session.refresh(existing_project)

    return existing_project

@router.delete(
    "/projects/{project_id}")

async def delete_project(
    project_id:int,
    session:AsyncSession=Depends(get_async_session),
    current_user=Depends(get_current_user)
):
    role = current_user.role
    if role== RolesUser.Admin:
        check = has_permission(role, "project", "delete_any")
        if not check:
            raise HTTPException(status_code=403, detail="Forbidden")
        result = await session.execute(
            select(Project).where(
                Project.id == project_id,
            )
        )
    else:
        result = await session.execute(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == current_user.id
            )
        )
    existing_project = result.scalar_one_or_none()
    if existing_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await session.delete(existing_project)    
    await session.commit()

    return {"message":"project deleted"}