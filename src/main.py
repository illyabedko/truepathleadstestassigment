from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends

from src.core import settings
from src.infra.db.session import init_db, close_db
from src.api.dependencies import get_application_controller, cleanup
from src.api.v1.applications import ApplicationController, router as applications_router
from src.api.schemas import CreateApplicationRequest, ApplicationResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await cleanup()
    await close_db()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)


@app.post("/api/v1/applications", response_model=ApplicationResponse, status_code=202)
async def create_application(
    request: CreateApplicationRequest,
    controller: ApplicationController = Depends(get_application_controller),
):
    return await controller.create(request)


@app.get("/api/v1/applications/{applicant_id}", response_model=ApplicationResponse)
async def get_application(
    applicant_id: str,
    controller: ApplicationController = Depends(get_application_controller),
):
    return await controller.get_by_applicant_id(applicant_id)

