from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAgentCreatorOrOwner(BasePermission):
    """Custom permission:
    - Anyone may perform safe (read) methods.
    - POST (create) allowed only for authenticated users whose Profile.role == 'ESTATE AGENT'.
    - For unsafe object-level methods (PUT, PATCH, DELETE), only the property's owner may act.
    """

    def _is_agent(self, user):
        try:
            return user.is_authenticated and user.profile.role == 'ESTATE AGENT'
        except Exception:
            return False

    def has_permission(self, request, view):
        # Allow safe methods for any request
        if request.method in SAFE_METHODS:
            return True

        # Creation allowed only for agents
        if request.method == 'POST':
            return self._is_agent(request.user)

        # For other non-safe methods, defer to object-level permission
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Safe methods: if the requester is an agent, they may only see their own objects.
        if request.method in SAFE_METHODS:
            if self._is_agent(request.user):
                try:
                    return obj.owner == request.user
                except Exception:
                    return False
            return True

        # Only owner can modify/delete
        try:
            return obj.owner == request.user
        except Exception:
            return False
