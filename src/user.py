"""
User module.
"""
import uuid
from typing import Dict, Set

from src.client import Client
from src.settings import Settings
from src.transmittable import Transmittable


class User:
    """
    User.
    :author: James Chan
    """

    def __init__(self, user_manager: "UserManager", username: str, pin: str):
        # The user manager creating this user
        self._user_manager: UserManager = user_manager

        # The username of this user
        self.username = username

        # The pin of this user
        self.pin = pin

        # Clients that are associated with this user
        self.client_set: Set[Client] = set()

    def add_client(self, client: Client) -> None:
        """
        Associates a client with this user.
        :param client: The client to associate.
        """
        self.client_set.add(client)

    def remove_client(self, client: Client) -> None:
        """
        Dissociate a client with this user. If the client is the last one to dissociate,
        this user is removed from the user manager.
        :param client: The client to dissociate.
        """
        self.client_set.remove(client)

        if len(self.client_set) == 0:
            self._user_manager.remove_user(self.username)

    def get_associated_client(self) -> Set[Client]:
        """
        Returns all the clients that associated with this user.
        """
        return self.client_set

    def broadcast(self, sender: Client, transmittable: Transmittable) -> None:
        """
        Broadcasts a transmittable object from a client to all other clients.
        :param sender: The client sending the transmittable object.
        :param transmittable: The transmittable object to broadcast.
        """
        for client in self.client_set - {sender}:
            client.send(transmittable)

    def __repr__(self):
        return f"User[username={self.username}; pin={self.pin}]"


class UserManager:
    """
    User manager.
    :author: James Chan
    """

    def __init__(self, settings: Settings):
        # App settings
        self.settings = settings

        # Mapping from username to the corresponding user instance
        self.by_username: Dict[str, User] = {}

    def get_by_username(self, username: str) -> User | None:
        """
        Retrieves a user based on the provided username.
        :param username: The username of the user to retrieve.
        :return: The user object associated with the provided username, or None if not found.
        """
        return self.by_username.get(username)

    def register_user(self, username: str, pin: str) -> User:
        """
        Registers a user.
        :param username: The username of the user to register.
        :param pin: The pin of the user to register.
        :return: The registered user object.
        """
        user = User(self, username, pin)
        self.by_username[username] = user

        return user

    def remove_user(self, username: str) -> None:
        """
        Removes a user from this user manager.
        :param: The username of the user to remove.
        """
        del self.by_username[username]

    def create_temporary_user(self) -> User:
        """
        Creates a temporary user. The temporary user is registered before being returned.
        """
        username = self.__generate_username()
        pin = self.__generate_pin(self.settings.pin_length)

        return self.register_user(username, pin)

    def __generate_username(self) -> str:
        """
        Generates a username. The username is guaranteed to be unique.
        :return: A unique username.
        """
        while True:
            username = str(uuid.uuid4())
            if self.by_username.get(username) is None:
                return username

    # noinspection PyMethodMayBeStatic
    def __generate_pin(self, n: int) -> str:
        """
        Generates an n-digit pin.
        :param n: The number of digits.
        :return: An n-digit pin string.
        """
        return "1" * n
