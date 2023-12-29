import socket
import os


def receive_file(server_address, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_address, port))
    server_socket.listen(5)

    print(f"Server listening on {server_address}:{port}")

    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")

    # Receive file name
    # file_name = client_socket.recv(1024).decode()
    # print(f"Receiving {file_name}")

    # Receive file size as a string
    file_size_str = client_socket.recv(1024)

    file_size = int(file_size_str.decode())

    print(f"Receiving ({file_size} bytes)")

    with open("received.txt", "wb") as file:
        while file_size > 0:
            data = client_socket.recv(1024)
            file.write(data)
            file_size -= len(data)

    print("File received successfully")
    client_socket.close()
    server_socket.close()


if __name__ == "__main__":
    server_address = "127.0.0.1"  # Change to your desired IP address
    port = 61111  # Change to your desired port number
    receive_file(server_address, port)
