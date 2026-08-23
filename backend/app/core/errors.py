from typing import Any, Optional
from fastapi import HTTPException, status

class SCCGException(Exception):
    def __init__(self, code: str, message: str, details: Optional[Any] = None, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.code = code
        self.message = message
        self.details = details
        self.status_code = status_code
        super().__init__(self.message)

class AWSPermissionError(SCCGException):
    def __init__(self, message: str = 'Required AWS permission is missing or access is denied'):
        super().__init__(
            code='AWS_PERMISSION_ERROR',
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )

class AWSConnectionError(SCCGException):
    def __init__(self, message: str = 'Unable to establish connection to AWS account'):
        super().__init__(
            code='AWS_CONNECTION_ERROR',
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST
        )

class ResourceNotFoundError(SCCGException):
    def __init__(self, resource_name: str = 'Resource'):
        super().__init__(
            code='NOT_FOUND',
            message=f'{resource_name} not found or access denied',
            status_code=status.HTTP_404_NOT_FOUND
        )

class UnauthorizedError(SCCGException):
    def __init__(self, message: str = 'Invalid authentication credentials'):
        super().__init__(
            code='UNAUTHORIZED',
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
