import pygame
from pygame.math import Vector2

class PhysicsObject:
    def __init__(self, pos=(0,0), vel=(0,0), mass=1):
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.mass = mass
        self.force = Vector2(0, 0)

    def clear_force(self):
        self.force *= 0

    def add_force(self, force):
        self.force += force

    def update(self, dt):
        # update velocity using the current force
        self.vel += self.force / self.mass * dt
        # update position using the newly updated velocity
        self.pos += self.vel * dt

class Circle(PhysicsObject):
    def __init__(self, radius=100, color=(255,255,255), width=0, **kwargs): # kwargs = keyword arguments
        super().__init__(**kwargs) # calls superclass constructor
        self.radius = radius
        self.color = color
        self.width = width

    def draw(self, window):
        pygame.draw.circle(window, self.color, self.pos, self.radius, self.width)

