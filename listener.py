
import socket
import threading
from datetime import datetime

def log_event(message):
    with open("honeytrap.log", "a") as file:
        file.write(message + "\n")

def handle_client(connection,ip):
    
    connection_time = datetime.now().strftime("%Y-%m-%d %Hh:%Mm")
    
    log_event(f"New connection from {ip} at {connection_time}")
    print(f"New connection: {ip} at {connection_time}")

    while True:
        data = connection.recv(1024)
        msg = data.decode(errors='replace')

        if not data:
            break
            
        log_event(f"Data received from {ip}: {msg}")
        print(f"({ip}): {msg}")

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


server.close()
