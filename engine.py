import math
import map
import pygame
import numpy

aspect_ratio = 16 / 9
width = 1080
height = int(width / aspect_ratio)

# Camera
focal_lenght = 300
focal_lenght_old = focal_lenght
zoom = 3000

# Time
last_tick = 0


def distance(x1, y1, x2, y2):
    distance = math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)) 
    return distance
#_______________________________________________________________________________________

class Walls():
    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0
    color = (0, 0, 0)
    wall_texture = 0
    u = 0
    v = 0
    shade = 0

class Sectors():
    wall_start = 0
    wall_end = 0
    d = 0
    color1 = (0, 0, 0)
    color2 = (0, 0, 0)
    surf = [0 for i in range(width)]
    surface = 0
    z1 = 0
    z2 = 0
    surface_texture = 0
    surface_scale = 0

class TextureMaps():
    texture_width = 0
    texture_height = 0
    texture_name = "placeholder"

def loadMap():
    global textures, W, S
    textures = [TextureMaps() for i in range(64)]
    W = [Walls() for i in range(256)]
    S = [Sectors() for i in range(128)]
    v1 = 0
    v2 = 0
    for s in range(map.SECTOR_NUM):
        S[s].wall_start = map.loadSectors()[v1 + 0]
        S[s].wall_end = map.loadSectors()[v1 + 1]
        S[s].z1 = map.loadSectors()[v1 + 2]
        S[s].z2 = map.loadSectors()[v1 + 3] - map.loadSectors()[v1 + 2]
        S[s].color1 = map.loadSectors()[v1 + 4]
        S[s].color2 = map.loadSectors()[v1 + 5]
        v1 = v1 + 6
        for w in range(S[s].wall_start, S[s].wall_end):
            W[w].x1 = map.loadWalls()[v2+0]
            W[w].y1 = map.loadWalls()[v2+1]
            W[w].x2 = map.loadWalls()[v2+2]
            W[w].y2 = map.loadWalls()[v2+3]
            W[w].color = map.loadWalls()[v2+4]
            v2 = v2 + 5
loadMap()

def clipBehindPlayer(x1, y1, z1, x2, y2, z2):
    da = y1
    db = y2
    d = da - db
    if d == 0:  d = 1
    s = da / d
    x1 = x1 + s * (x2 - x1)
    y1 = y1 + s * (y2 - y1)
    if y1 <= 0.1:
        y1 = 1
    z1 = z1 + s * (z2 - z1)
    return x1, y1, z1

def drawWall(x1, x2, b1, b2, t1, t2, color, s, w, frontBack):
    dyb = b2 - b1
    dyt = t2 - t1
    dx = x2 - x1
    if dx == 0:
        dx = 1
    xs = x1
    # Clip x
    if x1 < 0:  x1 = 0
    if x2 < 0:  x1 = 0
    if x1 > width:  x1 = width
    if x2 > width:  x2 = width

    for x in range(x1, x2):
        y1 = dyb * (x - xs) / dx + b1
        y2 = dyt * (x - xs) / dx + t1
        # Clip y
        if y1 < 0:  y1 = 0
        if y2 < 0:  y2 = 0
        if y1 > height:  y1 = height
        if y2 > height:  y2 = height
        # if S[s].surface == 1:
        #     S[s].surf[x] = y1
        #     continue
        # if S[s].surface == 2:
        #     S[s].surf[x] = y2
        #     continue
        # if S[s].surface == -1:
        #     framebuffer[x, int(S[s].surf[x]):int(y1)] = S[s].color1
        # if S[s].surface == -2:
        #     framebuffer[x, int(y2):int(S[s].surf[x])] = S[s].color2

        # Front walls
        if frontBack == 0:
            if S[s].surface == 1:
                S[s].surf[x] = y1
            if S[s].surface == 2:
                S[s].surf[x] = y2
            framebuffer[x, int(y1):int(y2)] = color
        # Back walls
        if frontBack == 1:
            if S[s].surface == 1:
                y2 = S[s].surf[x]
                framebuffer[x, int(y1):int(y2)] = S[s].color1
            if S[s].surface == 2:
                y1 = S[s].surf[x]
                framebuffer[x, int(y1):int(y2)] = S[s].color2


    

def draw3D(player_x, player_y, player_z, player_a, player_l):
    global framebuffer
    framebuffer = numpy.zeros((width, height, 3), numpy.uint8)
    world_x = [0, 0, 0, 0]
    world_y = [0, 0, 0, 0]
    world_z = [0, 0, 0, 0]
    CS = math.cos(math.radians(player_a))
    SN = math.sin(math.radians(player_a))
    
    # Sort sectors by distance
    for s in range(map.SECTOR_NUM):
        for w in range(map.SECTOR_NUM-s-1):
            if S[w].d < S[w + 1].d:
                st = S[w]
                S[w] = S[w + 1]
                S[w + 1] = st
    
    for s in range(map.SECTOR_NUM):
        if player_z < S[s].z1:
            S[s].surface = 1
            cycles = 2
            for i in range(width):
                S[s].surf[i] = height
        elif player_z > S[s].z2 + S[s].z1:
            S[s].surface = 2
            cycles = 2
            for i in range(width):
                S[s].surf[i] = 0
        else:
            S[s].surface = 0
            cycles = 1

        for frontBack in range(cycles):
            S[s].d = 0
            for w in range (S[s].wall_start, S[s].wall_end):
                # Point world location (no tilting)
                x1 = W[w].x1 - player_x; y1 = W[w].y1 - player_y
                x2 = W[w].x2 - player_x; y2 = W[w].y2 - player_y
                if frontBack == 1:
                    swp = x2
                    x2 = x1
                    x1 = swp
                    swp = y2
                    y2 = y1
                    y1 = swp
                # World X position
                world_x[0] = int(x1 * CS - y1 * SN)
                world_x[1] = int(x2 * CS - y2 * SN)
                world_x[2] = int(world_x[0])
                world_x[3] = int(world_x[1])
                # World Y position
                world_y[0] = int(y1 * CS + x1 * SN)
                world_y[1] = int(y2 * CS + x2 * SN)
                world_y[2] = int(world_y[0])
                world_y[3] = int(world_y[1])
                S[s].d = S[s].d + distance(0, 0, (world_x[0] + world_x[1])/2, (world_y[0] + world_y[1])/2)
                # World Z position
                world_z[0] = int(S[s].z1 - player_z + ((player_l - 180) * world_y[0] / 64))
                world_z[1] = int(S[s].z1 - player_z + ((player_l - 180) * world_y[1] / 64))
                world_z[2] = int(world_z[0] + S[s].z2)
                world_z[3] = int(world_z[1] + S[s].z2)
                # Skip drawing behind the player
                if world_y[0] < 1 and world_y[1] < 1: continue
                # Point 1 behind the player
                if world_y[0] < 1:
                    world_x[0], world_y[0], world_z[0] = clipBehindPlayer(world_x[0], world_y[0], world_z[0], world_x[1], world_y[1], world_z[1])
                    world_x[2], world_y[2], world_z[2] = clipBehindPlayer(world_x[2], world_y[2], world_z[2], world_x[3], world_y[3], world_z[3])
                if world_y[1] < 1:
                    world_x[1], world_y[1], world_z[1] = clipBehindPlayer(world_x[1], world_y[1], world_z[1], world_x[0], world_y[0], world_z[0])
                    world_x[3], world_y[3], world_z[3] = clipBehindPlayer(world_x[3], world_y[3], world_z[3], world_x[2], world_y[2], world_z[2])
                
                
                # Screen x, y, z
                world_x[0] = int(world_x[0] * focal_lenght / world_y[0] + width / 2); world_y[0] = int(world_z[0] * focal_lenght / world_y[0] + height / 2)
                world_x[1] = int(world_x[1] * focal_lenght / world_y[1] + width / 2); world_y[1] = int(world_z[1] * focal_lenght / world_y[1] + height / 2)
                world_x[2] = int(world_x[2] * focal_lenght / world_y[2] + width / 2); world_y[2] = int(world_z[2] * focal_lenght / world_y[2] + height / 2)
                world_x[3] = int(world_x[3] * focal_lenght / world_y[3] + width / 2); world_y[3] = int(world_z[3] * focal_lenght / world_y[3] + height / 2)
                
                # Draw points
                drawWall(world_x[0], world_x[1], world_y[0], world_y[1], world_y[2], world_y[3], W[w].color, s, w, frontBack)
            S[s].d = S[s].d / (S[s].wall_end - S[s].wall_start)
    return framebuffer
