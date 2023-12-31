"""Multi-threaded server that transfers files between clients."""
import os
import socket
import threading
from dotenv import load_dotenv
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from typing import Dict, Any

# Load environment variables
if os.path.exists(".env"):
    load_dotenv(".env")

# Server configuration
IP = os.getenv("SERVER_ADDRESS")
PORT = int(os.getenv("PORT"))
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = os.getenv("SERVER_DATA_PATH")

# Map socket connections to shared keys
shared_keys: Dict[Any, bytes] = {}


# ECDH key pair generation
def generate_ecdh_key_pair() -> tuple:
    """Generates a new ECDH key pair."""
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    public_key = private_key.public_key()
    return private_key, public_key


def perform_ecdh_key_exchange(conn) -> bytes:
    """Performs ECDH key exchange with the client."""
    # Generate ECDH key pair
    server_private_key, server_public_key = generate_ecdh_key_pair()

    # Send server's public key to the client
    serialized_public_key = server_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    conn.send(serialized_public_key)

    # Receive client's public key
    client_public_key_bytes = conn.recv(SIZE)
    client_public_key = serialization.load_pem_public_key(
        client_public_key_bytes, backend=default_backend()
    )

    # Perform ECDH key exchange
    shared_key = server_private_key.exchange(ec.ECDH(), client_public_key)

    return shared_key


def handle_client(conn, addr) -> None:
    """Handles a new client connection."""
    print(f"[NEW CONNECTION] {addr} connected.")

    # Perform ECDH key exchange
    shared_key = perform_ecdh_key_exchange(conn)

    # Store the shared key
    shared_keys[conn] = shared_key
    print(f"[SHARED KEY] Address: {addr} Key: {shared_key}")

    conn.send("OK@Welcome to the File Server.".encode(FORMAT))

    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        cmd = data[0]

        if cmd == "LIST":
            files = os.listdir(SERVER_DATA_PATH)
            send_data = "OK@"

            if len(files) == 0:
                send_data += "The server directory is empty"
            else:
                send_data += "\n".join(f for f in files)
            conn.send(send_data.encode(FORMAT))

        elif cmd == "UPLOAD":
            filename, filesize = data[1], int(data[2])
            filepath = os.path.join(SERVER_DATA_PATH, filename)

            with open(filepath, "wb") as f:
                received_data = 0
                while received_data < filesize:
                    chunk = conn.recv(SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
                    received_data += len(chunk)

            send_data = "OK@File uploaded successfully."
            conn.send(send_data.encode(FORMAT))

        elif cmd == "DELETE":
            files = os.listdir(SERVER_DATA_PATH)
            send_data = "OK@"
            filename = data[1]

            if len(files) == 0:
                send_data += "The server directory is empty"
            else:
                if filename in files:
                    os.system(f"rm {SERVER_DATA_PATH}/{filename}")
                    send_data += "File deleted successfully."
                else:
                    send_data += "File not found."

            conn.send(send_data.encode(FORMAT))

        elif cmd == "LOGOUT":
            break
        elif cmd == "HELP":
            data = "OK@"
            data += "LIST: List all the files from the server.\n"
            data += "UPLOAD <path>: Upload a file to the server.\n"
            data += "DELETE <filename>: Delete a file from the server.\n"
            data += "LOGOUT: Disconnect from the server.\n"
            data += "HELP: List all the commands."

            conn.send(data.encode(FORMAT))

        else:
            conn.send("OK@Invalid command.".encode(FORMAT))

    print(f"[DISCONNECTED] {addr} disconnected")
    conn.close()


def main():
    """Main function."""
    print("[STARTING] Server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}.")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


if __name__ == "__main__":
    main()
