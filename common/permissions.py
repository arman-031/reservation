from rest_framework.permissions import BasePermission


class IsBusinessOwner(BasePermission):
    message = "Only business owners can perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "business_owner"
        )