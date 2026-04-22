import pygame
from pygame.locals import *
from pygame.math import Vector2, Vector3
import random
import math

from physics_objects import Circle, Wall, Polygon, UniformPolygon, UniformCircle
import itertools
import contact

# initialize pygame and open window
pygame.init()
width, height = 800, 600
window = pygame.display.set_mode([width, height])
font = pygame.font.SysFont("comicsansms", 30)
big_font = pygame.font.SysFont("comicsansms", 50)

# set timing stuff
fps = 60
dt = 1/fps
clock = pygame.time.Clock()

# variables
density = 0.25
level = 1
num_spawned = 0
score = 0
high_score = 0
lives = 3
life_location = Vector2(550, 525)
bomb_shot = False
bomb_background = False

shape_spawn = 5
time_to_spawn = 5
min_random_vel_y = 50

shooter_reload = 0.33
time_to_reload = 0.33

respawn_timer = 0
time_to_respawn = 3

explosion_timer = 0
time_to_explode = 1

score_thresholds = [5, 20, 50, 100]

# states
game_over = False
running = True
dead = False
paused = False
first_start = True

# colors
yellow = (255,244,79)
green = (159,218,64)
red = (255,0,0)
black = (0,0,0)
white = (255,255,255)

level_backgrounds = [(0,0,10), (20,0,20), (40,0,30), (60,0,40), (80,0,50)]

# Objects
obj_walls = []
obj_bullets = []
obj_shapes = []
obj_bombs = []

# Walls for ground and invisible boundaries: left, right, and top
ground_wall = Wall(point1=(800,500), point2=(0,500), color=green, width=10)
left_wall = Wall(point1=(-25,600), point2=(-25,0), color=red, width=10)
right_wall = Wall(point1=(825,0), point2=(825,600), color=red, width=10)
top_wall = Wall(point1=(0,-50), point2=(800,-50), color=red, width=10)

obj_walls = [ground_wall] + [left_wall] + [right_wall] + [top_wall]

# shooter
shooter = Polygon(local_points=[[25,0], [0,50], [50,50]], color=yellow, mass=1)
shooter.set(Vector2(400-25, 450))

# shapes
triangle_points = [[25,0], [0,50], [50,50]]
square_points = [[0,0], [50,0], [50,50], [0,50]]
rhombus_points = [[0,0], [50,25], [0,50], [-50,25]]
pentagon_points = [[25,0], [0,30], [-35,20], [-35,-20], [0,-30]]
hexagon_points = [[40,0], [20,34.64], [-20,34.64], [-40,0], [-20,-34.64], [20,-34.64]]

triangle_points.reverse()
square_points.reverse()
rhombus_points.reverse()
pentagon_points.reverse()
hexagon_points.reverse()

# bombs
explosion = Circle(radius=100, color=red)

# Functions
def spawn(level): # spawns a new shape
    loc_y = -25
    random_loc_x = random.randint(50, width-50)
    random_avel = random.randint(-5, 5)
    random_vel_y = random.randint(min_random_vel_y, 200)
    random_vel_x = random.randint(-25, 25)

    random_shape = random.randint(1, level)
    match random_shape:
        case 1:
            triangle = UniformPolygon(local_points=triangle_points, color=white, density=density, point_value=1, width=2)
            triangle.set(Vector2(random_loc_x, loc_y))
            triangle.avel = random_avel
            triangle.vel = Vector2(random_vel_x, random_vel_y)
            obj_shapes.append(triangle)
        case 2:
            square = UniformPolygon(local_points=square_points, color=white, density=density, point_value=2, width=2)
            square.set(Vector2(random_loc_x, loc_y))
            square.avel = random_avel
            square.vel = Vector2(random_vel_x, random_vel_y)
            obj_shapes.append(square)
        case 3:
            rhombus = UniformPolygon(local_points=rhombus_points, color=white, density=density, point_value=3, width=2)
            rhombus.set(Vector2(random_loc_x, loc_y))
            rhombus.avel = random_avel
            rhombus.vel = Vector2(random_vel_x, random_vel_y)
            obj_shapes.append(rhombus)
        case 4:
            pentagon = UniformPolygon(local_points=pentagon_points, color=white, density=density, point_value=4, width=2)
            pentagon.set(Vector2(random_loc_x, loc_y))
            pentagon.avel = random_avel
            pentagon.vel = Vector2(random_vel_x, random_vel_y)
            obj_shapes.append(pentagon)
        case 5:
            hexagon = UniformPolygon(local_points=hexagon_points, color=white, density=density, point_value=5, width=2)
            hexagon.set(Vector2(random_loc_x, loc_y))
            hexagon.avel = random_avel
            hexagon.vel = Vector2(random_vel_x, random_vel_y)
            obj_shapes.append(hexagon)

def spawn_bullet(): # spawns a bullet
    bullet = UniformCircle(color=yellow, density=density)
    obj_bullets.append(bullet)
    bullet.set(Vector2(shooter.pos.x + 25, shooter.pos.y - 25))

def spawn_bomb(): # spawns a bomb
    loc_y = -25
    random_loc_x = random.randint(50, width-50)
    random_vel_y = random.randint(50, 100)
    random_vel_x = random.randint(-25, 25)

    bomb = UniformCircle(color=red, density=2)
    bomb.set(Vector2(random_loc_x, loc_y))
    bomb.vel = Vector2(random_vel_x, random_vel_y)
    obj_bombs.append(bomb)

while running:
    # update the display
    pygame.display.update()
    clock.tick(fps)
    
    # game loop
    # EVENT loop
    while event := pygame.event.poll():
        # Quitting game
        if (event.type == pygame.QUIT 
            or (event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE)):
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            paused = not paused
        # Use USEREVENT to start a new shooter after a delay of 2 seconds

    if not paused:
        # PHYSICS
        # Key controls of shooter
        key = pygame.key.get_pressed()

        if not dead:
            if key[K_LEFT]:
                shooter.vel = Vector2(-400,0)
            elif key[K_RIGHT]:
                shooter.vel = Vector2(400,0)
            else:
                shooter.vel = Vector2(0,0)

            shooter_reload += dt
            if key[K_SPACE] and shooter_reload > time_to_reload:
                spawn_bullet()
                obj_bullets[-1].vel = Vector2(0, -400)
                shooter_reload = 0

        # spawn shapes
        shape_spawn += dt
        if shape_spawn > time_to_spawn:
            if num_spawned >= 10:
                spawn_bomb()
                num_spawned = 0
            else:
                spawn(level)
                num_spawned += 1
            shape_spawn = 0
        
        # update all objects
        shooter.update(dt)

        for o in obj_walls:
            o.update(dt)

        for b in obj_bullets:
            b.update(dt)
        
        for s in obj_shapes:
            s.update(dt)

        for b in obj_bombs:
            b.update(dt)

        if bomb_shot:
            explosion.update(dt)
        
        # keep shooter on screen
        if shooter.pos.x < -25:
            shooter.pos.x = -25
        if shooter.pos.x > width-25:
            shooter.pos.x = width-25

        # collisions between bullets and polygons and polygons with each other
        for b in obj_bullets:
            for s in obj_shapes:
                c = contact.generate(b, s, resolve=True, restitution=1)
        
        for s1 in obj_shapes:
            for s2 in obj_shapes:
                if s1 != s2:
                    c = contact.generate(s1, s2, resolve=True, restitution=1)

        # check bullets hitting ground or going off screen
        for b in obj_bullets:
            for w in obj_walls:
                c = contact.generate(b, w, resolve=False)
                if c.overlap > 0:
                    obj_bullets.remove(b)
                    break
        
        # check polygons hitting ground or going off screen or hitting shooter
        for s in obj_shapes:
            c = contact.generate(s, shooter, resolve=False)
            if c.overlap > 0: # player collision
                if lives > 1:
                    lives -= 1
                    dead = True
                else:
                    lives -= 1
                    game_over = True
                obj_shapes.remove(s)

            if s.pos.y >= 450: # ground wall
                if not dead:
                    score -= s.point_value
                obj_shapes.remove(s)
            
            if s.pos.y <= -50: # ceiling wall
                if not dead:
                    score += s.point_value
                    if score > high_score: # save high score
                        high_score = score
                obj_shapes.remove(s)
            
            if s.pos.x <= -50: # left wall
                obj_shapes.remove(s)

            if s.pos.x >= 850: # right wall
                obj_shapes.remove(s)
        
        # check bombs hitting ground or going off screen or hitting shooter
        for b in obj_bombs:
            c = contact.generate(b, shooter, resolve=False)
            if c.overlap > 0: # player collision
                if not dead:
                    if lives > 1:
                        lives -= 1
                        dead = True
                    else:
                        lives -= 1
                        game_over = True
                bomb_shot = True
                obj_bombs.remove(b)
            
            for w in obj_walls:
                c = contact.generate(b, w, resolve=False)
                if c.overlap > 0: # walls
                    if b.pos.y >= 450: # ground wall
                        if not dead:
                            if lives > 1:
                                lives -= 1
                                dead = True
                            else:
                                lives -= 1
                                game_over = True
                        bomb_shot = True
                    obj_bombs.remove(b)
                    break
            
            for b2 in obj_bullets:
                c = contact.generate(b2, b, resolve=False)
                if c.overlap > 0: # bullets
                    explosion.set(Vector2(b.pos))
                    bomb_shot = True
                    obj_bombs.remove(b)
                    obj_bullets.remove(b2)

            for s in obj_shapes: # shapes
                c = contact.generate(b, s, resolve=True, restitution=1)
                if bomb_shot:
                    c2 = contact.generate(explosion, s, resolve=False)
                    if c2.overlap > 0: # overlap explosion radius
                        score += s.point_value + level
                        if score > high_score: # save high score
                            high_score = score
                        obj_shapes.remove(s)
        
        # Stages and scoring
        if level < 5 and high_score >= score_thresholds[level - 1]:
            level += 1
            lives += 1
            time_to_spawn -= 0.75
            min_random_vel_y += 25

    # DRAW section
    # clear the screen
    if dead and bomb_shot:
        bomb_background = True

    if bomb_background:
        window.fill(red)
    else:
        window.fill(level_backgrounds[level - 1])

    # draw objects
    if not dead:
        shooter.draw(window)
    else: # player dead
        respawn_timer += dt
        if respawn_timer > time_to_respawn: # reset board
            dead = False
            obj_shapes = []
            obj_bullets = []
            obj_bombs = []
            bomb_background = False
            shooter.set(Vector2(400-25, 450))
            respawn_timer = 0

    for w in obj_walls:
        w.draw(window)

    for b in obj_bullets:
        b.draw(window)
    
    for s in obj_shapes:
        s.draw(window)

    for b in obj_bombs:
        b.draw(window)
    
    if bomb_shot:
        explosion.draw(window)
        explosion_timer += dt
        if explosion_timer > time_to_explode:
            bomb_shot = False
            explosion.set(Vector2(0,800))
            explosion_timer = 0
    
    # draw reserve shooters
    if lives <= 3:
        for l in range(lives):
            life = Polygon(local_points=shooter.local_points, color=yellow)
            life.set((life_location.x + (75 * l), life_location.y))
            life.draw(window)
    else:
        life = Polygon(local_points=shooter.local_points, color=yellow)
        life.set((life_location.x, life_location.y))
        life.draw(window)
        text_surface = font.render(f"x{lives}", True, white)
        window.blit(text_surface, (600, 525))
    
    # display running score in the corners
    text_surface = font.render(f"Score: {score}", True, white)
    window.blit(text_surface, (25, 525))

    # display respawn text
    if dead:
        text_surface = font.render(f"Respawning...", True, white)
        window.blit(text_surface, (window.get_width() / 2 - text_surface.get_width() / 2, window.get_height() / 2 - text_surface.get_width() / 2))

    # display game over
    if game_over:
        text_surface = big_font.render(f"GAME OVER", True, red)
        window.blit(text_surface, (window.get_width() / 2 - text_surface.get_width() / 2, window.get_height() / 2 - text_surface.get_width() / 2))
        text_surface = big_font.render(f"High Score: {high_score}", True, red)
        window.blit(text_surface, (window.get_width() / 2 - text_surface.get_width() / 2, window.get_height() / 2 - text_surface.get_width() / 2 + 100))
        paused = True