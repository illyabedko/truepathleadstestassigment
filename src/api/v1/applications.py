from fastapi import APIRouter, HTTPException, status

from src.domain.applications.loan.use_cases import SubmitApplicationUseCase, GetApplicationStatusUseCase
from src.domain.exceptions import ValidationError
from src.api.schemas import CreateApplicationRequest, ApplicationResponse, ErrorResponse


router = APIRouter(prefix="/applications", tags=["applications"])


class ApplicationController:

    def __init__(
        self,
        submit_use_case: SubmitApplicationUseCase,
        get_status_use_case: GetApplicationStatusUseCase,
    ):
        self._submit_use_case = submit_use_case
        self._get_status_use_case = get_status_use_case

    async def create(self, request: CreateApplicationRequest) -> ApplicationResponse:
        try:
            application = await self._submit_use_case.execute(
                applicant_id=request.applicant_id,
                amount=request.amount,
                term_months=request.term_months,
            )

            return ApplicationResponse(
                id=application.id,
                applicant_id=application.applicant_id,
                amount=application.amount,
                term_months=application.term_months,
                status=application.status,
                rejection_reason=application.rejection_reason,
            )

        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "validation_error", "message": e.message, "field": e.field},
            )

    async def get_by_applicant_id(self, applicant_id: str) -> ApplicationResponse:
        application = await self._get_status_use_case.execute(applicant_id)

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "not_found", "message": f"Application for '{applicant_id}' not found"},
            )

        return ApplicationResponse(
            id=application.id,
            applicant_id=application.applicant_id,
            amount=application.amount,
            term_months=application.term_months,
            status=application.status,
            rejection_reason=application.rejection_reason,
        )


def setup_routes(controller: ApplicationController) -> APIRouter:
    router.post(
        "",
        response_model=ApplicationResponse,
        status_code=status.HTTP_202_ACCEPTED,
        responses={400: {"model": ErrorResponse}},
    )(controller.create)

    router.get(
        "/{applicant_id}",
        response_model=ApplicationResponse,
        responses={404: {"model": ErrorResponse}},
    )(controller.get_by_applicant_id)

    return router

