from typing import Any
import pygame
from pygame.math import *
import math

class PhysicsObject:
    def __init__(self, pos=(0,0), vel=(0,0), mass=1, angle=0, avel=0, momi=math.inf, freeze_position=False):
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.mass = mass
        self.angle = angle
        self.avel = avel
        self.momi = momi
        self.force = Vector2(0, 0)
        self.torque = 0
        self.pivot = Vector2(0,0)
        self.freeze_position = freeze_position

    def clear_force(self):
        self.force *= 0
        self.torque *= 0

    def add_force(self, force):
        self.force += force
    
    def add_torque(self, torque):
        self.torque += torque
    
    def impulse(self, impulse):
        self.vel += Vector2(impulse) / self.mass

    def update(self, dt):
        # update velocity using the current force
        self.vel += (self.force / self.mass) * dt
        # update position using the newly updated velocity
        if not self.freeze_position:
            self.pos += self.vel * dt

        # update angular
        self.avel += (self.torque / self.momi) * dt
        self.angle += self.avel * dt

class Polygon(PhysicsObject):
    def __init__(self, local_points=[], pivot=(0,0), color=(255,255,255), width=0, normals_length=0, **kwargs):
        super().__init__(**kwargs)
        self.local_points = [Vector2(p) for p in local_points]

        self.local_normals = []
        for i in range(len(self.local_points)):
            normal = (self.local_points[i] - self.local_points[i - 1]).normalize().rotate(90)
            self.local_normals.append(normal)
        
        self.check_convex()

        self.pivot = Vector2(pivot)
        self.color = color
        self.width = width
        self.normals_length = normals_length
        self.contact_type = "Polygon"
        self.update()

    def check_convex(self):
        if len(self.local_points) > 3:
            n = len(self.local_points)
            convex = True
            for i in range(n):
                d = [(self.local_points[j%n] - self.local_points[i]).dot(self.local_normals[i]) 
                     for j in range(i+1, i+n-1)]
                if max(d) <= 0:
                    pass
                elif min(d) >= 0:
                    self.local_normals[i] *= -1
                else:
                    convex = False
            if not convex:
                print("WARNING!  Non-convex polygon defined.  Collisions will be incorrect.")
                
    def update(self, dt=0):
        super().update(dt)
        self.points = [(p - self.pivot).rotate_rad(self.angle) + self.pivot + self.pos for p in self.local_points]
        self.normals = [n.rotate_rad(self.angle) for n in self.local_normals]
    
    def draw(self, window):
        pygame.draw.polygon(window, self.color, self.points, self.width)
        if self.normals_length > 0:
            for point, normal in zip(self.points, self.normals):
                pygame.draw.line(window, self.color, point, point + normal * self.normals_length)


class Circle(PhysicsObject):
    def __init__(self, radius=100, color=(255,255,255), width=0, **kwargs): # kwargs = keyword arguments
        super().__init__(**kwargs) # calls superclass constructor
        self.radius = radius
        self.color = color
        self.width = width
        self.contact_type = "Circle"

    def draw(self, window):
        pygame.draw.circle(window, self.color, self.pos, self.radius, self.width)

    def contains_point(self, point):
        diff_point = Vector2(point)
        distance = (self.pos - Vector2(point)).length()
        return distance <=self.radius

class Wall(PhysicsObject):
    def __init__(self, point1=(0, 0), point2=(0, 0), color=(255, 255, 255), width=1):
        self.point1 = Vector2(point1)
        self.point2 = Vector2(point2)
        self.color = color
        self.width = width
        self.normal = (self.point2 - self.point1).normalize().rotate(90)
        super().__init__(pos = (self.point1 + self.point2) / 2, mass = math.inf)
        self.contact_type = "Wall"
    
    def draw(self, window):
        pygame.draw.line(window, self.color, self.point1, self.point2, self.width)