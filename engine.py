import math
import numpy as np
from numba import njit, types
from numba.typed import Dict, List
import pygame
from random import randint

aspect_ratio = 16 / 9
width = 1200
height = int(width / aspect_ratio)

# Camera
focal_lenght = 400
focal_lenght_old = focal_lenght
zoom = 3000

# Time
last_tick = 0
fps = 1
QUIT = False

# Global arrays for Numba compatibility
W_data = np.zeros((256, 15), dtype=np.float64)  # x1, y1, x2, y2, color_r, color_g, color_b, wall_texture, u, v, shade, wy1, wy2, wx1, wx2
S_data = np.zeros((128, 16), dtype=np.float64)  # wall_start, wall_end, d, color1_r, color1_g, color1_b, color2_r, color2_g, color2_b, z1, z2, surface_texture, surface_scale, sector_type, groupid, surface
S_surf = np.zeros((128, width), dtype=np.float64)
textures_data = np.zeros((64, 3), dtype=np.float64)  # texture_width, texture_height, texture_name placeholder

# Player position for Numba functions
plane_x = 0.0
plane_y_start = 0.0
plane_y = 0.0
plane_z = 0.0
_numba_warmed_up = False

@njit(cache=True)
def get_wall_width(wall_idx):
    """Get width of a wall"""
    x1, y1, x2, y2 = W_data[wall_idx, 0], W_data[wall_idx, 1], W_data[wall_idx, 2], W_data[wall_idx, 3]
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def warmup_numba_functions():
    """Pre-compile Numba functions to reduce first-run lag"""
    global _numba_warmed_up
    if _numba_warmed_up:
        return
        
    print("Warming up Numba functions...")
    
    # Create test arrays with real game dimensions
    test_W_data = np.copy(W_data)  # Use actual wall data
    test_S_data = np.copy(S_data)  # Use actual sector data
    test_S_surf = np.zeros((128, width), dtype=np.float64)
    test_framebuffer = np.zeros((width, height, 3), dtype=np.uint8)
    
    try:
        print("  Warming up basic functions...")
        import map
        
        # Basic function warmup
        collisions_numba(0, 0, 100, test_S_data, test_W_data, map.SECTOR_NUM)
        clip_behind_player_numba(1, 1, 1, 2, 2, 2)
        sector_distance_numba(0, 0, 0, test_S_data, test_W_data)
        
        print("  Warming up movement across full game range...")
        # Test movement across the entire playable range
        # Based on your bounds: plane_x: -450 to 750, plane_z: 50 to 200
        movement_ranges = [
            # dx values (left/right movement)
            (0, 0), (-50, 0), (-100, 0), (-200, 0), (-400, 0),  # Left movement
            (50, 0), (100, 0), (200, 0), (400, 0),              # Right movement
            # dz values (up/down movement) 
            (0, -25), (0, -50), (0, -75), (0, -100),           # Up movement
            (0, 25), (0, 50), (0, 75), (0, 100),               # Down movement
            # Combined movements
            (-100, -50), (100, 50), (-200, 25), (200, -25),    # Diagonal
        ]
        
        # Test at different starting positions across the game world
        test_positions = [
            (-400, 0, 60),    # Far left, low
            (0, 500, 125),    # Center
            (700, 1000, 190), # Far right, high
            (-200, 200, 75),  # Mid-left
            (500, 800, 150),  # Mid-right
        ]
        
        for show_player in [False, True]:  # Both menu and game modes
            for start_x, start_y, start_z in test_positions:
                for dx, dz in movement_ranges:
                    update_map_numba(start_x, start_y, start_z, 0, show_player, dx, dz, 
                                   test_W_data, test_S_data, map.SECTOR_NUM, map.GROUP_NUM)
        
        print("  Warming up 3D rendering across full view range...")
        # Test viewing angles and positions across full game range
        viewing_scenarios = []
        
        # Different positions across the map
        for x in [-400, -200, 0, 200, 400, 700]:
            for y in [0, 500, 1000, 2000]:
                for z in [60, 100, 125, 150, 190]:
                    # Different rotation angles
                    for angle in [0, 45, 90, -45, -90, 180]:
                        # Different look angles (up/down)
                        for look in [160, 170, 180, 190, 200]:
                            viewing_scenarios.append((x, y, z, angle, look))
        
        # Sample a subset to avoid taking too long
        import random
        sampled_scenarios = random.sample(viewing_scenarios, min(50, len(viewing_scenarios)))
        
        for show_player in [False, True]:
            for player_x, player_y, player_z, player_a, player_l in sampled_scenarios:
                draw3d_numba(player_x, player_y, player_z, player_a, player_l, show_player, 
                            test_framebuffer, test_W_data, test_S_data, test_S_surf, 
                            map.SECTOR_NUM, width, height, focal_lenght)
        
        print("  Warming up collision detection across full range...")
        # Test collisions at various positions
        for x in range(-450, 751, 100):  # Full x range
            for z in range(50, 201, 25):   # Full z range
                for y in [0, 500, 1000]:    # Different y positions
                    collisions_numba(x, y, z, test_S_data, test_W_data, map.SECTOR_NUM)
        
        print("  Warming up wall rendering...")
        draw_wall_numba(100, 200, 100, 150, 50, 100, 255, 255, 255, 0, 0, 0, 
                       test_framebuffer, test_S_data, test_S_surf, width, height)
        
    except Exception as e:
        print(f"  Warmup error: {e}")
    
    _numba_warmed_up = True
    print("Numba warmup complete!")

def ensure_numba_warmup():
    """Ensure Numba functions are warmed up before first use"""
    if not _numba_warmed_up:
        warmup_numba_functions()

def loadMap():
    global plane_x, plane_y_start, plane_y, plane_z, W_data, S_data, S_surf
    
    # Delay import to avoid circular dependencies
    try:
        import map
    except ImportError:
        print("Warning: map module not found, using default values")
        return
    
    plane_x = 37.5 + 112.5
    plane_y_start = 50
    plane_y = 50
    plane_z = 190
    
    # Load sectors data
    sectors_raw = map.loadSectors()
    walls_raw = map.loadWalls()
    
    v1 = 0
    v2 = 0
    
    for s in range(map.SECTOR_NUM):
        S_data[s, 0] = sectors_raw[v1 + 0]  # wall_start
        S_data[s, 1] = sectors_raw[v1 + 1]  # wall_end
        S_data[s, 2] = 0  # d (distance, calculated later)
        S_data[s, 3:6] = sectors_raw[v1 + 4]  # color1 (RGB)
        S_data[s, 6:9] = sectors_raw[v1 + 5]  # color2 (RGB)
        S_data[s, 9] = sectors_raw[v1 + 2]  # z1
        S_data[s, 10] = sectors_raw[v1 + 3] - sectors_raw[v1 + 2]  # z2
        S_data[s, 11] = 0  # surface_texture
        S_data[s, 12] = 0  # surface_scale
        S_data[s, 13] = sectors_raw[v1 + 6]  # sector_type
        S_data[s, 14] = sectors_raw[v1 + 7]  # groupid
        S_data[s, 15] = 0  # surface
        v1 += 8
        
        # Load walls for this sector
        for w in range(int(S_data[s, 0]), int(S_data[s, 1])):
            W_data[w, 0] = walls_raw[v2 + 0]  # x1
            W_data[w, 1] = walls_raw[v2 + 1]  # y1
            W_data[w, 2] = walls_raw[v2 + 2]  # x2
            W_data[w, 3] = walls_raw[v2 + 3]  # y2
            W_data[w, 4:7] = walls_raw[v2 + 4]  # color (RGB)
            v2 += 5
            
            # Store original positions
            W_data[w, 11] = W_data[w, 1]  # wy1
            W_data[w, 12] = W_data[w, 3]  # wy2
            W_data[w, 13] = W_data[w, 0]  # wx1
            W_data[w, 14] = W_data[w, 2]  # wx2
            W_data[w, 11] += 300  # wy1
            W_data[w, 12] += 300  # wy2
            
        # Adjust positions for certain sector types
        if S_data[s, 13] == 1 or S_data[s, 13] == 2:  # sector_type
            for w in range(int(S_data[s, 0]), int(S_data[s, 1])):
                W_data[w, 0] += 112.5  # x1
                W_data[w, 2] += 112.5  # x2

@njit(cache=True)
def player_movement_numba(plane_x_val, plane_z_val, fps_val):
    """Numba-optimized player movement - returns dx, dz"""
    # Note: This is a simplified version since we can't access pygame directly in njit
    # The actual input handling should be done outside and passed as parameters
    dx = 0.0
    dz = 0.0
    speed = 800.0 / fps_val
    
    # These would need to be passed as parameters from the main game loop
    # For now, returning default values
    return dx, dz

def playerMovement():
    """Non-numba wrapper for pygame input"""
    buttons = pygame.key.get_pressed()
    dx = 0
    dz = 0
    speed = 800 / fps
    
    global plane_z, plane_x
    if plane_z > 50:
        if buttons[pygame.K_UP]:
            dz += -speed
    if plane_z < 200:
        if buttons[pygame.K_DOWN]:
            dz += speed
    if plane_x < 750:
        if buttons[pygame.K_RIGHT]:
            dx += speed
    if plane_x > -450:
        if buttons[pygame.K_LEFT]:
            dx += -speed
    return dx, dz

def loadFps(fps2):
    global fps
    fps = fps2

@njit(cache=True)
def update_map_numba(player_x, player_y, player_z, player_a, show_player, dx, dz, W_data, S_data, sector_num, group_num):
    """Numba-optimized map update function"""
    
    CS = math.cos(math.radians(player_a))
    SN = math.sin(math.radians(player_a))
    
    # Random values array (simplified)
    r = np.zeros((group_num, 2))
    
    # Calculate plane_y within the function
    if show_player:
        plane_y_local = player_y + 300
    else:
        plane_y_local = -1000
    
    for s in range(sector_num):
        sector_type = int(S_data[s, 13])
        groupid = int(S_data[s, 14])
        wall_start = int(S_data[s, 0])
        wall_end = int(S_data[s, 1])
        
        if sector_type == 0:
            # Generate random values if not set
            if r[groupid, 0] == 0:
                r[groupid, 0] = np.random.randint(-700, 700)
                if plane_y_local < 50000:
                    r[groupid, 1] = np.random.randint(1000, 2500)
                else:
                    r[groupid, 1] = np.random.randint(2000, 4000)
            
            for w in range(wall_start, wall_end):
                if W_data[w, 1] < player_y - 100 or W_data[w, 3] < player_y - 100:
                    # Update all walls in the same group
                    for s1 in range(sector_num):
                        if int(S_data[s1, 14]) == groupid:
                            wall_start1 = int(S_data[s1, 0])
                            wall_end1 = int(S_data[s1, 1])
                            for walls in range(wall_start1, wall_end1):
                                W_data[walls, 1] += r[groupid, 1]  # y1
                                W_data[walls, 3] += r[groupid, 1]  # y2
                                W_data[walls, 0] = W_data[walls, 13] + r[groupid, 0]  # x1 = wx1 + offset
                                W_data[walls, 2] = W_data[walls, 14] + r[groupid, 0]  # x2 = wx2 + offset
        
        elif (sector_type == 1 or sector_type == 2) and show_player:
            for w in range(wall_start, wall_end):
                # World Y position
                W_data[w, 1] = player_y + W_data[w, 11]  # y1 = player_y + wy1
                W_data[w, 3] = player_y + W_data[w, 12]  # y2 = player_y + wy2
                W_data[w, 0] += dx  # x1
                W_data[w, 2] += dx  # x2
            S_data[s, 9] += dz  # z1
        
        elif sector_type == 3:
            for w in range(wall_start, wall_end):
                W_data[w, 1] = player_y + W_data[w, 11]  # y1
                W_data[w, 3] = player_y + W_data[w, 12]  # y2
        
        elif sector_type == 4:
            for w in range(wall_start, wall_end):
                W_data[w, 1] -= 50  # y1
                W_data[w, 3] -= 50  # y2
            
            if r[groupid, 0] == 0:
                r[groupid, 0] = np.random.randint(-700, 700)
                if plane_y_local < 50000:
                    r[groupid, 1] = np.random.randint(1000, 2500)
                else:
                    r[groupid, 1] = np.random.randint(2000, 4000)
            
            for w in range(wall_start, wall_end):
                if W_data[w, 1] < player_y - 100 or W_data[w, 3] < player_y - 100:
                    for s1 in range(sector_num):
                        if int(S_data[s1, 14]) == groupid:
                            wall_start1 = int(S_data[s1, 0])
                            wall_end1 = int(S_data[s1, 1])
                            for walls in range(wall_start1, wall_end1):
                                W_data[walls, 1] += r[groupid, 1]
                                W_data[walls, 3] += r[groupid, 1]
                                W_data[walls, 0] = W_data[walls, 13] + r[groupid, 0]
                                W_data[walls, 2] = W_data[walls, 14] + r[groupid, 0]
    
    return plane_y_local

def updateMap(player_x, player_y, player_z, player_a, showPlayer):
    global QUIT, plane_x, plane_y, plane_z
    
    try:
        import map
    except ImportError:
        return
    
    dx, dz = playerMovement()
    
    # Update global plane coordinates
    if showPlayer:
        plane_x += dx
        plane_z += dz
    
    plane_y = update_map_numba(player_x, player_y, player_z, player_a, showPlayer, dx, dz, W_data, S_data, map.SECTOR_NUM, map.GROUP_NUM)
    
    if showPlayer:
        if collisions(plane_x, plane_y, plane_z):
            QUIT = True
        if collisions(plane_x, plane_y - 70, plane_z):
            QUIT = True

def checkQuit():
    global QUIT
    if QUIT:
        QUIT = False
        return True
    return QUIT

@njit(cache=True)
def collisions_numba(x, y, z, S_data, W_data, sector_num):
    """Numba-optimized collision detection"""
    for s in range(sector_num):
        z1 = S_data[s, 9]
        z2 = S_data[s, 10]
        if z1 < z < z1 + z2:
            if collision2D_numba(x, y, s, S_data, W_data):
                return True
    return False

@njit(cache=True)
def collision2D_numba(x, y, sector_idx, S_data, W_data):
    """Numba-optimized 2D collision detection"""
    collision_counter = 0
    sector_type = int(S_data[sector_idx, 13])
    
    if sector_type == 0 or sector_type == 4:
        wall_start = int(S_data[sector_idx, 0])
        wall_end = int(S_data[sector_idx, 1])
        
        for w in range(wall_start, wall_end):
            x1 = W_data[w, 0]
            y1 = W_data[w, 1]
            x2 = W_data[w, 2]
            y2 = W_data[w, 3]
            
            # Ignore horizontal edges
            if y1 == y2:
                continue
            
            # Ray crosses edge if y is between y1 and y2
            if ((y1 > y) != (y2 > y)):
                x_intersect = (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1
                if x < x_intersect:
                    collision_counter += 1
        
        if collision_counter % 2 == 1:
            return True
    return False

def collisions(x, y, z):
    import map
    return collisions_numba(x, y, z, S_data, W_data, map.SECTOR_NUM)

@njit(cache=True)
def clip_behind_player_numba(x1, y1, z1, x2, y2, z2):
    """Numba-optimized clipping behind player"""
    da = y1
    db = y2
    d = da - db
    if d == 0:
        d = 1
    s = da / d
    x1 = x1 + s * (x2 - x1)
    y1 = y1 + s * (y2 - y1)
    if y1 <= 0.1:
        y1 = 1
    z1 = z1 + s * (z2 - z1)
    return x1, y1, z1

@njit(cache=True)
def draw_wall_numba(x1, x2, b1, b2, t1, t2, color_r, color_g, color_b, s, w, front_back, framebuffer, 
                   S_data, S_surf, width, height):
    """Numba-optimized wall drawing"""
    dyb = b2 - b1
    dyt = t2 - t1
    dx = x2 - x1
    if dx == 0:
        dx = 1
    xs = x1
    
    # Clip x
    if x1 < 0: x1 = 0
    if x2 < 0: x1 = 0
    if x1 > width: x1 = width
    if x2 > width: x2 = width

    surface = int(S_data[s, 15]) if len(S_data[s]) > 15 else 0
    
    for x in range(int(x1), int(x2)):
        if x >= width or x < 0:
            continue
            
        y1_val = dyb * (x - xs) / dx + b1
        y2_val = dyt * (x - xs) / dx + t1
        
        # Clip y
        if y1_val < 0: y1_val = 0
        if y2_val < 0: y2_val = 0
        if y1_val > height: y1_val = height
        if y2_val > height: y2_val = height

        # Front walls
        if front_back == 0:
            if surface == 1:
                S_surf[s, x] = y1_val
            if surface == 2:
                S_surf[s, x] = y2_val
            
            # Fill the wall
            for y in range(int(y1_val), int(y2_val)):
                if 0 <= y < height:
                    framebuffer[x, y, 0] = color_r
                    framebuffer[x, y, 1] = color_g
                    framebuffer[x, y, 2] = color_b
        
        # Back walls
        elif front_back == 1:
            if surface == 1:
                y2_val = S_surf[s, x]
                for y in range(int(y1_val), int(y2_val)):
                    if 0 <= y < height:
                        framebuffer[x, y, 0] = S_data[s, 3]  # color1_r
                        framebuffer[x, y, 1] = S_data[s, 4]  # color1_g
                        framebuffer[x, y, 2] = S_data[s, 5]  # color1_b
            if surface == 2:
                y1_val = S_surf[s, x]
                for y in range(int(y1_val), int(y2_val)):
                    if 0 <= y < height:
                        framebuffer[x, y, 0] = S_data[s, 6]  # color2_r
                        framebuffer[x, y, 1] = S_data[s, 7]  # color2_g
                        framebuffer[x, y, 2] = S_data[s, 8]  # color2_b

@njit(cache=True)
def sector_distance_numba(s, player_x, player_y, S_data, W_data):
    """Numba-optimized sector distance calculation"""
    x_sum, y_sum, count = 0.0, 0.0, 0
    wall_start = int(S_data[s, 0])
    wall_end = int(S_data[s, 1])
    
    for w in range(wall_start, wall_end):
        x_sum += W_data[w, 0] + W_data[w, 2]  # x1 + x2
        y_sum += W_data[w, 1] + W_data[w, 3]  # y1 + y2
        count += 2
    
    if count == 0:
        return 999999999.0
        
    cx, cy = x_sum / count, y_sum / count
    return (player_x - cx) ** 2 + (player_y - cy) ** 2

@njit(cache=True)
def draw3d_numba(player_x, player_y, player_z, player_a, player_l, show_player, framebuffer, 
                W_data, S_data, S_surf, sector_num, width, height, focal_length):
    """Main Numba-optimized 3D drawing function"""
    world_x = np.zeros(4)
    world_y = np.zeros(4)
    world_z = np.zeros(4)
    
    CS = math.cos(math.radians(player_a))
    SN = math.sin(math.radians(player_a))
    
    # Compute distances and sort sectors
    distances = np.zeros(sector_num)
    sector_indices = np.arange(sector_num)
    
    for s in range(sector_num):
        if S_data[s, 13] == 3:  # sector_type
            distances[s] = 999999999
        else:
            distances[s] = sector_distance_numba(s, player_x, player_y, S_data, W_data)
    
    # Sort sectors by distance (furthest first)
    for i in range(sector_num):
        for j in range(sector_num - 1):
            if distances[j] < distances[j + 1]:
                # Swap distances
                temp_dist = distances[j]
                distances[j] = distances[j + 1]
                distances[j + 1] = temp_dist
                # Swap indices
                temp_idx = sector_indices[j]
                sector_indices[j] = sector_indices[j + 1]
                sector_indices[j + 1] = temp_idx
    
    for s_idx in range(sector_num):
        s = sector_indices[s_idx]
        z1 = S_data[s, 9]
        z2 = S_data[s, 10]
        
        # Determine surface and cycles
        if player_z < z1:
            surface = 1
            cycles = 2
            for i in range(width):
                S_surf[s, i] = height
        elif player_z > z2 + z1:
            surface = 2
            cycles = 2
            for i in range(width):
                S_surf[s, i] = 0
        else:
            surface = 0
            cycles = 1
        
        # Store surface info (extend S_data if needed)
        if len(S_data[s]) > 15:
            S_data[s, 15] = surface
        
        wall_start = int(S_data[s, 0])
        wall_end = int(S_data[s, 1])
        
        for front_back in range(cycles):
            for w in range(wall_start, wall_end):
                # Point world location
                x1 = W_data[w, 0] - player_x
                y1 = W_data[w, 1] - player_y
                x2 = W_data[w, 2] - player_x
                y2 = W_data[w, 3] - player_y
                
                if front_back == 1:
                    x1, x2 = x2, x1
                    y1, y2 = y2, y1
                
                # World X position
                world_x[0] = x1 * CS - y1 * SN
                world_x[1] = x2 * CS - y2 * SN
                world_x[2] = world_x[0]
                world_x[3] = world_x[1]
                
                # World Y position
                world_y[0] = y1 * CS + x1 * SN
                world_y[1] = y2 * CS + x2 * SN
                world_y[2] = world_y[0]
                world_y[3] = world_y[1]
                
                # World Z position
                world_z[0] = z1 - player_z + ((player_l - 180) * world_y[0] / 64)
                world_z[1] = z1 - player_z + ((player_l - 180) * world_y[1] / 64)
                world_z[2] = world_z[0] + z2
                world_z[3] = world_z[1] + z2
                
                # Skip drawing behind the player
                if world_y[0] < 1 and world_y[1] < 1:
                    continue
                
                # Point 1 behind the player
                if world_y[0] < 1:
                    world_x[0], world_y[0], world_z[0] = clip_behind_player_numba(
                        world_x[0], world_y[0], world_z[0], world_x[1], world_y[1], world_z[1])
                    world_x[2], world_y[2], world_z[2] = clip_behind_player_numba(
                        world_x[2], world_y[2], world_z[2], world_x[3], world_y[3], world_z[3])
                
                if world_y[1] < 1:
                    world_x[1], world_y[1], world_z[1] = clip_behind_player_numba(
                        world_x[1], world_y[1], world_z[1], world_x[0], world_y[0], world_z[0])
                    world_x[3], world_y[3], world_z[3] = clip_behind_player_numba(
                        world_x[3], world_y[3], world_z[3], world_x[2], world_y[2], world_z[2])
                
                # Screen x, y projection
                world_x[0] = world_x[0] * focal_length / world_y[0] + width / 2
                world_y_screen_0 = world_z[0] * focal_length / world_y[0] + height / 2
                world_x[1] = world_x[1] * focal_length / world_y[1] + width / 2
                world_y_screen_1 = world_z[1] * focal_length / world_y[1] + height / 2
                world_x[2] = world_x[2] * focal_length / world_y[2] + width / 2
                world_y_screen_2 = world_z[2] * focal_length / world_y[2] + height / 2
                world_x[3] = world_x[3] * focal_length / world_y[3] + width / 2
                world_y_screen_3 = world_z[3] * focal_length / world_y[3] + height / 2
                
                # Draw points
                color_r, color_g, color_b = W_data[w, 4], W_data[w, 5], W_data[w, 6]
                draw_wall_numba(world_x[0], world_x[1], world_y_screen_0, world_y_screen_1, 
                              world_y_screen_2, world_y_screen_3, color_r, color_g, color_b, 
                              s, w, front_back, framebuffer, S_data, S_surf, width, height)
    
    return framebuffer

def ensure_initialization():
    """Ensure map is loaded and Numba is warmed up"""
    global W_data
    # Check if map data is loaded (simple check)
    if np.all(W_data == 0):
        print("Loading map data...")
        loadMap()
    ensure_numba_warmup()

def draw3D(player_x, player_y, player_z, player_a, player_l, showPlayer, framebuffer):
    """Main drawing function that calls the Numba-optimized version"""
    # Ensure everything is initialized
    ensure_initialization()
    
    try:
        import map
    except ImportError:
        print("Warning: map module not available")
        return framebuffer
    
    # Update map first (non-numba part handles pygame input)
    updateMap(player_x, player_y - (not showPlayer)*200, player_z, player_a, showPlayer)
    
    # Convert framebuffer to numpy array if it isn't already
    if hasattr(framebuffer, 'shape'):
        fb_array = framebuffer
    else:
        fb_array = pygame.surfarray.array3d(framebuffer)
    
    # Call the Numba-optimized function
    result = draw3d_numba(player_x, player_y, player_z, player_a, player_l, showPlayer, 
                         fb_array, W_data, S_data, S_surf, map.SECTOR_NUM, width, height, focal_lenght)
    
    return result

# Initialize the map when module is used (delayed)
# Note: loadMap() and warmup will be called when first function is used