from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId
from src.config.database import db
from src.services.auth_service import AuthService
from src.models.admin import AdminUserModel


class AdminService:
    """Service class for admin user management operations."""

    @staticmethod
    def create_admin(email: str, password: str, organization_id: ObjectId) -> dict:
        """
        Create a new admin user.

        Args:
            email: Admin email address
            password: Plain text password
            organization_id: Associated organization ID

        Returns:
            Created admin user document

        Raises:
            Exception: If admin with email already exists
        """
        # Check if admin with email already exists
        existing_admin = db.admin_users.find_one({"email": email})
        if existing_admin:
            raise Exception("Admin with this email already exists")

        # Hash the password
        password_hash = AuthService.hash_password(password)

        # Create admin user document
        admin_doc = {
            "email": email,
            "password_hash": password_hash,
            "organization_id": organization_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        # Insert into database
        result = db.admin_users.insert_one(admin_doc)
        admin_doc["_id"] = result.inserted_id

        return admin_doc

    @staticmethod
    def authenticate_admin(email: str, password: str) -> Optional[dict]:
        """
        Authenticate admin user with email and password.

        Args:
            email: Admin email address
            password: Plain text password

        Returns:
            Admin user document if authenticated, None otherwise
        """
        # Find admin by email
        admin = db.admin_users.find_one({"email": email})

        if not admin:
            return None

        # Verify password
        if not AuthService.verify_password(password, admin["password_hash"]):
            return None

        return admin

    @staticmethod
    def get_admin_by_email(email: str) -> Optional[dict]:
        """
        Get admin user by email.

        Args:
            email: Admin email address

        Returns:
            Admin user document or None
        """
        return db.admin_users.find_one({"email": email})

    @staticmethod
    def get_admin_by_id(admin_id: ObjectId) -> Optional[dict]:
        """
        Get admin user by ID.

        Args:
            admin_id: Admin user ID

        Returns:
            Admin user document or None
        """
        return db.admin_users.find_one({"_id": admin_id})

    @staticmethod
    def get_admin_by_organization(organization_id: ObjectId) -> Optional[dict]:
        """
        Get admin user by organization ID.

        Args:
            organization_id: Organization ID

        Returns:
            Admin user document or None
        """
        return db.admin_users.find_one({"organization_id": organization_id})

    @staticmethod
    def update_admin_credentials(
        admin_id: ObjectId, email: Optional[str] = None, password: Optional[str] = None
    ) -> bool:
        """
        Update admin user credentials.

        Args:
            admin_id: Admin user ID
            email: New email (optional)
            password: New plain text password (optional)

        Returns:
            True if successful, False otherwise
        """
        update_doc = {"updated_at": datetime.now(timezone.utc)}

        if email:
            # Check if new email already exists for another admin
            existing = db.admin_users.find_one({"email": email, "_id": {"$ne": admin_id}})
            if existing:
                raise Exception("Email already in use by another admin")
            update_doc["email"] = email

        if password:
            update_doc["password_hash"] = AuthService.hash_password(password)

        if len(update_doc) == 1:  # Only updated_at
            return False

        result = db.admin_users.update_one({"_id": admin_id}, {"$set": update_doc})

        return result.modified_count > 0

    @staticmethod
    def delete_admin(admin_id: ObjectId) -> bool:
        """
        Delete an admin user.

        Args:
            admin_id: Admin user ID

        Returns:
            True if successful, False otherwise
        """
        result = db.admin_users.delete_one({"_id": admin_id})
        return result.deleted_count > 0

    @staticmethod
    def delete_admins_by_organization(organization_id: ObjectId) -> int:
        """
        Delete all admin users for an organization.

        Args:
            organization_id: Organization ID

        Returns:
            Number of admins deleted
        """
        result = db.admin_users.delete_many({"organization_id": organization_id})
        return result.deleted_count
