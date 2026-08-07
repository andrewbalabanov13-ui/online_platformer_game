import socket
import threading

PUBLIC_IP = "172.19.0.57"
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
    connection_lock = threading.Lock()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST,PORT))
        server.listen()

        print("listening")

        while True:
            conn, address = server.accept()

            print(f"accepted client, adress: {address}")

            

            thread = threading.Thread(target=thread_handle,args=(conn,address,connection_lock,connections),daemon=True)
            with connection_lock:
                connections[address]=conn

            thread.start()


main()