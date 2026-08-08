import pygame
import ast
import os
import socket
import threading
import struct
import random
import time

OTHER_PLAYERS = {}

SERVER_HOST = "192.168.1.133"
SERVER_PORT = 443

SEND_TICKS = 4

SPEED = 2

GRID_X = 40
GRID_Y = 30
LEVEL = 0
DATA_FILE = "level_data.txt"

GROUNDED = True

WIDTH = 480
HEIGHT = 360

RED = (255, 0, 0)
ORANGE = (255, 127, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (153, 0, 255) 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)


TILE_GRID_SIZE = WIDTH / GRID_X  # Evaluates to 12

clock = pygame.time.Clock()

player_rect = pygame.Rect(-1,-1,TILE_GRID_SIZE,TILE_GRID_SIZE)

player_float_x = 0.0
player_float_y = 0.0

speed_x = 0
speed_y = 0

screen = pygame.display.set_mode((WIDTH,HEIGHT))

def ensure_file_exists():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as file:
            file.write((("0" * GRID_X) * GRID_Y) + "\n")

def load():
    ensure_file_exists()
    with open(DATA_FILE, "r") as file:
        data = file.readlines()

    level_string = data[LEVEL].strip()
    loaded_data_in_list = []
    i = 0
    for _ in range(GRID_Y):
        append_list = []
        for _ in range(GRID_X):
            append_list.append(level_string[i])
            i += 1
        loaded_data_in_list.append(append_list)
    return loaded_data_in_list

def get_level_data():
    with open (DATA_FILE,"r") as file:
        level_data = load()
    return level_data

def set_spawnpoint(world):
    global player_float_x, player_float_y
    r = 0
    for row in world:
        c = 0
        for wall in row:
            if wall == "s":
                player_rect.x = c*TILE_GRID_SIZE
                player_rect.y = r*TILE_GRID_SIZE
                player_float_x = float(player_rect.x)
                player_float_y = float(player_rect.y)
                return 
            c += 1
        r += 1

def draw(world):
    y = 0
    for row in world:
        x = 0
        for col in row:
            if col == "0":
                pygame.draw.rect(screen, WHITE, (x, y, TILE_GRID_SIZE, TILE_GRID_SIZE))
            elif col == "w":
                pygame.draw.rect(screen, GRAY, (x, y, TILE_GRID_SIZE, TILE_GRID_SIZE))
            elif col == "k":
                pygame.draw.rect(screen, RED, (x, y, TILE_GRID_SIZE, TILE_GRID_SIZE))
            elif col == "s":
                pygame.draw.rect(screen, (0, 255, 255), (x, y, TILE_GRID_SIZE, TILE_GRID_SIZE))
            elif col == "e":
                pygame.draw.rect(screen, ORANGE, (x, y, TILE_GRID_SIZE, TILE_GRID_SIZE))
            elif col == "b":
                pygame.draw.rect(screen, GREEN, (x, y, TILE_GRID_SIZE, TILE_GRID_SIZE))
            elif col == "u":
                pygame.draw.rect(screen,YELLOW,(x,y,TILE_GRID_SIZE,TILE_GRID_SIZE))
            
            x += TILE_GRID_SIZE  
        y += TILE_GRID_SIZE

def check_if_colliding_x(world):
    global player_float_x
    global speed_x
    global speed_y
    global LEVEL
    up_wall_touched = False
    r = 0
    for row in world:
        c = 0
        for wall in row:
            if wall == "w":
                tile_rect = pygame.Rect(c*TILE_GRID_SIZE, r*TILE_GRID_SIZE, TILE_GRID_SIZE, TILE_GRID_SIZE)
                if player_rect.colliderect(tile_rect):
                    if speed_x > 0: 
                        player_rect.right = tile_rect.left
                    elif speed_x < 0: 
                        player_rect.left = tile_rect.right
                    player_float_x = float(player_rect.x)
                     
            elif wall == "k":
                tile_rect = pygame.Rect(c*TILE_GRID_SIZE, r*TILE_GRID_SIZE, TILE_GRID_SIZE, TILE_GRID_SIZE)
                if player_rect.colliderect(tile_rect):
                    set_spawnpoint(world)
                    speed_x = 0
                    speed_y = 0
            elif wall == "b":
                tile_rect = pygame.Rect(c*TILE_GRID_SIZE, r*TILE_GRID_SIZE, TILE_GRID_SIZE, TILE_GRID_SIZE)
                if player_rect.colliderect(tile_rect):
                    if speed_y > 0:
                        speed_y = speed_y * -0.8
            elif wall == "e":
                tile_rect = pygame.Rect(c*TILE_GRID_SIZE, r*TILE_GRID_SIZE, TILE_GRID_SIZE, TILE_GRID_SIZE)
                if player_rect.colliderect(tile_rect):
                    LEVEL += 1
                    new_world = load()
                    set_spawnpoint(new_world)
                    
            elif wall == "u":
                tile_rect = pygame.Rect(c*TILE_GRID_SIZE, r*TILE_GRID_SIZE, TILE_GRID_SIZE, TILE_GRID_SIZE)
                if player_rect.colliderect(tile_rect):
                    if up_wall_touched == False:
                        speed_y -= 0.75
                        up_wall_touched = True
            c += 1
        r += 1

def check_if_colliding_y(world):
    global speed_y, player_float_y, GROUNDED
    r = 0
    for row in world:
        c = 0
        for wall in row:
            if wall == "w":
                tile_rect = pygame.Rect(c*TILE_GRID_SIZE, r*TILE_GRID_SIZE, TILE_GRID_SIZE, TILE_GRID_SIZE)
                if player_rect.colliderect(tile_rect):
                    GROUNDED = True
                    if speed_y > 0: 
                        player_rect.bottom = tile_rect.top
                        speed_y = 0
                    elif speed_y < 0: 
                        player_rect.top = tile_rect.bottom
                        GROUNDED = False
                        speed_y = 0
                    player_float_y = float(player_rect.y)
                    return 
            c += 1
        r += 1
    GROUNDED = False
def move_player(world):
    global player_float_x, player_float_y

    player_float_x += speed_x
    player_rect.x = int(player_float_x)
    check_if_colliding_x(world)
    if player_rect.left < 0:
        player_rect.left = 0
    if player_rect.right > WIDTH:
        player_rect.right = WIDTH
    player_float_y += speed_y
    player_rect.y = int(player_float_y)
    check_if_colliding_y(world)
    if player_rect.top < 0:
        player_rect.top = 0
    if player_rect.bottom > HEIGHT:
        player_rect.bottom = HEIGHT

def thread_handle(conn):
    try:
        while True:
            data_recieved = bytearray()
            while True:
                data = conn.recv(1024)
                data_recieved.extend(data)
                if len(data_recieved) >= 16:
                    break

            x,y,other_id,LEVEL = struct.unpack_from("!IIII", data_recieved, offset=0)

            OTHER_PLAYERS[other_id]=(x,y,time.time(),LEVEL)

            print("recieved")

    except (ConnectionResetError, BrokenPipeError, OSError) as error:
        print("connection lost")

    finally:
        conn.close()
    

def main():
    global speed_x, speed_y, GROUNDED
    
    socket_buffer = 0

    client_id = random.randint(0, 4294967295)

    running = True

    world = get_level_data()
    set_spawnpoint(world)
    print("It gets to this point")
    with socket.create_connection((SERVER_HOST,SERVER_PORT)) as connection:
        print("connected to server")
        thread = threading.Thread(target=thread_handle,args=(connection,),daemon=True)

        thread.start()


        while running:
            socket_buffer += 1


            world = get_level_data()

            screen.fill(BLACK)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            keys = pygame.key.get_pressed()
            speed_x = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                speed_x -= SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                speed_x += SPEED

            speed_y += 0.4

            if keys[pygame.K_UP] or keys[pygame.K_w]:
                if GROUNDED:
                    speed_y = -5.4
                    GROUNDED = False


            move_player(world)
            draw(world)

            if socket_buffer > SEND_TICKS:
                socket_buffer = 0

                message = struct.pack("!IIII",max(1,int(player_float_x)),max(1,int(player_float_y)),client_id,LEVEL)

                connection.sendall(message)
                # print("sent")
            remove_key = []
            for other_id, (x,y,t,l) in OTHER_PLAYERS.items():
                if time.time() - t > 10:
                    remove_key.append(other_id)
                    print('added')
                if l == LEVEL:
                    color_data = other_id.to_bytes(4, byteorder="little")
                    color = (color_data[0], color_data[1], color_data[2])
                    pygame.draw.rect(screen,color,(x,y,TILE_GRID_SIZE,TILE_GRID_SIZE))
            
            for remove_id in remove_key:
                del OTHER_PLAYERS[remove_id]

            pygame.draw.rect(screen,BLUE,player_rect)
            pygame.display.flip()

            clock.tick(60)
main()
