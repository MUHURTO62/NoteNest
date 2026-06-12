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
    Allows safe methods (GET, HEAD, OPTIONS) to authenticated users.
    Allows write methods (POST, DELETE, etc.) only to users with role='admin'.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user.role == 'admin'
