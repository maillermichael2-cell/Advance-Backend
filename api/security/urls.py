from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from .views import RegisterView, CustomTokenObtainPairView, GoogleIssueTokenView, CompleteProfileView

urlpatterns = [
    # Registration endpoint
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    
    # Login endpoint (Generates JWT tokens containing roles)
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Token refreshing endpoint
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Logout (blacklist refresh token) — uses SimpleJWT's built-in view
    path('auth/logout/', TokenBlacklistView.as_view(), name='auth_logout'),
    
    path('auth/google/token/', GoogleIssueTokenView.as_view(), name='google_issue_token'),
    path('auth/completeprofile/', CompleteProfileView.as_view(), name='complete_profile'),
]


# superuser username : api, password: dare1234