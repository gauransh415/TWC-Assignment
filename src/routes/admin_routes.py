from fastapi import APIRouter, HTTPException, status
from datetime import timedelta
from src.models.admin import LoginRequest, TokenResponse
from src.services.admin_service import AdminService
from src.services.auth_service import AuthService
from src.config.settings import settings

router = APIRouter(prefix="/admin", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def admin_login(request: LoginRequest):
    """
    Admin login endpoint - authenticates admin and returns JWT token.

    Args:
        request: Login credentials (email and password)

    Returns:
        JWT access token with admin and organization info

    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Authenticate admin
        admin = AdminService.authenticate_admin(request.email, request.password)

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Prepare token data
        token_data = {
            "admin_id": str(admin["_id"]),
            "organization_id": str(admin["organization_id"]),
            "email": admin["email"],
        }

        # Create access token
        access_token = AuthService.create_access_token(token_data)

        # Calculate expiration time in seconds
        expires_in = settings.jwt_expiration_hours * 3600

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            admin_id=str(admin["_id"]),
            organization_id=str(admin["organization_id"]),
            email=admin["email"],
            expires_in=expires_in,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}",
        )
