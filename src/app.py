"""
App module.
"""
from src.settings import Settings
from src.client import ClientManager
from src.user import UserManager


class App:
    """
    Application.
    """

    def __init__(self):
        # Application settings
        self.settings = Settings()

        # Client manager
        self.client_manager = ClientManager()

        # User manager
        self.user_manager = UserManager(self.settings)
