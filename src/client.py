"""
Client module.
"""

from typing import TYPE_CHECKING, Dict, Type
from abc import ABC, abstractmethod
import socket

from src.transmittable import Transmittable

if TYPE_CHECKING:
    from src.user import User

# link: https://github.com/typinghare/min-send-server/blob/pat-dev/src/client_test.py

# The socket class in the socket module (I wonder why they don't apply PascalCase to class names)
Socket = socket.socket


class Client(ABC):
    """
    A socket wrapper. This is an abstract class in which the send() method is remained to be
    implemented.
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

    def __repr__(self):
        return f"Client[socket={hex(id(self.socket))}; user={self.user}]"


class SocketClient(Client):
    """
    Socket client.
    """

    def send(self, transmittable: Transmittable) -> None:
        pass


class ClientManager:
    """
    Client manager.
    :author: James Chan
    """

    def __init__(self):
        # Mapping from socket to client
        self.by_socket: Dict[Socket, Client] = {}

        # Client class
        self.client_class: Type[Client] = SocketClient

    def register(self, _socket: Socket, user: "User") -> Client:
        """
        Registers a client.
        :param _socket: The socket of the client.
        :param user: The user the client associated with.
        :return: The registered client object.
        """
        client = self.client_class(_socket, user)
        self.by_socket[_socket] = client

        return client

    def get_by_socket(self, _socket: Socket) -> Client | None:
        """
        Retrieves a client by its socket.
        :param _socket: The socket of the client to retrieve.
        :return: The client associated with the given socket; None if the client does not exist.
        """
        return self.by_socket.get(_socket)
