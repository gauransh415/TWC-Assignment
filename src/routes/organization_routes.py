from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId
from src.models.organization import (
    CreateOrganizationRequest,
    GetOrganizationRequest,
    UpdateOrganizationRequest,
    DeleteOrganizationRequest,
    OrganizationResponse,
)
from src.services.organization_service import OrganizationService
from src.utils.validators import Validators
from src.middleware.auth_middleware import get_current_admin

router = APIRouter(prefix="/org", tags=["Organizations"])


@router.post("/create", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(request: CreateOrganizationRequest):
    """
    Create a new organization with admin user and dynamic collection.

    Args:
        request: Organization creation request

    Returns:
        Created organization details

    Raises:
        HTTPException: If creation fails
    """
    try:
        # Validate organization name
        is_valid, error_msg = Validators.validate_organization_name(
            request.organization_name
        )
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

        # Validate email
        if not Validators.validate_email(request.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format"
            )

        # Validate password strength
        is_valid, error_msg = Validators.validate_password_strength(request.password)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

        # Create organization
        org = OrganizationService.create_organization(
            request.organization_name, request.email, request.password
        )

        # Return response
        return OrganizationResponse(
            organization_id=str(org["_id"]),
            organization_name=org["organization_name"],
            collection_name=org["collection_name"],
            created_at=org["created_at"].isoformat(),
            admin_email=org.get("admin_email"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/get", response_model=OrganizationResponse)
def get_organization(organization_name: str):
    """
    Get organization details by name.

    Args:
        organization_name: Name of the organization (query parameter)

    Returns:
        Organization details

    Raises:
        HTTPException: If organization not found
    """
    try:
        org = OrganizationService.get_organization(organization_name)

        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        return OrganizationResponse(
            organization_id=str(org["_id"]),
            organization_name=org["organization_name"],
            collection_name=org["collection_name"],
            created_at=org["created_at"].isoformat(),
            admin_email=org.get("admin_email"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.put("/update", response_model=OrganizationResponse)
def update_organization(
    request: UpdateOrganizationRequest,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Update organization name and/or admin credentials.
    Requires authentication.

    Args:
        request: Organization update request
        current_admin: Authenticated admin from JWT token

    Returns:
        Updated organization details

    Raises:
        HTTPException: If update fails
    """
    try:
        # Validate new organization name
        is_valid, error_msg = Validators.validate_organization_name(
            request.organization_name
        )
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

        # Validate email if provided
        if request.email and not Validators.validate_email(request.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format"
            )

        # Validate password if provided
        if request.password:
            is_valid, error_msg = Validators.validate_password_strength(request.password)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg
                )

        # Get current organization name from admin's organization
        current_org = OrganizationService.get_organization_by_id(
            current_admin["organization_id"]
        )
        if not current_org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Current organization not found",
            )

        # Update organization
        org = OrganizationService.update_organization(
            current_org["organization_name"],
            request.organization_name,
            request.email,
            request.password,
        )

        return OrganizationResponse(
            organization_id=str(org["_id"]),
            organization_name=org["organization_name"],
            collection_name=org["collection_name"],
            created_at=org["created_at"].isoformat(),
            admin_email=org.get("admin_email"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete("/delete", status_code=status.HTTP_200_OK)
def delete_organization(
    request: DeleteOrganizationRequest,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Delete an organization.
    Requires authentication. Only the organization's admin can delete it.

    Args:
        request: Organization deletion request
        current_admin: Authenticated admin from JWT token

    Returns:
        Success message

    Raises:
        HTTPException: If deletion fails or not authorized
    """
    try:
        # Delete organization using authenticated admin ID
        success = OrganizationService.delete_organization(
            request.organization_name, current_admin["_id"]
        )

        if success:
            return {"message": "Organization deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete organization",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
