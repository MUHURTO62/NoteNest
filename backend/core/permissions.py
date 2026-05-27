from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only allow users with role='admin' to access."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )


class IsAuthenticatedAndAdminOrReadOnly(BasePermission):
    """
    Allows safe methods (GET, HEAD, OPTIONS) to any user (authenticated or not).
    Allows write methods (POST, DELETE, etc.) only to users with role='admin'.
    """

    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.role == 'admin'
