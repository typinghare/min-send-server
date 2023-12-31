"""File Server Module."""

import os
import socket
import threading
from dotenv import load_dotenv
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers import CipherContext
from typing import Dict, Any


class Server:
    """File Transfer Server."""

    def __init__(self, ip, port, server_data_path) -> None:
        # Server configuration
        self._ip = ip
        self._port = port
        self._addr = (self._ip, self._port)
        self._size = 1024
        self._format = "utf-8"
        self._server_data_path = server_data_path

        # Create a new server
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Map socket connections to shared keys
        self.connection_directory: Dict[
            Any, (ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey)
        ] = {}

    def start(self) -> None:
        """Starts the server."""
        # Print a server starting message
        print("[STARTING] Server is starting")
        # Bind the server to the server address and port
        self._server.bind(self._addr)
        # Start listening for connections
        self._server.listen()
        # Print a server listening message
        print(f"[LISTENING] Server is listening on {self._ip}:{self._port}.")

        # Start accepting connections
        while True:
            # Accept a new connection
            conn, addr = self._server.accept()
            # Create a new thread to handle the new connection
            thread = threading.Thread(
                target=self._handle_client, args=(conn, addr)
            )
            # Start the thread
            thread.start()
            # Print the number of active connections
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

    # ECDH key pair generation
    def _generate_ecdh_key_pair(
        self,
    ) -> (ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey):
        """Generates a new ECDH key pair."""
        # Generate the private key
        private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        # Generate the public key
        public_key = private_key.public_key()
        # Return the key pair
        return private_key, public_key

    def _perform_ecdh_key_exchange(
        self, conn
    ) -> (CipherContext, CipherContext):
        """Performs ECDH key exchange with the client."""
        # Generate ECDH key pair
        server_private_key, server_public_key = self._generate_ecdh_key_pair()

        # Serialize the public key
        serialized_public_key = server_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        # Send the public key to the client
        conn.send(serialized_public_key)

        # Receive client's public key
        client_public_key_bytes = conn.recv(self._size)
        # Deserialize the public key
        client_public_key = serialization.load_pem_public_key(
            client_public_key_bytes, backend=default_backend()
        )

        # Perform ECDH key exchange
        shared_key = server_private_key.exchange(ec.ECDH(), client_public_key)

        # Use the shared key for encryption
        cipher = Cipher(
            algorithms.AES(shared_key),
            modes.CFB(b"\0" * 16),
            backend=default_backend(),
        )

        # Create encryptor and decryptor
        encryptor = cipher.encryptor()
        decryptor = cipher.decryptor()

        # Store the encryptor and decryptor
        self.connection_directory[conn] = (encryptor, decryptor)

        return encryptor, decryptor

    def _handle_client(self, conn, addr) -> None:
        """Handles a new client connection."""
        print(f"[NEW CONNECTION] {addr} connected.")

        # Perform ECDH key exchange
        encryptor, decryptor = self._perform_ecdh_key_exchange(conn)

        # Send a welcome message
        conn.send(
            encryptor.update(
                "OK@Welcome to the File Server.".encode(self._format)
            )
        )

        while True:
            # Receive data from the client
            data = conn.recv(self._size)
            # Decrypt the data
            data = decryptor.update(data).decode(self._format)
            # Split the data into command and message
            data = data.split("@")
            cmd = data[0]

            if cmd == "LIST":
                files = os.listdir(self._server_data_path)
                send_data = "OK@"

                if len(files) == 0:
                    send_data += "The server directory is empty"
                else:
                    send_data += "\n".join(f for f in files)

                # Encrypt the data
                encrypted_send_data = encryptor.update(
                    send_data.encode(self._format)
                )
                conn.send(encrypted_send_data)

            elif cmd == "UPLOAD":
                filename, filesize = data[1], int(data[2])
                filepath = os.path.join(self._server_data_path, filename)

                received_data = 0
                decrypted_file_data = b""
                while received_data < filesize:
                    chunk = conn.recv(self._size)
                    decrypted_chunk = decryptor.update(chunk)
                    decrypted_file_data += decrypted_chunk
                    received_data += len(chunk)

                filepath = os.path.join(self._server_data_path, filename)
                with open(filepath, "wb") as f:
                    f.write(decrypted_file_data)

                send_data = "OK@File uploaded successfully."
                encrypted_response = encryptor.update(
                    send_data.encode(self._format)
                )
                conn.send(encrypted_response)

            elif cmd == "DELETE":
                # Get the filename
                filename = data[1]
                # Get the files from the server directory
                files = os.listdir(self._server_data_path)
                # Generate the response message
                send_data = "OK@"

                # Check if the server directory is empty
                if len(files) == 0:
                    send_data += "The server directory is empty"
                else:
                    # If the file exists, delete it
                    if filename in files:
                        os.system(f"rm {self._server_data_path}/{filename}")
                        send_data += "File deleted successfully."
                    # Otherwise, send an error message
                    else:
                        send_data += "File not found."

                # Encrypt the data
                encrypted_response = encryptor.update(
                    send_data.encode(self._format)
                )
                # Send the data
                conn.send(encrypted_response)

            elif cmd == "LOGOUT":
                break
            elif cmd == "HELP":
                # Generate the help message
                data = "OK@"
                data += "LIST: List all the files from the server.\n"
                data += "UPLOAD <path>: Upload a file to the server.\n"
                data += "DELETE <filename>: Delete a file from the server.\n"
                data += "LOGOUT: Disconnect from the server.\n"
                data += "HELP: List all the commands."

                # Encrypt the data
                encrypted_response = encryptor.update(data.encode(self._format))
                # Send the data
                conn.send(encrypted_response)

            else:
                # Generate the error message
                data = "ERROR@Invalid command."
                # Encrypt the data
                encrypted_response = encryptor.update(data.encode(self._format))
                # Send the data
                conn.send(encrypted_response)

        # Close the connection
        print(f"[DISCONNECTED] {addr} disconnected")
        conn.close()


if __name__ == "__main__":
    # Load environment variables
    if os.path.exists(".env"):
        load_dotenv(".env")

    # Server configuration
    IP = os.getenv("SERVER_ADDRESS")
    PORT = int(os.getenv("PORT"))
    SERVER_DATA_PATH = os.getenv("SERVER_DATA_PATH")

    # Create a new server
    server: Server = Server(IP, PORT, SERVER_DATA_PATH)
    server.start()
