"""
Client module.
"""

from typing import Set, TYPE_CHECKING
from abc import ABC, abstractmethod
import socket

from src.transmittable import Transmittable

if TYPE_CHECKING:
    from src.user import User

# link: https://github.com/typinghare/min-send-server/blob/pat-dev/src/client.py

# The socket class in the socket module (I wonder why they don't apply PascalCase to class names)
Socket = socket.socket


class Client(ABC):
    """
    A socket wrapper.
    :author: James Chan
    """

    def __init__(self, _socket: Socket, user: "User"):
        # Client socket
        self.socket = _socket

        # The user this client is associated with
        self.user: User = user

    @abstractmethod
    def send(self, transmittable: Transmittable) -> None:
        """
        Sends a transmittable object via the socket.
        :param transmittable: The transmittable object to send.
        """

    def receive(self, transmittable: Transmittable) -> None:
        """
        This client receives a transmittable object.
        :param transmittable: The received transmittable object.
        """
        self.user.broadcast(self, transmittable)


class ClientManager:
    """
    Client manager.
    :author: James Chan
    """

    def __init__(self):
        """
        A set of clients.
        """
        self.client_set: Set[Client] = set()
