import socket
import os


def send_file(server_address, port, file_path):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_address, port))

    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    # client_socket.send(file_name.encode())
    client_socket.send(str(file_size).encode())

    print(f"Sending {file_name} ({file_size} bytes)")

    with open(file_path, "rb") as file:
        for data in iter(lambda: file.read(1024), b""):
            client_socket.sendall(data)

    print("File sent successfully")
    client_socket.close()


if __name__ == "__main__":
    server_address = "127.0.0.1"  # Change to the server's IP address
    port = 61111  # Change to the server's port number
    file_path = "../res/data.txt"  # Change to the path of the file you want to send
    send_file(server_address, port, file_path)
