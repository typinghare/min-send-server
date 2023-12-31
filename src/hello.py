import socket

from settings import Settings
from client import Socket, Client
# noinspection PyCompatibility
from user import UserManager

settings = Settings()
user_manager = UserManager(settings)
user = user_manager.create_temporary_user()

client = Client(Socket(socket.AF_INET, socket.SOCK_STREAM), user)
print(client.user.username)
print(client.user.pin)
