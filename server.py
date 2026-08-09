import socket
import threading
import time
import online_platformer
import struct
COMPUTER_IP = "172.16.0.0"
PUBLIC_IP = "192.168.1.133"
HOST = "25.0.141.101"
PORT = 443

def check_legitimacy_of_packet(x, y, other_id, other_level):
    try:
        if x < 0 or x > 480: return False
        if y > 360 or y < 0: return False
        if other_id < 0 or other_id > 4294967295: return False
        if other_level < 0 or other_level > 10: return False
        return True
    except:
        return False

def anti_cheat(x,y,this_id,level,previous_data,address):
    level_change_or_reset_check = False
    if address not in previous_data:
        return True
    
    time_since_last_socket = time.time() - previous_data[address][2]
    maximum_x_changed = online_platformer.SPEED * 60 * time_since_last_socket
    x_change = abs(previous_data[address][0] - x)

    if x_change > maximum_x_changed+5:
        world = load(level)
        x_start,y_start = get_spawnpoint(world)
        if x > x_start-10 and x < x_start+10:
            level_change_or_reset_check = True

        if level_change_or_reset_check == False:
            return False

    return True
    
def load(level):
    with open("level_data.txt", "r") as file:
        data = file.readlines()

    level_string = data[level].strip()
    loaded_data_in_list = []
    i = 0
    for _ in range(online_platformer.GRID_Y):
        append_list = []
        for _ in range(online_platformer.GRID_X):
            append_list.append(level_string[i])
            i += 1
        loaded_data_in_list.append(append_list)
    return loaded_data_in_list

def get_spawnpoint(world):
    r = 0
    for row in world:
        c = 0
        for wall in row:
            if wall == "s":
                return (c*online_platformer.TILE_GRID_SIZE,r*online_platformer.TILE_GRID_SIZE)
            c += 1
        r += 1


def thread_handle(conn,address,connection_lock,connections,previous_data):
    buffer = bytearray()

    try:
        while True:
            data = conn.recv(1024)
            buffer.extend(data)
            while len(buffer) >= 16:
                x, y, this_id, level = struct.unpack_from(
                    "!IIII",
                    buffer,
                    0
                )
                del buffer[:16]
            

            Legitimate_packet = check_legitimacy_of_packet(x,y,this_id,level)

            if not Legitimate_packet:
                print("given invalid packet")
                raise Exception("Invalid Packet")
           

            valid_packet = anti_cheat(x,y,this_id,level,previous_data,address)
            previous_data[address] = (x,y,time.time(),level)
            
            if not valid_packet:
                print("Client Anticheat detected")
                raise Exception("Anticheat")
            if Legitimate_packet and valid_packet:
                with connection_lock:
                    for other_adress, other_conn  in connections.items():
                        if other_adress != address:
                            other_conn.sendall(data)




    except (ConnectionResetError, BrokenPipeError, OSError) as error:
        print("connection lost")
    
    except Exception as error:
        print(f"connection lost, reason: {error}")

    finally:
        conn.close()
        with connection_lock:
            del connections[address]
    
        print(f"client deleted, adress: {address}")

def main():
    previous_data = {}
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
                    previous_connection[client_ip] = time.time()
            
            if deny_connection:
                conn.close()
            
            if not deny_connection:
                previous_connection[address[0]]=time.time()
                thread = threading.Thread(target=thread_handle,args=(conn,address,connection_lock,connections,previous_data),daemon=True)
                with connection_lock:
                    connections[address]=conn
                print(f"accepted client, adress: {address}")

                thread.start()


main()