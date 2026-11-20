
import socket
import threading
from datetime import datetime

def log_event(message):
    with open("honeytrap.log", "a") as file:
        file.write(message + "\n")

def receive_ssh_banner(connection):
    banner = b""

    while not banner.endswith(b"\n"):
        byte = connection.recv(1)

        if not byte:
            break

        banner += byte

    return banner.decode(errors="replace").strip()

def handle_client(connection,ip):

    server_banner = "SSH-2.0-OpenSSH_9.6\r\n"
    connection.sendall(server_banner.encode())

    connection_time = datetime.now().strftime("%Y-%m-%d %Hh:%Mm")
    
    log_event(f"New connection from {ip} at {connection_time}")
    print(f"New connection: {ip} at {connection_time}")

    client_banner = receive_ssh_banner(connection)
    
    print(f"Client SSH banner: {client_banner}")
    log_event(f"Client SSH banner: {client_banner}")

    connection.settimeout(10)

    try:
        while True:
            data = connection.recv(4096)

            if not data:
                break

            print(f"Received {len(data)} bytes from {ip}")
            log_event(f"Received {len(data)} bytes from {ip}")

    except socket.timeout:
        print(f"{ip} timed out waiting for more data")

    finally:
        disconnect_time = datetime.now().strftime("%Y-%m-%d %Hh:%Mm")
        log_event(f"{ip} disconnected at {disconnect_time}")
        print(f"{ip} disconnected at {disconnect_time}")
        connection.close()



server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 1234))
server.listen(5)

print("HoneyTrap is listening on port 1234...")

while True:

    connection, address = server.accept()
    client_ip = address[0]

    client_thread = threading.Thread(
        target=handle_client,
        args=(connection,client_ip)
    )

    client_thread.start()



