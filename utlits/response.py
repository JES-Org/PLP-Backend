
from rest_framework.response import Response
from rest_framework import status

def success_response(data=None, message=None, status_code=status.HTTP_200_OK):
    return Response({
        "isSuccess": True,
        "message": message,
        "data": data,
        "errors": None
    }, status=status_code)

def error_response(message="An error occurred.", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({
        "isSuccess": False,
        "message": message,
        "data": None,
        "errors": errors if errors else []
    }, status=status_code)
