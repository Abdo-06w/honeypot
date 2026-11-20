import socket
import threading
import paramiko

# Load HoneyTrap's SSH host key
host_key = paramiko.Ed25519Key.from_private_key_file(
    "honeytrap_host_key"
)

class HoneyTrapServer(paramiko.ServerInterface):

    def check_auth_password(self, username, password):
        print(f"Login attempt — Username: {username}")
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return "password"


def handle_client(client_socket, client_address):

    transport = paramiko.Transport(client_socket)

    try:
        transport.add_server_key(host_key)

        server = HoneyTrapServer()

        transport.start_server(server=server)

        print(f"SSH connection established with {client_address[0]}")

    except Exception as error:
        print(f"SSH error: {error}")

    finally:
        transport.close()
        client_socket.close()


def start_server():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind(("127.0.0.1", 2222))

    server_socket.listen(5)

    print("HoneyTrap SSH server listening on port 2222...")

    while True:
        client_socket, client_address = server_socket.accept()

        client_thread = threading.Thread(
            target=handle_client,
            args=(client_socket, client_address)
        )

        client_thread.start()


if __name__ == "__main__":
    start_server()