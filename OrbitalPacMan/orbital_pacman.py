import pygame
from pygame.locals import *
from pygame.math import Vector2, Vector3
import random
import math
from physics_objects import Circle

# INITIALIZE PYGAME
pygame.init()

# CREATE WINDOW
screen_width, screen_height = pygame.display.get_desktop_sizes()[0]
SIZE = 0.4*min(screen_height, screen_width)
window = pygame.display.set_mode([2*SIZE+1, 2*SIZE+1])
label_font = pygame.font.SysFont("comicsansms", 150)
timer_font = pygame.font.SysFont("comicsansms", 30)

# CONSTANTS
force = Vector2(0, 0)
thrust = SIZE/15
gravitational_constant = thrust * pow(SIZE, 2)

# TIMING
clock = pygame.time.Clock()
FPS = 60
dt = 1/FPS
clock.tick()
best_time = 0

# GAME LOOP
StartGame = True
while StartGame:
    running = True
    StartGame = False
    Win = False
    Lose = False
    timer = 0

    # OBJECTS
    sun = Circle(radius=SIZE/10, pos=(SIZE+0.5,SIZE+0.5), color=(255,255,0))
    ship = Circle(radius=SIZE/30, pos=sun.pos-Vector2(SIZE,SIZE)/2, color=(135,206,235), vel=(100,0))
    thrust_flame = Circle(radius=SIZE/40, pos=ship.pos, color=(255,255,0), vel=ship.vel)

    objects = []
    objects.append(sun)
    objects.append(thrust_flame)
    objects.append(ship)

    initial_speed = math.sqrt((gravitational_constant / (ship.pos - sun.pos).magnitude_squared()) * (ship.pos - sun.pos).magnitude())
    initial_vel = initial_speed * (ship.pos - sun.pos).normalize().rotate(90)
    ship.vel = initial_vel

    print(sun.radius)

    dots = []
    for i in range(0, 6):
        x = random.randint(0, 700) - 350
        y = random.randint(0, 700) - 350
        dots.append(Circle(radius=ship.radius/2, pos=(sun.pos + (Vector2(x, y).normalize() * (sun.radius + 50 + (len(dots) * 75)))), color=(255,255,255)))
        dot_initial_speed = math.sqrt((gravitational_constant / (dots[i].pos - sun.pos).magnitude_squared()) * (dots[i].pos - sun.pos).magnitude())
        dot_initial_vel = dot_initial_speed * (dots[i].pos - sun.pos).normalize().rotate(90)
        dots[i].vel = dot_initial_vel
    
    while running:
        # DISPLAY AND TIMING
        pygame.display.update()
        dt = clock.tick(FPS) / 1000
        if not Win and not Lose:
            timer += dt

        # BACKGROUND GRAPHICS
        window.fill((0,0,0))

        # EVENTS
        while event := pygame.event.poll():
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False

        # PHYSICS
        ## Add forces
        ### Gravitational force
        force = Vector2(0, 0)
        gravity = -(((gravitational_constant * sun.mass * ship.mass) / (ship.pos - sun.pos).magnitude_squared()) * (ship.pos - sun.pos).normalize())
        force += gravity
        ship.add_force(force)

        force = Vector2(0, 0)
        for i in dots:
            gravity = -(((gravitational_constant * sun.mass * i.mass) / (i.pos - sun.pos).magnitude_squared()) * (i.pos - sun.pos).normalize())
            force += gravity
            i.add_force(force)
            force = Vector2(0, 0)

        ### Thrust force
        # key state check
        force = Vector2(0, 0)
        thrust_flame.pos = ship.pos - Vector2(0, 0)
        key = pygame.key.get_pressed() # returns a list of booleans of the state of every key
        if key[K_UP] or key[K_w]:
            thrust_flame.pos += Vector2(0, 10)
            force += Vector2(0, -1)
        if key[K_DOWN] or key[K_s]:
            thrust_flame.pos += Vector2(0, -10)
            force += Vector2(0, 1)
        if key[K_RIGHT] or key[K_d]:
            thrust_flame.pos += Vector2(-10, 0)
            force += Vector2(1, 0)
        if key[K_LEFT] or key[K_a]:
            thrust_flame.pos += Vector2(10, 0)
            force += Vector2(-1, 0)

        if force:
            force = thrust * force.normalize() * 3
            ship.add_force(force)
            thrust_flame.add_force(force)

        if key[K_SPACE] and (Win or Lose): # True if spacebar is pressed
            StartGame = True
            running = False

        ## Update objects
        for o in objects:
            o.update(dt)
        for d in dots:
            d.update(dt)
        ## Clear force on all objects
        for o in objects:
            o.clear_force()
        for d in dots:
            d.clear_force()
        
        # GAME ELEMENTS
        ## Dot collection
        for d in dots:
            if math.dist(d.pos, ship.pos) <= ship.radius + i.radius:
                dots.remove(d)
        
        # Lines
        if ship.pos.x > window.get_width() or ship.pos.y > window.get_height() or ship.pos.x < 0 or ship.pos.y < 0:
            line_length = Vector2(ship.pos - sun.pos).magnitude()
            line_angle = Vector2(ship.pos - sun.pos).normalize()

            offset_pos = math.asin(ship.radius / Vector2(ship.pos - sun.pos).magnitude())
            actual_pos_angle = line_angle.rotate_rad(offset_pos)
            actual_pos_endpoint = sun.pos + actual_pos_angle * line_length

            offset_neg = -(math.asin(ship.radius / Vector2(ship.pos - sun.pos).magnitude()))
            actual_neg_angle = line_angle.rotate_rad(offset_neg)
            actual_neg_endpoint = sun.pos + actual_neg_angle * line_length

            pygame.draw.line(window, (255,255,255), sun.pos, actual_pos_endpoint, 1)
            pygame.draw.line(window, (255,255,255), sun.pos, actual_neg_endpoint, 1)

    
        ## Winning
        if (not dots) and not Win and not Lose and (best_time == 0 or timer <= best_time):
            Win = True
        
        ## Losing
        if ((math.dist(sun.pos, ship.pos) <= ship.radius + sun.radius) and not Win and not Lose) or ((best_time != 0 and timer > best_time) and not Win and not Lose):
            Lose = True
            objects.remove(ship)
            objects.remove(thrust_flame)

        # GRAPHICS
        for o in objects:
            o.draw(window)    
        for d in dots:
            d.draw(window)
        
        if Win:
            text_surface = label_font.render("YOU WON!", True, (255,255,255))
            x = window.get_width() / 2 - text_surface.get_width() / 2
            y = window.get_height() / 2 - text_surface.get_height() / 2
            window.blit(text_surface, (x, y))

            text_surface_2 = timer_font.render(f"Now you must win within your fastest time...", True, (255,255,255))
            x = window.get_width() / 2 - text_surface_2.get_width() / 2
            y = window.get_height() / 2 - text_surface_2.get_height() / 2 + 200
            window.blit(text_surface_2, (x, y))

            best_time = timer
            print(best_time)
        
        if Lose:
            text_surface = label_font.render("YOU LOST!", True, (255,255,255))
            x = window.get_width() / 2 - text_surface.get_width() / 2
            y = window.get_height() / 2 - text_surface.get_height() / 2
            window.blit(text_surface, (x, y))

            if timer > best_time and best_time != 0:
                text_surface_2 = timer_font.render("Too slow...", True, (255,255,255))
                x = window.get_width() / 2 - text_surface.get_width() / 2
                y = window.get_height() / 2 - text_surface.get_height() / 2 + 200
                window.blit(text_surface_2, (x, y))
        
        # TIMER
        if int(timer % 60) < 10:
            time_text = f"Time: {int(timer / 60)}:0{int(timer % 60)}"
        else:
            time_text = f"Time: {int(timer / 60)}:{int(timer % 60)}"
        
        text_surface = timer_font.render(time_text, True, (255,255,255))
        x = window.get_width() - text_surface.get_width()
        y = window.get_height() - text_surface.get_height()
        window.blit(text_surface, (x, y))