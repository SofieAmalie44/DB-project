from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
# imports for authentication endpoints
from rest_framework.authtoken import views as drf_auth
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


schema_view = get_schema_view(
    openapi.Info(
        title="RPG API",
        default_version='v1',
        description="API documentation for RPG project",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # --- TOKEN AUTH ---
    path("api/auth/token/login/", drf_auth.obtain_auth_token),

    # --- JWT AUTH ---
    path("api/auth/jwt/create/", TokenObtainPairView.as_view(), name="jwt_create"),
    path("api/auth/jwt/refresh/", TokenRefreshView.as_view(), name="jwt_refresh"),
    path("api/auth/jwt/verify/", TokenVerifyView.as_view(), name="jwt_verify"),

    # RPG app endpoints
    path("api/", include("rpg_backend.rpg.urls")),

    # Swagger UI
    path("api/docs/", schema_view.with_ui('swagger', cache_timeout=0), name="swagger-ui"),
    path("api/redoc/", schema_view.with_ui('redoc', cache_timeout=0), name="redoc-ui"),

    # Raw OpenAPI JSON
    path("api/openapi.json", schema_view.without_ui(cache_timeout=0), name="openapi-json"),
]
