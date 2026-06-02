"""
SMPOOS Authentication Utilities
Handles admin login with environment variables and localStorage session management.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def verify_admin_credentials(username: str, password: str) -> bool:
    """
    Verify admin credentials against environment variables.

    Args:
        username: Entered username
        password: Entered password

    Returns:
        bool: True if credentials match, False otherwise
    """
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')

    return username == admin_username and password == admin_password


def get_admin_info() -> dict:
    """
    Get admin user information.

    Returns:
        dict: Admin user information
    """
    return {
        'username': os.getenv('ADMIN_USERNAME', 'admin'),
        'name': 'Administrator',
        'role': 'System Administrator',
        'email': 'admin@smpoos.com'
    }
