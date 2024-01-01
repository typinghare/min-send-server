import socket

from src.app import App

app = App()

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
user = app.user_manager.create_temporary_user()
client = app.client_manager.register(socket, user)

print(client)
