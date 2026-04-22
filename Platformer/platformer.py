import pygame
from pygame.math import Vector2
from pygame.locals import *
from physics_objects import Circle, Wall, Polygon
import contact
from forces import Gravity
import itertools
import math

# initialize pygame and open window
pygame.init()
width, height = 800, 600
window = pygame.display.set_mode([width, height])
font = pygame.font.SysFont("comicsansms", 30)
big_font = pygame.font.SysFont("comicsansms", 80)

# set timing stuff
fps = 60
dt = 1/fps
clock = pygame.time.Clock()

# colors
light_red = (255,127,127)
red = (255,0,0)
light_blue = (1,101,252)
neon_green = (57,255,20)
white = (255,255,255)
yellow = (255,244,79)
black = (0,0,0)
gray = (128,128,128)
sky_blue = (135,206,235)

# set objects
obj = []
obj_platforms = []
obj_platforms_normal = []
obj_platforms_bouncy = []
obj_platforms_reduced_friction = []
obj_death_zones = []
obj_checkpoints = []

# platforms
ground = Polygon(mass=math.inf, local_points=[[0,560], [800,560], [800,600], [0,600]], pos=[0,0], color=gray)
ground2 = Polygon(mass=math.inf, local_points=[[40,380], [560,380], [560,400], [40,400]], pos=[0,0], color=gray)
ground3 = Polygon(mass=math.inf, local_points=[[160,200], [760,200], [760,220], [160,220]], pos=[0,0], color=gray)
left_wall = Polygon(mass=math.inf, local_points=[[0,40], [40,40], [40,560], [0,560]], pos=[0,0], color=gray)
right_wall = Polygon(mass=math.inf, local_points=[[760,40], [800,40], [800,560], [760,560]], pos=[0,0], color=gray)
ceiling = Polygon(mass=math.inf, local_points=[[0,0], [800,0], [800,40], [0,40]], pos=[0,0], color=gray)

platform1 = Polygon(mass=math.inf, local_points=reversed([[200,560], [360,480], [360,560]]), pos=[0,0], color=gray)
platform2 = Polygon(mass=math.inf, local_points=[[480,220], [500,220], [500,320], [480,320]], pos=[0,0], color=gray)
platform3 = Polygon(mass=math.inf, local_points=[[120,360], [280,360], [280,380], [120,380]], pos=[0,0], color=gray)
platform4 = Polygon(mass=math.inf, local_points=[[40,340], [120,340], [120,380], [40,380]], pos=[0,0], color=gray)
platform5 = Polygon(mass=math.inf, local_points=[[160,280], [220,280], [220,300], [160,300]], pos=[0,0], color=gray)
platform6 = Polygon(mass=math.inf, local_points=[[220,200], [240,200], [240,300], [220,300]], pos=[0,0], color=gray)
platform7 = Polygon(mass=math.inf, local_points=reversed([[120,340], [160,360], [120,360]]), pos=[0,0], color=gray)
platform8 = Polygon(mass=math.inf, local_points=[[260,160], [280,160], [280,200], [260,200]], pos=[0,0], color=gray)
platform9 = Polygon(mass=math.inf, local_points=[[240,520], [400,520], [400,560], [240,560]], pos=[0,0], color=gray)
platform10 = Polygon(mass=math.inf, local_points=[[600,120], [640,120], [640,140], [600,140]], pos=[0,0], color=gray)

obj_platforms_normal += [ground] + [ground2] + [ground3] + [left_wall] + [right_wall] + [ceiling]
obj_platforms_normal += [platform2] + [platform3] + [platform4] + [platform5] + [platform6] + [platform7] + [platform8] + [platform9] + [platform10]

# rebound platforms
r_platform1 = Polygon(mass=math.inf, local_points=reversed([[680,560], [760,520], [760,560]]), pos=[0,0], color=light_red)
r_platform2 = Polygon(mass=math.inf, local_points=[[40,160], [60,160], [60,340], [40,340]], pos=[0,0], color=light_red)
r_platform3 = Polygon(mass=math.inf, local_points=reversed([[480,160], [500,180], [480,180]]), pos=[0,0], color=light_red)
r_platform4 = Polygon(mass=math.inf, local_points=reversed([[740,180], [760,160], [760,180]]), pos=[0,0], color=light_red)
r_platform5 = Polygon(mass=math.inf, local_points=reversed([[460,180], [480,160], [480,180]]), pos=[0,0], color=light_red)
r_platform6 = Polygon(mass=math.inf, local_points=[[480,40], [760,40], [760,60], [480,60]], pos=[0,0], color=light_red)

obj_platforms_bouncy += [r_platform1] + [r_platform2] + [r_platform3] + [r_platform4] + [r_platform5] + [r_platform6]

# reduced friction platforms
rf_platform1 = Polygon(mass=math.inf, local_points=[[280,360], [400,360], [440,380], [280,380]], pos=[0,0], color=sky_blue)
rf_platform2 = Polygon(mass=math.inf, local_points=reversed([[400,520], [560,560], [400,560]]), pos=[0,0], color=sky_blue)
rf_platform3 = Polygon(mass=math.inf, local_points=[[280,180], [760,180], [760,200], [280,200]], pos=[0,0], color=sky_blue)

obj_platforms_reduced_friction += [rf_platform1] + [rf_platform2] + [rf_platform3]

# add platforms to one list
obj_platforms += obj_platforms_bouncy + obj_platforms_reduced_friction + obj_platforms_normal

# death zones
death_zone1 = Polygon(mass=math.inf, local_points=[[500,220], [760,220], [760,240], [500,240]], pos=[0,0], color=red)
death_zone2 = Polygon(mass=math.inf, local_points=[[280,340], [320,340], [320,360], [280,360]], pos=[0,0], color=red)
death_zone3 = Polygon(mass=math.inf, local_points=[[340,500], [380,500], [380,520], [340,520]], pos=[0,0], color=red)
death_zone4 = Polygon(mass=math.inf, local_points=[[600,540], [640,540], [640,560], [600,560]], pos=[0,0], color=red)
death_zone5 = Polygon(mass=math.inf, local_points=[[40,40], [60,40], [60,160], [40,160]], pos=[0,0], color=red)
death_zone6 = Polygon(mass=math.inf, local_points=[[280,160], [300,160], [300,180], [280,180]], pos=[0,0], color=red)
death_zone7 = Polygon(mass=math.inf, local_points=[[260,40], [480,40], [480,60], [260,60]], pos=[0,0], color=red)

obj_death_zones += [death_zone1] + [death_zone2] + [death_zone3] + [death_zone4] + [death_zone5] + [death_zone6] + [death_zone7]

# checkpoints
checkpoint1 = Polygon(mass=math.inf, local_points=[[0,0], [40,0], [40,40], [0,40]], pos=[80,520], color=yellow)
checkpoint2 = Polygon(mass=math.inf, local_points=[[0,0], [40,0], [40,40], [0,40]], pos=[470,340], color=yellow)
checkpoint3 = Polygon(mass=math.inf, local_points=[[0,0], [40,0], [40,40], [0,40]], pos=[200,160], color=yellow)

obj_checkpoints += [checkpoint1] + [checkpoint2] + [checkpoint3]

# goal
goal = Polygon(mass=math.inf, local_points=[[0,0], [40,0], [40,40], [0,40]], pos=[600,80], color=neon_green)

# player
player = Circle(pos=(100,520), vel=(0,0), radius=16, mass=1, color=light_blue, width=0)
gravity_objects = [player]

# add all objects on one list
obj += obj_death_zones + obj_checkpoints + obj_platforms + [goal]

# forces
G = 980
gravity = Gravity(acc=[0,G], objects_list=gravity_objects)

# variables
in_air = False
jump_time = 0
jump_max = 0.5
normal_friction = 0.5
low_friction = 0.05
current_save = Vector2(obj_checkpoints[0].pos.x + 20, obj_checkpoints[0].pos.y + 20)
game_over = False
win = False
lives = 3

# game loop
running = True
while running:
    # update the display
    pygame.display.update()
    # delay for correct timing
    clock.tick(fps)
    # clear the screen
    window.fill([255,255,255])

    # EVENTS
    while event := pygame.event.poll():
        if event.type == pygame.QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False

    # CONTROLS
    key = pygame.key.get_pressed()

    # checkpoints
    if key[K_1]:
        jump_time = 0
        player.avel = 0
        player.vel = Vector2(0,0)
        player.pos = Vector2(obj_checkpoints[0].pos.x + 20, obj_checkpoints[0].pos.y + 20)

    if key[K_2]:
        jump_time = 0
        player.avel = 0
        player.vel = Vector2(0,0)
        player.pos = Vector2(obj_checkpoints[1].pos.x + 20, obj_checkpoints[1].pos.y + 20)

    if key[K_3]:
        jump_time = 0
        player.avel = 0
        player.vel = Vector2(0,0)
        player.pos = Vector2(obj_checkpoints[2].pos.x + 20, obj_checkpoints[2].pos.y + 20)

    # movement
    if key[K_LEFT] and not key[K_RIGHT]:
        player.avel = -15
    elif key[K_RIGHT] and not key[K_LEFT]:
        player.avel = 15
    else:
        player.avel = 0

    # PHYSICS
    # forces
    gravity.apply()
    
    # update objects
    for o in obj:
        o.update(dt)
    
    if not game_over and not win:
        player.update(dt)

    # clear force
    for o in obj:
        o.clear_force()
    
    if not game_over and not win:
        player.clear_force()

    # jumping
    in_air = True
    for p in obj_platforms:
        c = contact.generate(player, p, resolve=False)
        if c.overlap >= 0:
            in_air = False
    
    if key[K_SPACE]:
        jump_time += dt
        jump_time = min(jump_time, jump_max)
        if in_air:
            jump_time = jump_max
    elif in_air:
        jump_time = 0

    # COLLISIONS
    # platforms
    for p in obj_platforms_normal:
        if in_air or not key[K_SPACE]:
            c = contact.generate(player, p, resolve=True, restitution=0.25, rebound = math.sqrt(2 * G * (jump_time / jump_max)) * 8, friction=normal_friction)
        else:
            c = contact.generate(player, p, resolve=True, restitution=0.25, friction=normal_friction)
    
    for p in obj_platforms_bouncy:
        c = contact.generate(player, p, resolve=True, rebound = 750, friction=normal_friction)
    
    for p in obj_platforms_reduced_friction:
        if in_air or not key[K_SPACE]:
            c = contact.generate(player, p, resolve=True, restitution=0.25, rebound = math.sqrt(2 * G * (jump_time / jump_max)) * 8, friction=low_friction)
        else:
            c = contact.generate(player, p, resolve=True, restitution=0.25, friction=low_friction)
    
    # death zones
    for d in obj_death_zones:
        c = contact.generate(player, d, resolve=False)
        if c.overlap > 0:
            if lives > 1:
                lives -= 1
                jump_time = 0
                player.avel = 0
                player.vel = Vector2(0,0)
                player.pos = current_save
            else:
                lives -= 1
                game_over = True
    
    # checkpoints
    for cp in obj_checkpoints:
        c = contact.generate(player, cp, resolve=False)
        if c.overlap > 0:
            current_save = Vector2(cp.pos.x + 20, cp.pos.y + 20)

    # goal
    c = contact.generate(player, goal, resolve=False)
    if c.overlap > 0 and not game_over:
        win = True

    # GRAPHICS
    # draw objects
    for o in obj:
        o.draw(window)
    
    if not game_over and not win:
        player.draw(window)

    # draw text
    if not game_over and not win:
        text_surface = font.render(f"Lives: {lives}", True, black)
        window.blit(text_surface, (window.get_width() / 2 - text_surface.get_width() / 2, window.get_height() - text_surface.get_height()))

    if game_over:
        text_surface = big_font.render(f"You Lose!", True, black)
        window.blit(text_surface, (window.get_width() / 2 - text_surface.get_width() / 2, window.get_height() / 2 - text_surface.get_height() / 2))

    if win:
        text_surface = big_font.render(f"You Win!", True, black)
        window.blit(text_surface, (window.get_width() / 2 - text_surface.get_width() / 2, window.get_height() / 2 - text_surface.get_height() / 2))
