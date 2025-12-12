from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId
from src.services.auth_service import AuthService
from src.services.admin_service import AdminService

security = HTTPBearer()


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    FastAPI dependency to get current authenticated admin from JWT token.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        Admin user document with decoded token data

    Raises:
        HTTPException: If token is invalid or admin not found
    """
    token = credentials.credentials

    # Decode token
    payload = AuthService.decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract admin_id from payload
    admin_id_str = payload.get("admin_id")
    if not admin_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Convert to ObjectId
    try:
        admin_id = ObjectId(admin_id_str)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get admin from database
    admin = AdminService.get_admin_by_id(admin_id)

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin user not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Add decoded token data to admin document
    admin["token_data"] = payload

    return admin


def verify_admin_organization(admin: dict, organization_id: ObjectId) -> bool:
    """
    Verify that admin belongs to the specified organization.

    Args:
        admin: Admin user document from get_current_admin
        organization_id: Organization ID to verify against

    Returns:
        True if admin belongs to organization

    Raises:
        HTTPException: If admin doesn't belong to organization
    """
    if admin["organization_id"] != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this organization",
        )

    return True
