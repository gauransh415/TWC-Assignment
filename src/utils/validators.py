import re
from typing import Optional


class ValidationError(Exception):
    """Custom validation error exception."""

    pass


class Validators:
    """Utility class for input validation."""

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format.

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password strength.

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"

        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"

        if not re.search(r"\d", password):
            return False, "Password must contain at least one digit"

        return True, None

    @staticmethod
    def validate_organization_name(name: str) -> tuple[bool, Optional[str]]:
        """
        Validate organization name.

        Args:
            name: Organization name to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(name) < 3:
            return False, "Organization name must be at least 3 characters long"

        if len(name) > 50:
            return False, "Organization name must be at most 50 characters long"

        # SQL injections check also because we are smart.
        sql_patterns = [
            r"(\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b)",
            r"(--|;|\/\*|\*\/)",
        ]

        for pattern in sql_patterns:
            if re.search(pattern, name, re.IGNORECASE):
                return False, "Organization name contains invalid characters"

        return True, None

    @staticmethod
    def sanitize_input(input_string: str) -> str:
        """
        Sanitize user input to prevent injection attacks.

        Args:
            input_string: String to sanitize

        Returns:
            Sanitized string
        """
        # Remove any null bytes
        sanitized = input_string.replace("\x00", "")

        # Remove leading/trailing whitespace
        sanitized = sanitized.strip()

        return sanitized
