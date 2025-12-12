from pymongo import MongoClient, ASCENDING
from pymongo.database import Database
from src.config.settings import settings


class DatabaseConfig:
    """Manages MongoDB connection and provides database access."""

    _client: MongoClient = None
    _database: Database = None

    @classmethod
    def get_client(cls) -> MongoClient:
        """Get MongoDB client instance (singleton)."""
        if cls._client is None:
            cls._client = MongoClient(settings.mongodb_url)
        return cls._client

    @classmethod
    def get_database(cls) -> Database:
        """Get main database instance."""
        if cls._database is None:
            client = cls.get_client()
            cls._database = client[settings.database_name]
        return cls._database

    @classmethod
    def close_connection(cls):
        """Close MongoDB connection."""
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            cls._database = None

    @classmethod
    def initialize_indexes(cls):
        """Create necessary indexes for the master database."""
        db = cls.get_database()

        # Organizations collection indexes
        db.organizations.create_index(
            [("organization_name", ASCENDING)], unique=True
        )

        # Admin users collection indexes
        db.admin_users.create_index([("email", ASCENDING)], unique=True)
        db.admin_users.create_index([("organization_id", ASCENDING)])


# Global database instance
db = DatabaseConfig.get_database()
