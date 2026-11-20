import socket
import threading
import paramiko
from datetime import datetime

# Load HoneyTrap's SSH host key
host_key = paramiko.Ed25519Key.from_private_key_file(
    "honeytrap_host_key"
)

def log_event(message):
        with open("honeytrap.log", "a") as file:
            file.write(message + "\n")


class HoneyTrapServer(paramiko.ServerInterface):
    def check_auth_password(self, username, password):

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        message = f"[{timestamp}] Login attempt — Username: {username}"

        print(message)
        log_event(message)
        
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return "password"
    
    def check_channel_request(self, kind, chanid):

        if kind == "session":
            return paramiko.OPEN_SUCCEEDED

        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        return True


def handle_client(client_socket, client_address):

    transport = paramiko.Transport(client_socket)

    try:
        transport.add_server_key(host_key)

        server = HoneyTrapServer()

        transport.start_server(server=server)
        transport.auth_timeout = 20

        while not transport.is_authenticated() and transport.is_active():
            threading.Event().wait(0.1)

        if transport.is_authenticated():
            print(f"Authentication successful: {client_address[0]}")
        else:
            print(f"Authentication failed or connection closed: {client_address[0]}")

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