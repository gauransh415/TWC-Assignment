from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId
from src.config.database import db
from src.services.database_service import DatabaseService
from src.services.admin_service import AdminService


class OrganizationService:
    """Service class for organization CRUD operations."""

    @staticmethod
    def validate_organization_exists(organization_name: str) -> bool:
        """
        Check if organization with given name already exists.

        Args:
            organization_name: Name to check

        Returns:
            True if exists, False otherwise
        """
        existing = db.organizations.find_one({"organization_name": organization_name})
        return existing is not None

    @staticmethod
    def create_organization(
        organization_name: str, admin_email: str, admin_password: str
    ) -> dict:
        """
        Create a new organization with admin user and dynamic collection.

        Args:
            organization_name: Name of the organization
            admin_email: Admin user email
            admin_password: Admin user password

        Returns:
            Created organization document with admin info

        Raises:
            Exception: If organization already exists or creation fails
        """
        # Validate organization name doesn't exist
        if OrganizationService.validate_organization_exists(organization_name):
            raise Exception("Organization with this name already exists")

        # Generate collection name
        collection_name = DatabaseService.generate_collection_name(organization_name)

        # Create organization document
        org_doc = {
            "organization_name": organization_name,
            "collection_name": collection_name,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        # Insert organization into master database
        result = db.organizations.insert_one(org_doc)
        organization_id = result.inserted_id
        org_doc["_id"] = organization_id

        try:
            # Create dynamic collection for organization
            DatabaseService.create_dynamic_collection(collection_name)

            # Create admin user for organization
            admin_doc = AdminService.create_admin(
                admin_email, admin_password, organization_id
            )

            # Return organization with admin info
            org_doc["admin_id"] = admin_doc["_id"]
            org_doc["admin_email"] = admin_email

            return org_doc

        except Exception as e:
            # Rollback: delete organization if admin creation fails
            db.organizations.delete_one({"_id": organization_id})
            DatabaseService.drop_collection(collection_name)
            raise Exception(f"Failed to create organization: {str(e)}")

    @staticmethod
    def get_organization(organization_name: str) -> Optional[dict]:
        """
        Get organization by name.

        Args:
            organization_name: Name of the organization

        Returns:
            Organization document or None if not found
        """
        org = db.organizations.find_one({"organization_name": organization_name})

        if not org:
            return None

        # Get admin info for the organization
        admin = AdminService.get_admin_by_organization(org["_id"])
        if admin:
            org["admin_email"] = admin["email"]
            org["admin_id"] = admin["_id"]

        return org

    @staticmethod
    def get_organization_by_id(organization_id: ObjectId) -> Optional[dict]:
        """
        Get organization by ID.

        Args:
            organization_id: Organization ObjectId

        Returns:
            Organization document or None if not found
        """
        return db.organizations.find_one({"_id": organization_id})

    @staticmethod
    def update_organization(
        old_organization_name: str,
        new_organization_name: str,
        admin_email: Optional[str] = None,
        admin_password: Optional[str] = None,
    ) -> dict:
        """
        Update organization name and optionally admin credentials.
        This involves creating a new collection and migrating data.

        Args:
            old_organization_name: Current organization name
            new_organization_name: New organization name
            admin_email: New admin email (optional)
            admin_password: New admin password (optional)

        Returns:
            Updated organization document

        Raises:
            Exception: If organization not found or update fails
        """
        # Get existing organization
        org = db.organizations.find_one({"organization_name": old_organization_name})
        if not org:
            raise Exception("Organization not found")

        # Check if new name already exists (and it's not the same org)
        if old_organization_name != new_organization_name:
            if OrganizationService.validate_organization_exists(new_organization_name):
                raise Exception("Organization with new name already exists")

        old_collection_name = org["collection_name"]
        new_collection_name = DatabaseService.generate_collection_name(
            new_organization_name
        )

        try:
            # Create new collection
            DatabaseService.create_dynamic_collection(new_collection_name)

            # Migrate data from old collection to new collection
            if DatabaseService.collection_exists(old_collection_name):
                DatabaseService.migrate_collection_data(
                    old_collection_name, new_collection_name
                )

            # Update organization document
            update_doc = {
                "organization_name": new_organization_name,
                "collection_name": new_collection_name,
                "updated_at": datetime.now(timezone.utc),
            }

            db.organizations.update_one({"_id": org["_id"]}, {"$set": update_doc})

            # Drop old collection
            DatabaseService.drop_collection(old_collection_name)

            # Update admin credentials if provided
            if admin_email or admin_password:
                admin = AdminService.get_admin_by_organization(org["_id"])
                if admin:
                    AdminService.update_admin_credentials(
                        admin["_id"], admin_email, admin_password
                    )

            # Get updated organization
            updated_org = OrganizationService.get_organization(new_organization_name)
            return updated_org

        except Exception as e:
            # Cleanup new collection if update fails
            DatabaseService.drop_collection(new_collection_name)
            raise Exception(f"Failed to update organization: {str(e)}")

    @staticmethod
    def delete_organization(organization_name: str, admin_id: ObjectId) -> bool:
        """
        Delete organization and cleanup associated resources.
        Only the organization's admin can delete it.

        Args:
            organization_name: Name of the organization
            admin_id: ID of the admin requesting deletion

        Returns:
            True if successful, False otherwise

        Raises:
            Exception: If organization not found or admin not authorized
        """
        # Get organization
        org = db.organizations.find_one({"organization_name": organization_name})
        if not org:
            raise Exception("Organization not found")

        # Verify admin belongs to this organization
        admin = AdminService.get_admin_by_id(admin_id)
        if not admin or admin["organization_id"] != org["_id"]:
            raise Exception("Not authorized to delete this organization")

        try:
            # Drop the organization's collection
            DatabaseService.drop_collection(org["collection_name"])

            # Delete admin users for this organization
            AdminService.delete_admins_by_organization(org["_id"])

            # Delete organization from master database
            result = db.organizations.delete_one({"_id": org["_id"]})

            return result.deleted_count > 0

        except Exception as e:
            raise Exception(f"Failed to delete organization: {str(e)}")

    @staticmethod
    def list_all_organizations() -> list:
        """
        Get list of all organizations.

        Returns:
            List of organization documents
        """
        return list(db.organizations.find())
