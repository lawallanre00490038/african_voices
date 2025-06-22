from typing import Any, Callable
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI, status
from sqlalchemy.exc import SQLAlchemyError

class GovernanceException(Exception):
    """Base class for all AI for Governance platform-related exceptions."""
    
    def __init__(self, message: str = "An error occurred", error_code: str = "error"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

    
class DatabaseError(GovernanceException):
    """An error occurred while interacting with the database."""
    def __init__(self, message: str = "Database error occurred", error_code: str = "database_error"):
        super().__init__(message=message, error_code=error_code)
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class InvalidToken(GovernanceException):
    """User has provided an invalid or expired token."""
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message=message, error_code="invalid_token")

class UserLoggedOut(GovernanceException):
    """User has logged out and the token is no longer valid."""
    pass

class ResetPasswordFailed(GovernanceException):
    """User has provided an invalid or expired token."""
    pass

class RevokedToken(GovernanceException):
    """User has provided a token that has been revoked."""
    pass


class AccessTokenRequired(GovernanceException):
    """User has provided a refresh token when an access token is needed."""
    pass


class RefreshTokenRequired(GovernanceException):
    """User has provided an access token when a refresh token is needed."""
    pass


class UserAlreadyExists(GovernanceException):
    """User is trying to register with an email that already exists."""
    def __init__(self, message: str = "User with this email already exists"):
        super().__init__(message=message, error_code="user_exists")

class EmailAlreadyVerified(GovernanceException):
    """User is trying to register with an email that has already been verified."""
    def __init__(self, message: str = "Email already verified"):
        super().__init__(message=message, error_code="email_already_verified")

class EmailNotVerified(GovernanceException):
    """User has not verified their email."""
    def __init__(self, message: str = "Email not verified"):
        super().__init__(message=message, error_code="email_not_verified")

class InvalidCredentials(GovernanceException):
    """User has provided incorrect login details."""
    pass

class UnAuthenticated(GovernanceException):
    """User is not authenticated."""
    pass


class InsufficientPermission(GovernanceException):
    """User does not have the necessary permissions to perform an action."""
    pass


class UserNotFound(GovernanceException):
    """User not found in the system."""
    pass


class AccountNotVerified(GovernanceException):
    """User account has not been verified yet."""
    pass

class AssessmentNotFound(GovernanceException):
    """Assessment not found."""
    pass

class AllAssessmentsNotFound(GovernanceException):
    """All assessments not found."""
    pass

class QuestionNotFound(GovernanceException):
    """Question not found."""
    pass

class QuestionNotFoundForPillar(GovernanceException):
    """Question not found for the specified pillar."""
    pass

class PillarNotFound(GovernanceException):
    """Pillar not found."""
    pass

class NoPillarFound(GovernanceException):
    """No pillar found for the specified assessment."""
    pass

class PillarScoreNotFound(GovernanceException):
    """Pillar score not found."""
    pass

class AnswerNotFound(GovernanceException):
    """Answer not found."""
    pass

class TrueScoreNotFound(GovernanceException):
    """True score not found."""
    pass

class ProgressTractionNotFound(GovernanceException):
    """Progress traction not found."""
    pass

class SubmissionError(GovernanceException):
    """Error occurred during submission."""
    pass


class ReportNotFound(GovernanceException):
    """Report not found."""
    pass

class ShareableReportNotFound(GovernanceException):
    """Shareable Report not found."""
    pass

class InvalidAssessmentStatus(GovernanceException):
    """The assessment is in the wrong status for this operation."""
    pass

class AssessmentAlreadyCompleted(GovernanceException):
    """The assessment has been already completed."""
    def __init__(self, message: str = "Assessment is already completed"):
        super().__init__(message=message, error_code="assessment_already_completed")

class AssessmentNotBelongToUser(GovernanceException):
     """The assessment does not belong to user."""
     def __init__(self, message: str = "Assessment does not belong to user"):
          super().__init__(message=message, error_code="assessment_not_belong_to_user")

class QuestionAlreadyAnswered(GovernanceException):
    """Question already answered in assessment."""
    def __init__(self, message: str = "Question already answered in assessment"):
        super().__init__(message=message, error_code="question_already_answered")


class NoChatSessionFoundError(GovernanceException):
    """No chat session found for the user."""
    def __init__(self, message: str = "No chat session found"):
        super().__init__(message=message, error_code="no_chat_session_found")

class InvalidSessionId(GovernanceException):
    """The provided session ID is invalid."""
    def __init__(self, message: str = "Invalid session ID or session id not found"):
        super().__init__(message=message, error_code="invalid_session_id")

class NoChatHistoryFoundError(GovernanceException):
    """No chat history found for the user."""
    def __init__(self, message: str = "No chat history found for the user"):
        super().__init__(message=message, error_code="no_chat_history_found")

class InvalidTaskSubmission(GovernanceException):
    """User submitted a task that does not meet requirements."""
    pass


class DataValidationError(GovernanceException):
    """Submitted data failed validation checks."""
    pass

class Unauthorized(GovernanceException):
    """The client is not authorized to perform this action."""
    pass

class Forbidden(GovernanceException):
    """The client does not have permission to access this resource."""
    pass

class RateLimitExceeded(GovernanceException):
    """The client has exceeded the rate limit."""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message=message, error_code="rate_limit_exceeded")

class Conflict(GovernanceException):
    """The request conflicts with the current state of the server."""
    def __init__(self, message: str = "Conflict with current server state"):
        super().__init__(message=message, error_code="conflict")

class ReportGenerationError(GovernanceException):
    """An error occurred while generating the report."""
    def __init__(self, message: str = "Error generating report"):
        super().__init__(message=message, error_code="report_generation_error")

class InvalidReportFormat(GovernanceException):
    """The requested report format is invalid."""
    def __init__(self, message: str = "Invalid report format"):
        super().__init__(message=message, error_code="invalid_report_format")

class SharingReportError(GovernanceException):
    """An error occurred while sharing the report."""
    def __init__(self, message: str = "Error sharing report"):
        super().__init__(message=message, error_code="sharing_report_error")

class AssessmentNotCompleted(GovernanceException):
    """The assessment has not been completed."""
    def __init__(self, message: str = "Assessment not completed or not found"):
        super().__init__(message=message, error_code="assessment_not_completed")


class StateNotFound(GovernanceException):
    """State not found."""
    def __init__(self, message: str = "State not found"):
        super().__init__(message=message, error_code="state_not_found")

def create_exception_handler(
    status_code: int,
    initial_detail: str = "An unexpected error occurred"
) -> Callable[[Request, GovernanceException], JSONResponse]:

    async def exception_handler(request: Request, exc: GovernanceException):
        return JSONResponse(
            status_code=status_code,
            content={
                "message": exc.message or initial_detail,
                "error_code": initial_detail["error_code"] or exc.error_code,
                "resolution": initial_detail["resolution"] or "Please try again later",
            }
        )

    return exception_handler


def register_all_errors(app: FastAPI):
    """Registers all exception handlers in the FastAPI app."""

    app.add_exception_handler(
        StateNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "State not found",
                "resolution": "Please check the state ID",
                "error_code": "state_not_found",
            },
        ),
    )

    app.add_exception_handler(
        DatabaseError,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            initial_detail={
                "message": "Database error occurred",
                "resolution": "Please try again later",
                "error_code": "database_error",
            },
        ),
    )

    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "User with this email already exists",
                "resolution": "Please use a different email",
                "error_code": "user_exists",
            },
        ),
    )

    app.add_exception_handler(
        EmailAlreadyVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Email already verified",
                "error_code": "email_already_verified",
                "resolution": "Please use a different email or  go ahead to sign in",
            },
        ),
    )

    app.add_exception_handler(
        UserLoggedOut,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "User is logged out",
                "resolution": "You are already logged out. Please log in if you want to",
                "error_code": "user_logged_out",
            },
        ),
    )

    app.add_exception_handler(
        EmailNotVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Email not verified",
                "resolution": "Please verify your email and check for verification details",
                "error_code": "email_not_verified",
            },
        ),
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found",
                "resolution": "Please check the user credentials",
                "error_code": "user_not_found",
            },
        ),
    )
    
    app.add_exception_handler(
        AssessmentNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Assessment not found",
                "resolution": "Please check the assessment ID",
                "error_code": "assessment_not_found",
            },
        ),
    )

    app.add_exception_handler(
        AssessmentNotCompleted,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Assessment not completed or not found",
                "resolution": "Please complete the assessment or take a new one",
                "error_code": "assessment_not_completed",
            },
        ),
    )

    app.add_exception_handler(
        AllAssessmentsNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Assessment not found",
                "resolution": "Please try again later",
                "error_code": "assessment_not_found",
            },
        ),
    )

    app.add_exception_handler(
        PillarNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Assessment Pillar not found",
                "resolution": "Please check the assessment ID and pillar ID",
                "error_code": "pillar_not_found",
            },
        ),
    )

    app.add_exception_handler(
        PillarScoreNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "No pillar scores found for this assessment.",
                "resolution": "Please check the assessment ID",
                "error_code": "pillar_score_not_found",
            },
        ),
    )

    app.add_exception_handler(
        QuestionNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Question(s) not found",
                "resolution": "Please check the assessment ID and question ID",
                "error_code": "question_not_found",
            },
        ),
    )   

    app.add_exception_handler(
        QuestionNotFoundForPillar,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Question not found for the specified pillar",
                "resolution": "Please check the assessment ID and pillar ID",
                "error_code": "question_not_found_for_pillar",
            },
        ),
    )

    app.add_exception_handler(
        AnswerNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Answer not found",
                "resolution": "Please check the assessment ID and question ID",
                "error_code": "answer_not_found",
            },
        ),
    )

    app.add_exception_handler(
        ReportNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Report not found",
                "resolution": "Please check the report ID",
                "error_code": "report_not_found",
            },
        ),
    )

    app.add_exception_handler(
        ShareableReportNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Shareable Report not found",
                "resolution": "Please check the report ID",
                "error_code": "shareable_report_not_found",
            },
        ),
    )

    app.add_exception_handler(
        InvalidAssessmentStatus,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Assessment is in an invalid status for this operation",
                "resolution": "Please check the assessment status",
                "error_code": "invalid_assessment_status",
            },
        ),
    )

    app.add_exception_handler(
        SubmissionError,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Error occurred during submission",
                "resolution": "Please check the submitted data",
                "error_code": "submission_error",
            },
        ),
    )
    
    app.add_exception_handler(
        AssessmentAlreadyCompleted,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Assessment is already completed",
                "resolution": "Please start a new assessment",
                "error_code": "assessment_already_completed",
            },
        ),
    )

    app.add_exception_handler(
        AssessmentNotBelongToUser,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Assessment does not belong to user",
                "resolution": "Please check the assessment ID",
                "error_code": "assessment_not_belong_to_user",
            },
        ),
    )


    app.add_exception_handler(
        TrueScoreNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "True score not found",
                "resolution": "Please check the assessment ID",
                "error_code": "true_score_not_found",
            },
        ),
    )
    
    app.add_exception_handler(
        NoPillarFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "No pillar found",
                "resolution": "Please check the assessment ID",
                "error_code": "no_pillar_found",
            },
        ),
    )

    app.add_exception_handler(
        ProgressTractionNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Progress traction not found for this assessment",
                "resolution": "Please check the assessment ID",
                "error_code": "progress_traction_not_found",
            },
        ),
    )

    app.add_exception_handler(
        ResetPasswordFailed,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Reset password failed",
                "resolution": "Please check the reset token and try again",
                "error_code": "reset_password_failed",
            },
        ),
    )
    
    app.add_exception_handler(
        QuestionAlreadyAnswered,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "message": "Question already answered in assessment",
                "resolution": "Please answer a different question",
                "error_code": "question_already_answered",
            },
        ),
    )

    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid email or password",
                "resolution": "Please check your credentials and try again",
                "error_code": "invalid_credentials",
            },
        ),
    )

    app.add_exception_handler(
        UnAuthenticated,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "User not authenticated.",
                "resolution": "Please request a new token or signin.",
                "error_code": "unauthenticated",
            },
        ),
    )

    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid or expired",
                "resolution": "Please request a new token",
                "error_code": "invalid_token",
            },
        ),
    )

    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token has been revoked",
                "resolution": "Please request a new token",
                "error_code": "token_revoked",
            },
        ),
    )

    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Access token required",
                "resolution": "Please provide a valid access token",
                "error_code": "access_token_required",
            },
        ),
    )

    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Refresh token required",
                "resolution": "Please provide a valid refresh token",
                "error_code": "refresh_token_required",
            },
        ),
    )

    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Insufficient permissions",
                "resolution": "Please check your permissions",
                "error_code": "insufficient_permissions",
            },
        ),
    )

    app.add_exception_handler(
        AccountNotVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Account not verified",
                "error_code": "account_not_verified",
                "resolution": "Please check your email for verification details",
            },
        ),
    )

    app.add_exception_handler(
        NoChatSessionFoundError,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "No chat session found",
                "error_code": "no_chat_session_found",
                "resolution": "Please create a new chat session",
            },
        ),
    )

    app.add_exception_handler(
        InvalidSessionId,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Invalid session ID or session id not found",
                "error_code": "invalid_session_id",
                "resolution": "Please check the session ID and try again",
            },
        ),
    )

    app.add_exception_handler(
        NoChatHistoryFoundError,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "No chat history found for the user",
                "error_code": "no_chat_history_found",
                "resolution": "Please create a new chat session",
            },
        ),
    )

    app.add_exception_handler(
        DataValidationError,
        create_exception_handler(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            initial_detail={
                "message": "Data validation failed",
                "resolution": "Please check the data you provided",
                "error_code": "data_validation_error",
            },
        ),
    )
    
    app.add_exception_handler(
        Unauthorized,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Unauthorized",
                "resolution": "Please provide valid credentials",
                "error_code": "unauthorized",
            },
        ),
    )

    app.add_exception_handler(
        Forbidden,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Forbidden",
                "resolution": "You do not have permission to access this resource",
                "error_code": "forbidden",
            },
        ),
    )

    app.add_exception_handler(
        RateLimitExceeded,
        create_exception_handler(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            initial_detail={
                "message": "Rate limit exceeded",
                "resolution": "Please slow down your requests",
                "error_code": "rate_limit_exceeded",
            },
        ),
    )

    app.add_exception_handler(
        Conflict,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "message": "Conflict with current server state",
                "resolution": "Please resolve the conflict and try again",
                "error_code": "conflict",
            },
        ),
    )

    app.add_exception_handler(
        ReportGenerationError,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            initial_detail={
                "message": "Error generating report",
                "resolution": "Please try again later",
                "error_code": "report_generation_error",
            },
        ),
    )

    app.add_exception_handler(
        InvalidReportFormat,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid report format",
                "resolution": "Please provide a valid format (e.g., PDF, DOCX)",
                "error_code": "invalid_report_format",
            },
        ),
    )

    app.add_exception_handler(
        SharingReportError,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            initial_detail={
                "message": "Error sharing report",
                "resolution": "Please try again later",
                "error_code": "sharing_report_error",
            },
        ),
    )

    @app.exception_handler(500)
    async def internal_server_error(request, exc):
        return JSONResponse(
            content={
                "message": "Oops! Something went wrong",
                "resolution": "Please try again later",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error(request, exc):
        print(str(exc))
        return JSONResponse(
            content={
                "message": "Database error occurred",
                "resolution": "Please try again later",
                "error_code": "database_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
