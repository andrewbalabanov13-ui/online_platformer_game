import pygame
import math
import os

pygame.init()
screen = pygame.display.set_mode((480, 360))

RED = (255, 0, 0)
ORANGE = (255, 127, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (153, 0, 255) 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
CYAN = (0,255,255)

LEVEL_SELECTED = 0
GRID_X = 40
GRID_Y = 30
TILE_GRID_SIZE = 480 / GRID_X  # Evaluates to 12
WALL_TYPES = ["0", "w", "k", "s", "e", "b", "u"]
WALL_COLORS = [WHITE,GRAY,RED,CYAN,ORANGE,GREEN,YELLOW]
WALL_SELECTED = 0
DATA_FILE = "level_data.txt"

def unload(world):
    return_str = ""
    for row in world:
        for character in row:
            return_str += character
    return return_str

def load():
    ensure_file_exists()
    with open(DATA_FILE, "r") as file:
        data = file.readlines()
    
    # Safety fallback if level line is missing or corrupted
    if LEVEL_SELECTED >= len(data) or len(data[LEVEL_SELECTED].strip()) < (GRID_X * GRID_Y):
        return [["0" for _ in range(GRID_X)] for _ in range(GRID_Y)]

    level_string = data[LEVEL_SELECTED].strip()
    loaded_data_in_list = []
    i = 0
    for _ in range(GRID_Y):
        append_list = []
        for _ in range(GRID_X):
            append_list.append(level_string[i])
            i += 1
        loaded_data_in_list.append(append_list)
    return loaded_data_in_list

def ensure_file_exists():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as file:
            file.write((("0" * GRID_X) * GRID_Y) + "\n")

def add_line_to_prevent_error():
    ensure_file_exists()
    with open(DATA_FILE, "r") as file:
        data = file.readlines()
    
    # If we need a new level, open in append mode freshly so pointer behaves
    if LEVEL_SELECTED + 1 > len(data):
        with open(DATA_FILE, "a") as file:
            file.write((("0" * GRID_X) * GRID_Y) + "\n")

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
                pygame.draw.rect(screen, YELLOW, (x, y, TILE_GRID_SIZE, TILE_GRID_SIZE))
            
            
            x += TILE_GRID_SIZE  
        y += TILE_GRID_SIZE

def replace_data_with_new_data(data):
    with open(DATA_FILE, "w") as file:
        for line in data:
            line_without_space = line.strip()
            if line_without_space: 
                file.write(line_without_space + "\n") 

def draw_wall_cursor(mouse_x,mouse_y):
    rounded_x = math.floor(mouse_x / TILE_GRID_SIZE) * TILE_GRID_SIZE
    rounded_y = math.floor(mouse_y / TILE_GRID_SIZE) * TILE_GRID_SIZE
    pygame.draw.rect(screen,WALL_COLORS[WALL_SELECTED],(rounded_x,rounded_y,TILE_GRID_SIZE,TILE_GRID_SIZE))



def check_if_out_of_bounds(x, y):
    if x >= 480 or x < 0 or y >= 360 or y < 0:
        return True
    return False

def place_wall(mouse_x, mouse_y):
    if check_if_out_of_bounds(mouse_x, mouse_y):
        return
    
    with open(DATA_FILE, "r") as file:
        data = file.readlines()

    world = load()
    rounded_x = math.floor(mouse_x / TILE_GRID_SIZE) 
    rounded_y = math.floor(mouse_y / TILE_GRID_SIZE)
    
    if rounded_y < len(world) and rounded_x < len(world[0]):
        world[rounded_y][rounded_x] = WALL_TYPES[WALL_SELECTED]
        new_line = unload(world)
        data[LEVEL_SELECTED] = new_line
        replace_data_with_new_data(data)

def main():
    global WALL_SELECTED, WALL_TYPES, LEVEL_SELECTED
    running = True
    clock = pygame.optimizations = pygame.time.Clock() 

    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    if WALL_SELECTED + 1 != len(WALL_TYPES):
                        WALL_SELECTED += 1 
                if event.key == pygame.K_n:
                    if WALL_SELECTED != 0:
                        WALL_SELECTED -= 1
                if event.key == pygame.K_p:
                    LEVEL_SELECTED += 1
                if event.key == pygame.K_o:
                    if LEVEL_SELECTED != 0:
                        LEVEL_SELECTED -= 1
                        
        add_line_to_prevent_error()
        world = load()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            place_wall(mouse_x, mouse_y)

        draw(world)

        draw_wall_cursor(mouse_x,mouse_y)

        pygame.display.flip()
        clock.tick(60) 

    pygame.quit()

main()