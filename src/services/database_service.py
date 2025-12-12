import re
from typing import Optional
from pymongo.collection import Collection
from pymongo.errors import CollectionInvalid
from src.config.database import db


class DatabaseService:
    """Service class for dynamic database and collection operations."""

    @staticmethod
    def sanitize_org_name(name: str) -> str:
        """
        Sanitize org name for use in collection naming.

        Args:
            name: Original org name

        Returns:
            Sanitized name (lowercase, alphanumeric with underscores)
        """
        sanitized = name.lower()
        sanitized = sanitized.replace(" ", "_").replace("-", "_")
        sanitized = re.sub(r"[^a-z0-9_]", "", sanitized)
        sanitized = re.sub(r"_+", "_", sanitized)
        sanitized = sanitized.strip("_")
        return sanitized

    @staticmethod
    def generate_collection_name(org_name: str) -> str:
        """
        Generate MongoDB collection name from org name.

        Args:
            org_name: Name of the org

        Returns:
            Collection name in format: org_sanitizedname
        """
        sanitized = DatabaseService.sanitize_org_name(org_name)
        return f"org_{sanitized}"

    @staticmethod
    def create_dynamic_collection(collection_name: str) -> Collection:
        """
        Create a new collection for an org.

        Args:
            collection_name: Name of the collection to create

        Returns:
            Created collection handle

        Raises:
            CollectionInvalid: If collection already exists or name is invalid
        """
        try:
            # Create collection explicitly
            collection = db.create_collection(collection_name)
            return collection
        except CollectionInvalid:
            # Collection already exists
            return db[collection_name]

    @staticmethod
    def get_collection_handle(collection_name: str) -> Collection:
        """
        Get a handle to an existing collection.

        Args:
            collection_name: Name of the collection

        Returns:
            Collection handle
        """
        return db[collection_name]

    @staticmethod
    def drop_collection(collection_name: str) -> bool:
        """
        Drop a collection from the database.

        Args:
            collection_name: Name of the collection to drop

        Returns:
            True if successful, False otherwise
        """
        try:
            db.drop_collection(collection_name)
            return True
        except Exception:
            return False

    @staticmethod
    def migrate_collection_data(
        source_collection_name: str, target_collection_name: str
    ) -> bool:
        """
        Migrate all data from source collection to target collection.

        Args:
            source_collection_name: Source collection name
            target_collection_name: Target collection name

        Returns:
            True if successful, False otherwise
        """
        try:
            source_collection = db[source_collection_name]
            target_collection = db[target_collection_name]

            # Get all documents from source
            documents = list(source_collection.find())

            # Insert into target if documents exist
            if documents:
                target_collection.insert_many(documents)

            return True
        except Exception:
            return False

    @staticmethod
    def collection_exists(collection_name: str) -> bool:
        """
        Check if a collection exists in the database.

        Args:
            collection_name: Name of the collection

        Returns:
            True if exists, False otherwise
        """
        return collection_name in db.list_collection_names()
