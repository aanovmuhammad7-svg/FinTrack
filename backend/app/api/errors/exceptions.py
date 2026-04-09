from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status


class ProjectException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Internal server error"
    expose_to_client: bool = True

    def __init__(self, detail: Optional[str] = None, expose_to_client: bool = True):
        if detail is not None:
            self.detail = detail
        self.expose_to_client = expose_to_client
        super().__init__(status_code=self.status_code, detail=self.detail)


class FinanceException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Internal finance service error"
    expose_to_client: bool = True

    def __init__(self, detail: Optional[str] = None, expose_to_client: bool = True):
        if detail is not None:
            self.detail = detail
        self.expose_to_client = expose_to_client
        super().__init__(status_code=self.status_code, detail=self.detail)


class TransactionException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Internal transaction service error"
    expose_to_client: bool = True

    def __init__(self, detail: Optional[str] = None, expose_to_client: bool = True):
        if detail is not None:
            self.detail = detail
        self.expose_to_client = expose_to_client
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(ProjectException):
    status_code = status.HTTP_409_CONFLICT

    def __init__(self, user_email: str):
        super().__init__(detail=f"User {user_email} already exists")


class UserNotFoundException(ProjectException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, user_email: str):
        super().__init__(detail=f"User {user_email} was not found")


class PasswordValidationErrorException(ProjectException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, validation_result: list[str]):
        errors = "; ".join(validation_result)
        super().__init__(detail=f"Password does not meet the requirements: {errors}")


class PasswordIdenticalToPreviousException(ProjectException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "New password must differ from the previous password"


class InvalidPasswordResetTokenException(ProjectException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Password reset link is invalid"


class InvalidCredentialsException(ProjectException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid credentials"


class EmailNotConfirmedException(ProjectException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Email is not confirmed"


class RefreshTokenNotFoundException(ProjectException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Refresh token was not provided"


class AccessTokenNotFoundException(ProjectException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Access token was not provided"


class InvalidTokenException(ProjectException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid token"


class ExpiredTokenException(ProjectException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token has expired"


class InvalidOrExpiredEmailTokenException(ProjectException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Email confirmation link is invalid or expired"


class EmailAlreadyConfirmedException(ProjectException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Email is already confirmed"


class TooEarlyResendException(ProjectException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "Too many requests. Please try again later"


class InternalServerErrorException(ProjectException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, reason: str = "Internal server error"):
        super().__init__(detail=reason, expose_to_client=False)


class CategoryAlreadyExists(FinanceException):
    status_code = status.HTTP_409_CONFLICT

    def __init__(self, name: str, type: str):
        super().__init__(detail=f"Category '{name}' with type '{type}' already exists")


class CategoryNotFound(FinanceException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, category_id: int):
        super().__init__(detail=f"Category with id {category_id} was not found")


class InvalidCategoryType(FinanceException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, type: str):
        super().__init__(detail=f"Invalid category type: {type}")


class TransactionNotFound(TransactionException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, transaction_id: int):
        super().__init__(detail=f"Transaction with id {transaction_id} was not found")


class TransactionAccessDenied(TransactionException):
    status_code = status.HTTP_403_FORBIDDEN

    def __init__(self):
        super().__init__(detail="Access to this transaction is denied")


class InvalidTransactionAmount(TransactionException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, amount: Decimal):
        super().__init__(detail=f"Invalid transaction amount: {amount}")


class InvalidTransactionType(TransactionException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, tx_type: str):
        super().__init__(detail=f"Invalid transaction type: {tx_type}")


class TransactionCategoryAccessDenied(TransactionException):
    status_code = status.HTTP_403_FORBIDDEN

    def __init__(self, category_id: int):
        super().__init__(detail=f"Category {category_id} is not available for this transaction")


class BudgetNotFound(FinanceException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, budget_id: int):
        super().__init__(detail=f"Budget with id {budget_id} was not found")


class InvalidBudgetPeriod(FinanceException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Invalid budget period: period_start must be before or equal to period_end"


class BudgetAlreadyExists(FinanceException):
    status_code = status.HTTP_409_CONFLICT

    def __init__(self, category_id: int, period_start: object, period_end: object):
        super().__init__(
            detail=f"Budget already exists for category {category_id} in period {period_start} - {period_end}"
        )


class BudgetCategoryTypeError(FinanceException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, category_id: int, category_type: str):
        super().__init__(
            detail=f"Category {category_id} cannot be used for budget. Type={category_type}, expected=expense"
        )


class InvalidReportPeriod(FinanceException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Invalid report period: date_from must be before or equal to date_to"


class UserInactiveException(ProjectException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Account is inactive"


class CSRFMissingOrInvalidException(ProjectException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "CSRF token is missing or invalid"
