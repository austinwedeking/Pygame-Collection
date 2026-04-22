import pygame
from pygame.math import Vector2
from pygame.locals import *
from physics_objects import Circle, Wall, Polygon, UniformPolygon, UniformCircle
import contact
from forces import Gravity
import itertools
import math
import random

# initialize pygame and open window
pygame.init()
width, height = 1200,600
window = pygame.display.set_mode([width, height])
font = pygame.font.SysFont("comicsansms", 30)
big_font = pygame.font.SysFont("comicsansms", 50)

# set timing
fps = 60
dt = 1/fps
clock = pygame.time.Clock()

# colors
black = (0,0,0)
white = (255,255,255)
yellow = (255,244,79)
red = (255,0,0)
orange = (255,105,0)
gray = (128,128,128)
light_red = (255,127,127)
sky_blue = (135,206,235)

# OBJECTS
obj_walls = []
obj_bullets = []
obj_elec_barriers = []
obj_rockets = []
obj_laser_borders = []
obj_lasers = []
obj_coins = []

# walls
ground_wall = Wall(point1=(window.get_width(),500), point2=(0,500), color=gray, width=5)
top_wall = Wall(point1=(0,50), point2=(window.get_width(),50), color=gray, width=5)
top_polygon = UniformPolygon(local_points=([0, 0], [0, -top_wall.point1.y], [window.get_width(), -top_wall.point1.y], [window.get_width(), 0]), pos=[0, top_wall.point1.y], color=gray, normals_length=0, vel=[0, 0], density=0.1)
ground_polygon = UniformPolygon(local_points=([0, 0], [0, -(window.get_height() - ground_wall.point1.y)], [window.get_width(), -(window.get_height() - ground_wall.point1.y)], [window.get_width(), 0]), pos=[0, window.get_height()], color=gray, normals_length=0, vel=[0, 0], density=0.1)

obj_walls += [ground_wall] + [top_wall] + [top_polygon] + [ground_polygon]

# player
player = Circle(pos=(100,520), vel=(0,0), radius=16, mass=1, color=black, width=0) # mess with vel.x later
gravity_objects = [player]

# FORCES
G = 490
gravity = Gravity(acc=[0,G], objects_list=gravity_objects)

# VARIABLES
# misc
distFromTop = top_wall.point1.y
distFromBottom = window.get_height() - ground_wall.point1.y
pixelsPerMeter = player.radius*2
dying = False
dead = False
game_over = False

# background color
bg_color = sky_blue
color_timer = 0
time_to_change_color = 0.25

# velocity
currentVelocity = 200
increase_vel_rate = 0.1
vel_on_death = 0.0
max_vel = 800
max_vel_per_meter = max_vel / pixelsPerMeter

# bullets
bullet_timer = 0.05
time_to_spawn_bullet = 0.05

# elec barriers
electricTimer = 0
electricCounter = 0
barrier_spacing = 1000

# lasers
borderTimer = 0
laserBorderProcess = False
laserTimer = 0
laserProcess = False
toLaserCounter = -1
laserCounterStart = False

# rockets
rocket_counter = 0
rocket_active = False
rocket_delay = 0
rocket_coords = []

# coins
coins = 3
coin_timer = 0
time_to_spawn_coin = 15
coin_direction_timer = 0

# invincibility frames
revive_timer = 3
time_to_revive = 3

# game over
perm_death_timer = 0
time_to_death = 5

# distance
distanceObject = Circle(pos=(4000000000000, - 1000), vel=(-currentVelocity,0), radius=1, mass=1, color=black, width=0)
currPos = distanceObject.pos.x
prevPos = distanceObject.pos.x
distanceTraveled = 0

# Functions
def spawn_barrier(): # spawns a new shape
    #Increments barrier counter
    spawn_barrier.counter += 1

    #length of barrier between 100 -> half the playable area's height
    random_length = random.uniform(100, (window.get_height() - distFromTop - distFromBottom)/2)

    #If this is the 4th barrier spawned
    if spawn_barrier.counter >= 4:
        spawn_barrier.counter = 0
        rand_int = random.randint(0, 1)

        #50% chance to spawn on the top or bottom of screen
        if rand_int == 0:
            random_pos_y = window.get_height() - distFromBottom - (random_length/2)
        else:
            random_pos_y = random_length/2 + distFromTop

    #If not the 4th barrier, give an actual random position
    else:
        random_pos_y = random.uniform(random_length/2 + distFromTop, window.get_height() - (random_length/2) - distFromBottom)
    
    #1 in 5 chance to rotate
    rotateRand = random.randint(0, 5)
    if rotateRand == 0:
        angleVel = random.random() - 0.5
    else:
        angleVel = 0

    #Spawn barrier
    electricOffsets = [[0, -random_length/2], [50, -random_length/2], [50, random_length/2], [0, random_length/2]]
    obj_elec_barriers.append(UniformPolygon(local_points=(electricOffsets), pos=[window.get_width() + 50 + random_length/2, random_pos_y], color=orange, avel=angleVel, normals_length=0, vel=[-currentVelocity, 0], density=0.1))
spawn_barrier.counter = 0

def spawn_rocket(coords, mode):
    if mode == 0: # warning
        rock = pygame.draw.rect(window, 'dark red', [coords[0] - 60, coords[1] - 25, 50, 50], 0, 5)
        window.blit(font.render('!', True, 'black'), (coords[0] - 40, coords[1] - 20))
        if coords[1] > player.pos.y + 10:
            coords[1] -= 3
        else:
            coords[1] += 3
    else: # rocket fires
        rock = pygame.draw.rect(window, 'red', [coords[0], coords[1] - 10, 50, 20], 0 )
        pygame.draw.ellipse(window, 'orange', [coords[0] + 50, coords[1] - 10, 50, 20], 7)
        coords[0] -= 10 + (currentVelocity * 0.02)

    return coords, rock

def spawn_laser_borders(): # spawns laser borders
    laserSpots = [0, 1, 2, 3, 4, 5]
    BoundaryOffsets = [[0, 0], [0, -(window.get_height() - distFromBottom - distFromTop)/6], [50, -(window.get_height() - distFromBottom - distFromTop)/6], [50, 0]]
    laserCount = random.randint(2, 4)
    spawn_laser_borders.usedLaserPosition = []
    for i in range(0, laserCount):
        laserSpot = random.randint(0, len(laserSpots)-1)
        obj_laser_borders.append(UniformPolygon(local_points=(BoundaryOffsets), pos=[0, distFromTop + ((window.get_height() - distFromBottom - distFromTop)/6) + laserSpots[laserSpot]*((window.get_height() - distFromBottom - distFromTop)/6)], color=red, normals_length=0, density=0.1))
        obj_laser_borders.append(UniformPolygon(local_points=(BoundaryOffsets), pos=[window.get_width()-50, distFromTop + ((window.get_height() - distFromBottom - distFromTop)/6) + laserSpots[laserSpot]*((window.get_height() - distFromBottom - distFromTop)/6)], color=red, normals_length=0, density=0.1))
        spawn_laser_borders.usedLaserPosition.append(laserSpots[laserSpot])
        laserSpots.remove(laserSpots[laserSpot])
    return spawn_laser_borders.usedLaserPosition
spawn_laser_borders.usedLaserPosition = []

def spawn_laser(): # spawns a laser
    LaserOffsets = [[0, 0], [0, -(window.get_height() - distFromBottom - distFromTop-150)/6], [window.get_width(), -(window.get_height() - distFromBottom - distFromTop-150)/6], [window.get_width(), 0]]
    for i in range(len(spawn_laser_borders.usedLaserPosition)):
        obj_lasers.append(UniformPolygon(local_points=(LaserOffsets), pos=[0, (distFromTop + ((window.get_height() - distFromBottom - distFromTop)/6) + spawn_laser_borders.usedLaserPosition[i]*((window.get_height() - distFromBottom - distFromTop)/6)) - 12.5], color=red, normals_length=0, density=0.1))

def spawn_bullet(): # spawns a bullet
    bullet = Circle(color=yellow)
    obj_bullets.append(bullet)
    bullet.set(Vector2(player.pos.x, player.pos.y + 10))

def spawn_coin():
    obj_coins.append(Circle(pos=(1250,300), vel=(-(currentVelocity/3),0), radius=20, mass=1, color=yellow, width=0))

# GAME LOOP
running = True
while running:
    # update the display
    pygame.display.update()
    # delay for correct timing
    clock.tick(fps)
    # clear the screen
    window.fill(bg_color)

    # EVENTS
    while event := pygame.event.poll():
        if event.type == pygame.QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False
    
    # CONTROLS
    key = pygame.key.get_pressed()

    # jetpack launch
    if key[K_SPACE] and not dying and not dead and not game_over:
        player.vel += Vector2(0, -16)
        bullet_timer += dt
        if bullet_timer > time_to_spawn_bullet:
            spawn_bullet()
            random_vel_x = random.randint(-100, 100)
            obj_bullets[-1].vel = Vector2(random_vel_x, 500)
            bullet_timer = 0
    # use coins to revive
    elif key[K_SPACE] and dead and coins >= 3 and perm_death_timer < 5:
        coin_timer = 0
        increase_vel_rate = 0.5
        coins -= 3
        dying = False
        dead = False
        perm_death_timer = 0

    # CALCULATIONS
    # distance traveled
    currPos = distanceObject.pos.x
    distanceTraveled += abs(currPos - prevPos)/pixelsPerMeter
    prevPos = distanceObject.pos.x
    
    # obstacle spawns
    if not laserBorderProcess:
        if electricCounter < 10:
            # elec barrier spawn time
            electricTimer += dt
            if currentVelocity > 0 and electricTimer > barrier_spacing / currentVelocity:
                spawn_barrier()
                electricTimer = 0
                electricCounter += 1
            
            # coin spawn time
            if not dead and not game_over:
                coin_timer += dt
                if coin_timer > time_to_spawn_coin:
                    spawn_coin()
                    coin_timer = 0
            
        elif laserCounterStart == False:
            toLaserCounter = 2
            laserCounterStart = True
    else: # laser spawn time
        borderTimer += dt
        for l in obj_laser_borders:
            if l.color == red:
                l.color = black
            else:
                l.color = red
        if borderTimer > 3:
            laserTimer += dt
            if laserProcess == False:
                spawn_laser()
                laserProcess = True
            if laserTimer > 2:
                laserProcess = False
                laserBorderProcess = False
                borderTimer = 0
                laserTimer = 0
                laserBorderProcess = False
                electricCounter = 0
                obj_lasers = []
                obj_laser_borders = []
                laserCounterStart = False

    # rocket spawn time
    if not dead and not game_over:
        if not rocket_active:
            rocket_counter += 1
        if rocket_counter > 180:
            rocket_counter = 0
            rocket_active = True
            rocket_delay = 0
            rocket_coords = [width, height/2]
        if rocket_active:
            if rocket_delay < 90:
                rocket_delay += 1
                rocket_coords, rocket = spawn_rocket(rocket_coords, 0)
            else:
                rocket_coords, rocket = spawn_rocket(rocket_coords, 1)
            if rocket_coords[0] < -50:
                rocket_active = False

    # live velocity changes
    if math.ceil(currentVelocity/pixelsPerMeter) < max_vel_per_meter and not dying and not dead and not game_over:
        currentVelocity += increase_vel_rate

    if math.ceil(currentVelocity/pixelsPerMeter) >= vel_on_death:
        increase_vel_rate = 0.1
    
    # change position of coin
    for c in obj_coins:
        c.pos.y = ((math.sin(coin_direction_timer) + 1.25) * ((window.get_height() - distFromTop - distFromBottom)/2.5) + 50)
    coin_direction_timer += dt

    # bg color change
    if bg_color == light_red:
        color_timer += dt
        if color_timer > time_to_change_color:
            bg_color = sky_blue

    # slow velocity on death
    if dying and currentVelocity > 0:
        currentVelocity -= 2.5
    elif dead and currentVelocity > 0:
        currentVelocity -= 10
    
    if currentVelocity < 0:
        currentVelocity = 0
    
    # permanent death countdown
    if dead:
        perm_death_timer += dt
        if perm_death_timer >= time_to_death:
            game_over = True
    
    # destroy offscreen objects
    for eb in obj_elec_barriers:
        if eb.pos.x < -((window.get_height() - distFromTop - distFromBottom)/2):
            toLaserCounter -= 1
            obj_elec_barriers.remove(eb)
            if toLaserCounter == 0:
                spawn_laser_borders()
                laserBorderProcess = True
    
    for c in obj_coins:
        if c.pos.x < -((window.get_height() - distFromTop - distFromBottom)/2):
            obj_coins.remove(c)

    # PHYSICS
    # forces
    gravity.apply()

    # update objects
    for b in obj_bullets:
        b.update(dt)
    
    for c in obj_coins:
        c.update(dt)

    for eb in obj_elec_barriers:
        eb.vel = Vector2(-currentVelocity, 0)
        eb.update(dt)

    for l in obj_laser_borders:
        l.update(dt)

    for l in obj_lasers:
        l.update(dt)
    
    for w in obj_walls:
        w.update(dt)
    
    player.update(dt)

    distanceObject.vel = Vector2(-currentVelocity, 0)
    distanceObject.update(dt)

    # clear force
    for b in obj_bullets:
        b.clear_force()
    
    for c in obj_coins:
        c.clear_force()

    for eb in obj_elec_barriers:
        eb.clear_force()
    
    for l in obj_laser_borders:
        l.clear_force()
    
    for l in obj_lasers:
        l.clear_force()
    
    for w in obj_walls:
        w.clear_force()
    
    player.clear_force()

    # COLLISIONS
    for w in obj_walls:
        c = contact.generate(player, w, resolve=True, restitution=0.25)
        if c.overlap > 0 and dying:
            dead = True
    
    for b in obj_bullets:
        c = contact.generate(b, ground_wall, resolve=False)
        if c.overlap > 0:
            obj_bullets.remove(b)

    revive_timer += dt
    for eb in obj_elec_barriers:
        c = contact.generate(player, eb, resolve=False)
        if c.overlap > 0 and not dead and not game_over and revive_timer > time_to_revive:
            bg_color = light_red
            vel_on_death = currentVelocity / pixelsPerMeter
            dying = True
            revive_timer = 0

    if rocket_active:
        if rocket.collidepoint(player.pos) and not dead and not game_over and revive_timer > time_to_revive:
            bg_color = light_red
            vel_on_death = currentVelocity / pixelsPerMeter
            dying = True
            revive_timer = 0
        
    for l in obj_lasers:
        c = contact.generate(player, l, resolve=False)
        if c.overlap > 0 and not dead and not game_over and revive_timer > time_to_revive:
            bg_color = light_red
            vel_on_death = currentVelocity / pixelsPerMeter
            dying = True
            revive_timer = 0

    for coin in obj_coins:
        c = contact.generate(player, coin, resolve=False)
        if c.overlap > 0 and not dead and not game_over:
            coins += 1
            obj_coins.remove(coin)

    # GRAPHICS
    # draw objects
    for b in obj_bullets:
        b.draw(window)
    
    for c in obj_coins:
        c.draw(window)

    for eb in obj_elec_barriers:
        eb.draw(window)
    
    for l in obj_lasers:
        l.draw(window)

    for l in obj_laser_borders:
        l.draw(window)
        
    for w in obj_walls:
        w.draw(window)
    
    player.draw(window)
    
    # draw text
    text_surface = font.render(f"Vel: {math.ceil(currentVelocity/pixelsPerMeter)}m/s", True, white)
    window.blit(text_surface, (25, 5))

    text_surface = font.render(f"Distance Traveled: {math.ceil(distanceTraveled)}m", True, white)
    window.blit(text_surface, (window.get_width() / 2 - text_surface.get_width() / 2, 5))

    text_surface = font.render(f"Coins: {math.ceil(coins)}", True, white)
    window.blit(text_surface, (window.get_width() - text_surface.get_width() - 25, 5))

    if dead and not game_over:
        text_surface = big_font.render(f"SPACE TO REVIVE", True, light_red)
        window.blit(text_surface, (window.get_width() / 2 - text_surface.get_width() / 2, window.get_height() / 2 - text_surface.get_height() - 75))

        text_surface = big_font.render(f"COST: 3 COINS", True, light_red)
        window.blit(text_surface, (window.get_width() / 2 - text_surface.get_width() / 2, window.get_height() / 2 - text_surface.get_height()))

        text_surface = big_font.render(f"HURRY! {6 - math.ceil(perm_death_timer)}S LEFT!", True, light_red)
        window.blit(text_surface, (window.get_width() / 2 - text_surface.get_width() / 2, window.get_height() / 2 - text_surface.get_height() + 75))
    
    if game_over:
        text_surface = big_font.render(f"GAME OVER...", True, light_red)
        window.blit(text_surface, (window.get_width() / 2 - text_surface.get_width() / 2, window.get_height() / 2 - text_surface.get_height() / 2))