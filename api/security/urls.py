from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from .views import RegisterView, CustomTokenObtainPairView

urlpatterns = [
    # Registration endpoint
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    
    # Login endpoint (Generates JWT tokens containing roles)
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Token refreshing endpoint
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Logout (blacklist refresh token) — uses SimpleJWT's built-in view
    path('auth/logout/', TokenBlacklistView.as_view(), name='auth_logout'),
]


# superuser username : api, password: dare1234