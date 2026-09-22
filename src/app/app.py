from fastapi import FastAPI
from .routers.users import router as users_router
from .routers.projects import router as projects_router
from .routers.tasks import router as tasks_router

app = FastAPI()

app.include_router(users_router)
app.include_router(projects_router)
app.include_router(tasks_router)
