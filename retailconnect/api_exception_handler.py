"""Custom exception handler for API responses."""

from rest_framework.views import exception_handler
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """Mask low-level parse errors with a user-friendly message."""
    # Use DRF's default handler first
    response = exception_handler(exc, context)

    if isinstance(exc, ParseError):
        message = "Invalid JSON payload. Please check your request body."
        return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)

    return response
