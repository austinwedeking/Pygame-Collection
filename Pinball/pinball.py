import pygame
from pygame.constants import *
from pygame.math import Vector2
from physics_objects import Circle, Polygon, Wall
from forces import *
import contact
import math
from threading import Event

pygame.init()
pygame.font.init()

# Fonts
font = pygame.font.SysFont("comicsansms", 40)
game_over_font = pygame.font.SysFont("comicsansms", 100)

# Colors
light_red = (255,127,127)
red = (255,0,0)
light_blue = (1,101,252)
muted_blue = (62,67,111)
neon_green = (57,255,20)
white = (255,255,255)
gray = (128,128,128)

# Variables
score = 0
balls_left = 3
bonuses_hit = 0
G = 10000
screen_width, screen_height = pygame.display.get_desktop_sizes()[0]
center = Vector2(screen_width/2, screen_height/2)
diagonal = math.sqrt(screen_width**2 + screen_height**2)
frame_counter = 0


# Create window
window = pygame.display.set_mode(flags=FULLSCREEN)

# Clock object for timing
clock = pygame.time.Clock()
fps = 120
dt = 1/fps

# OBJECTS
obj = []
obj_walls = []
obj_bumpers = []
obj_bonus = []
obj_paddles = []
gravity_obj = []

# walls
wall1 = Polygon(mass=math.inf, local_points=[[432,0], [480,0], [480,1080], [432,1080]], pos=[0,0], color=light_red)
wall2 = Polygon(mass=math.inf, local_points=[[480,0], [1440,0], [1440,36], [480,36]], pos=[0,0], color=light_red)
wall3 = Polygon(mass=math.inf, local_points=[[1440,0], [1488,0], [1488,1080], [1440,1080]], pos=[0,0], color=light_red)
#wall4 = Polygon(mass=math.inf, local_points=[[1392,1044], [1440,1044], [1440,1080], [1392,1080]], pos=[0,0], color=light_red)
wall5 = Polygon(mass=math.inf, local_points=[[1344,288], [1392,252], [1392,1080], [1344,1080]], pos=[0,0], color=light_red)
wall6 = Polygon(mass=math.inf, local_points=[[1008,1080], [1008,1008], [1344,936], [1344,1080]], pos=[0,0], color=light_red)
wall7 = Polygon(mass=math.inf, local_points=reversed([[1440,180], [1344,36], [1440,36]]), pos=[0,0], color=light_red)
wall8 = Polygon(mass=math.inf, local_points=reversed([[576,36], [480,180], [480,36]]), pos=[0,0], color=light_red)
wall9 = Polygon(mass=math.inf, local_points=[[480,936], [912,1008], [912,1080], [480,1080]], pos=[0,0], color=light_red)
wall10 = Polygon(mass=math.inf, local_points=[[816,36], [1104,36], [1056,72], [864,72]], pos=[0,0], color=light_red)
wall11 = Polygon(mass=math.inf, local_points=[[576,684], [624,720], [624,792], [576,828]], pos=[0,0], color=light_red)
wall12 = Polygon(mass=math.inf, local_points=[[576,828], [624,792], [768,828], [768,864], [720,864]], pos=[0,0], color=light_red)
wall13 = Polygon(mass=math.inf, local_points=[[1248,720], [1296,684], [1296,828], [1248,792]], pos=[0,0], color=light_red)
wall14 = Polygon(mass=math.inf, local_points=[[1248,792], [1296,828], [1200,864], [1152,864], [1152,828]], pos=[0,0], color=light_red)
wall15 = Polygon(mass=math.inf, local_points=[[672,324], [720,360], [720,432], [672,396]], pos=[0,0], color=light_red)
wall16 = Polygon(mass=math.inf, local_points=[[816,504], [816,540], [768,576], [768,540]], pos=[0,0], color=light_red)
wall17 = Polygon(mass=math.inf, local_points=[[1104,504], [1104,540], [1152,576], [1152,540]], pos=[0,0], color=light_red)

obj_walls = [wall1] + [wall2] + [wall3] + [wall5] + [wall6] + [wall7] + [wall8] + [wall9] + [wall10] + [wall11] + [wall12] + [wall13] + [wall14] + [wall15] + [wall16] + [wall17]

# bumpers
bumper1 = Polygon(mass=math.inf, local_points=[[672,36], [576,36], [528,108]], pos=[0,0], color=muted_blue)
bumper2 = Polygon(mass=math.inf, local_points=reversed([[1248,36], [1344,36], [1392,108]]), pos=[0,0], color=muted_blue)
bumper3 = Polygon(mass=math.inf, local_points=reversed([[576,252], [672,288], [720,360]]), pos=[0,0], color=muted_blue)
bumper4 = Polygon(mass=math.inf, local_points=[[1344,288], [1248,360], [1344,432]], pos=[0,0], color=muted_blue)
bumper5 = Polygon(mass=math.inf, local_points=[[480,468], [528,504], [528,576], [480,612]], pos=[0,0], color=muted_blue)
bumper6 = Circle(mass=math.inf, pos=[576,396], radius=20, color=light_blue, width=12)
bumper7 = Circle(mass=math.inf, pos=[840,234], radius=20, color=light_blue, width=12)
bumper8 = Circle(mass=math.inf, pos=[1080,234], radius=20, color=light_blue, width=12)
bumper9 = Circle(mass=math.inf, pos=[888,414], radius=20, color=light_blue, width=12)
bumper10 = Circle(mass=math.inf, pos=[1032,414], radius=20, color=light_blue, width=12)
bumper11 = Circle(mass=math.inf, pos=[744,558], radius=20, color=light_blue, width=12)
bumper12 = Circle(mass=math.inf, pos=[1176,558], radius=20, color=light_blue, width=12)

obj_bumpers = [bumper1] + [bumper2] + [bumper3] + [bumper4] + [bumper5] + [bumper6] + [bumper7] + [bumper8] + [bumper9] + [bumper10] + [bumper11] + [bumper12]

# bonus zones
bonus_zone1 = Polygon(mass=math.inf, local_points=[[960,108], [1008,144], [960,180], [912,144]], pos=[0,0], color=neon_green, width=2)
bonus_zone2 = Polygon(mass=math.inf, local_points=[[624,324], [672,360], [624,396], [576,360]], pos=[0,0], color=neon_green, width=2)
bonus_zone3 = Polygon(mass=math.inf, local_points=[[1248,396], [1296,432], [1248,468], [1200,432]], pos=[0,0], color=neon_green, width=2)

obj_bonus = [bonus_zone1] + [bonus_zone2] + [bonus_zone3]

# paddles
paddle_min_angle = 0
paddle_max_angle = 0.785
left_paddle = Polygon(mass=1000, local_points=reversed([[0,0], [144,36], [0,36]]), pos=[768,828], color=white, avel=0, freeze_position=True) # [768,828], [912,864], [768, 864]
right_paddle = Polygon(mass=1000, local_points=[[0,0], [-144,36], [0,36]], pos=[1152,828], color=white, avel=0, freeze_position=True) # [1152,828], [1008,864], [1152,828]

obj_paddles = [left_paddle] + [right_paddle]

# plunger
plunger_min_height = 864
plunger_max_height = 684
plunger = Polygon(mass=math.inf, local_points=reversed([[-20,-20], [20,-20], [20,500], [-20,500]]), pos=[1416,684], color=red)

# pinball
pinball = Circle(pos=[1416, 648], radius=18, color=white, mass=1)
pinball2 = Circle(pos=[384, 140], radius=18, color=white, mass=1)
pinball3 = Circle(pos=[336, 140], radius=18, color=white, mass=1)
gravity_obj.append(pinball)

# add all objects to one list
obj = obj_walls + obj_bumpers + obj_bonus + obj_paddles + [plunger] + [pinball] + [pinball2] + [pinball3]

# FORCES
gravity = Gravity(objects_list=gravity_obj, acc=Vector2(0,G * math.sin(math.radians(6.5))))

# Game loop
pinball2_removed = False
pinball3_removed = False
running = True
while running:
    pygame.display.update()
    clock.tick(fps)
    window.fill((0,0,0))

    # EVENTS
    while event := pygame.event.poll():
        if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False

    # KEY STATE
    key = pygame.key.get_pressed()

    # Plunger control
    if key[K_DOWN]:
        plunger.vel = Vector2(0, 200)
    else:
        plunger.vel += Vector2(0, -5000) * dt

    # Paddle controls
    if key[K_LSHIFT]:
        left_paddle.avel -= 0.75
    else:
        left_paddle.avel += 0.75

    if key[K_RSHIFT]:
        right_paddle.avel += 0.75
    else:
        right_paddle.avel -= 0.75

    # PHYSICS
    # Add forces
    gravity.apply()
    
    # Update particles
    for o in obj:
        o.update(dt)
    
    # Plunger limits
    if plunger.pos.y < plunger_max_height:
        plunger.pos.y = plunger_max_height
        plunger.vel.y = 0
    if plunger.pos.y > plunger_min_height:
        plunger.pos.y = plunger_min_height
        plunger.vel.y = 0
    
    # Paddle limits
    if left_paddle.angle < -paddle_max_angle:
        left_paddle.angle = -paddle_max_angle
        left_paddle.avel = 0
    if left_paddle.angle > paddle_min_angle:
        left_paddle.angle = paddle_min_angle
        left_paddle.avel = 0
    
    if right_paddle.angle > paddle_max_angle:
        right_paddle.angle = paddle_max_angle
        right_paddle.avel = 0
    if right_paddle.angle < paddle_min_angle:
        right_paddle.angle = paddle_min_angle
        right_paddle.avel = 0
    
    for p in obj_paddles:
        p.update(0)

    # Clear force from all particles
    for o in obj:
        o.clear_force()
    
    # Checking if pinball has fallen out of the game
    for o in obj:
        if (o.pos - center).magnitude() > diagonal + pinball.radius:
            balls_left -= 1
            if balls_left > 0:
                o.pos = [1416, 612]
    
    # updating balls left
    if balls_left == 2 and not pinball2_removed:
        obj.remove(pinball2)
        pinball2_removed = True
    
    if balls_left == 1 and not pinball3_removed:
        obj.remove(pinball3)
        pinball3_removed = True

    # CONTACTS
    c = contact.generate(pinball, plunger, resolve=True, restitution=0.1)

    for w in obj_walls:
        c = contact.generate(pinball, w, resolve=True, restitution=0.25)

    for p in obj_paddles:
        c = contact.generate(pinball, p, resolve=True, restitution=0.25)

    for b in obj_bumpers:
        c = contact.generate(pinball, b, resolve=True, rebound=750)
        if c.overlap > 0 and type(b) == Circle:
            score += 10

    for b in obj_bonus:
        c = contact.generate(pinball, b, resolve=False)
        if c.overlap > 0 and b.color == neon_green:
            b.color = gray
            score += 50
            bonuses_hit += 1
    
    # resetting bonus zones
    if bonuses_hit == 3:
        score += 100
        bonuses_hit = 0
        frame_counter = 240
    
    if frame_counter > 0:
        frame_counter -= 1

    if frame_counter == 1:
        for b in obj_bonus:
            b.color = neon_green


    # GRAPHICS
    ## Clear window
    window.fill((0,0,0))

    ## Draw objects
    for o in obj:
        o.draw(window)
    
    ## Draw Text
    text_surface = font.render(f"Score: {score}", True, white)
    window.blit(text_surface, (96,36))

    text_surface = font.render("Balls Left:", True, white)
    window.blit(text_surface, (96,108))

    if balls_left < 1:
        text_surface = game_over_font.render("GAME OVER", True, red)
        x = window.get_width() / 2 - text_surface.get_width() / 2
        y = window.get_height() / 2 - text_surface.get_width() / 2
        window.blit(text_surface, (x, y))