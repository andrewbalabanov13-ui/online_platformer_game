import socket
import threading
import time
COMPUTER_IP = "172.16.0.0"
PUBLIC_IP = "192.168.1.133"
HOST = "25.0.141.101"
PORT = 443


def thread_handle(conn,address,connection_lock,connections):
    try:
        while True:
            data = conn.recv(1024)
            with connection_lock:
                for other_adress, other_conn  in connections.items():
                    if other_adress != address:
                        other_conn.sendall(data)

    except (ConnectionResetError, BrokenPipeError, OSError) as error:
        print("connection lost")
    
    finally:
        conn.close()
        with connection_lock:
            del connections[address]
    
        print(f"client deleted, adress: {address}")

def main():
    connections = {}
    previous_connection = {}
    connection_lock = threading.Lock()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("",PORT))
        server.listen()

        print("listening")

        while True:
            deny_connection = False
            conn, address = server.accept()
            with connection_lock:
                for other_adress, other_con in connections.items():
                    if other_adress[0] == address[0]:
                        deny_connection = True
            client_ip = address[0]

            if client_ip in previous_connection:
                if time.time() - previous_connection[client_ip] < 10:
                    deny_connection = True

            if not deny_connection:
                previous_connection[address[0]]=time.time()
                thread = threading.Thread(target=thread_handle,args=(conn,address,connection_lock,connections),daemon=True)
                with connection_lock:
                    connections[address]=conn
                print(f"accepted client, adress: {address}")

                thread.start()


main()