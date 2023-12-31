"""Dummy client module for testing the server."""
import os
import socket
from dotenv import load_dotenv
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Load environment variables
if os.path.exists(".env"):
    load_dotenv(".env")

# Server configuration
IP = os.getenv("SERVER_ADDRESS")
PORT = int(os.getenv("PORT"))
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"


def generate_ecdh_key_pair():
    """Generates a new ECDH key pair."""
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    public_key = private_key.public_key()
    return private_key, public_key


def perform_ecdh_key_exchange(conn):
    """Performs ECDH key exchange with the server."""
    # Generate ECDH key pair
    client_private_key, client_public_key = generate_ecdh_key_pair()

    # Send client's public key to the server
    serialized_public_key = client_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    conn.send(serialized_public_key)

    # Receive server's public key
    server_public_key_bytes = conn.recv(SIZE)
    server_public_key = serialization.load_pem_public_key(
        server_public_key_bytes, backend=default_backend()
    )

    # Perform ECDH key exchange
    shared_key = client_private_key.exchange(ec.ECDH(), server_public_key)

    # Use the shared key for encryption
    cipher = Cipher(
        algorithms.AES(shared_key),
        modes.CFB(b"\0" * 16),
        backend=default_backend(),
    )
    encryptor = cipher.encryptor()
    decryptor = cipher.decryptor()

    return encryptor, decryptor


def main():
    """Main function."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    encryptor, decryptor = perform_ecdh_key_exchange(client)
    # print(f"[SERVER]: {shared_key}")

    while True:
        data = client.recv(SIZE)
        data = decryptor.update(data).decode(FORMAT)
        cmd, msg = data.split("@")

        if cmd == "DISCONNECTED":
            print(f"[SERVER]: {msg}")
            break
        elif cmd == "OK":
            print(f"{msg}")

        data = input("> ")
        data = data.split(" ")
        cmd = data[0]

        if cmd == "HELP":
            encrypted_cmd = encryptor.update(cmd.encode(FORMAT))
            client.send(encrypted_cmd)
        elif cmd == "LOGOUT":
            encrypted_cmd = encryptor.update(cmd.encode(FORMAT))
            client.send(encrypted_cmd)
            break
        elif cmd == "LIST":
            encrypted_cmd = encryptor.update(cmd.encode(FORMAT))
            client.send(encrypted_cmd)
        elif cmd == "DELETE":
            cmd = f"{cmd}@{data[1]}"
            encrypted_cmd = encryptor.update(cmd.encode(FORMAT))
            client.send(encrypted_cmd)
        elif cmd == "UPLOAD":
            filepath = data[1]

            # Get the filename and filesize
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)

            # Create the command
            cmd = f"{cmd}@{filename}@{filesize}"
            # Encrypt the command
            encrypted_command = encryptor.update(cmd.encode(FORMAT))
            # Send the command
            client.send(encrypted_command)

            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(SIZE), b""):
                    encrypted_chunk = encryptor.update(chunk)
                    client.send(encrypted_chunk)

    print("Disconnected from the server.")
    client.close()


if __name__ == "__main__":
    main()
