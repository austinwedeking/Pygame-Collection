import pygame
from pygame.math import Vector2
import itertools
import math
from physics_objects import PhysicsObject

class SingleForce: # air drag
    def __init__(self, objects_list=[]):
        self.objects_list = objects_list #single force just needs a list of objects

    def apply(self):
        for obj in self.objects_list:
            obj:PhysicsObject
            force = self.force(obj)
            obj.add_force(force)

    def force(self):
        return Vector2(0, 0)


class PairForce: # repulsion
    def __init__(self, objects_list=[]):
        self.objects_list = objects_list

    def apply(self):
        # Loop over all pairs of objects and apply the calculated force
        for i in range(len(self.objects_list)):
            for j in range(i): # j < i
                a:PhysicsObject = self.objects_list[i]
                b:PhysicsObject = self.objects_list[j]
                force = self.force(a, b)
                a.add_force(force)
                b.add_force(-force)

class BondForce: # spring
    def __init__(self, pairs_list=[]): # need the list of specific pairs
        # pairs_list has the format 
        # [[obj1, obj2], [obj3, obj4], ... ] 
        # ^ each pair representing a bond
        self.pairs_list = pairs_list

    def apply(self):
        # Loop over all *pairs* from the pairs list.  
        for a, b in self.pairs_list:
            a:PhysicsObject
            b:PhysicsObject
            force = self.force(a, b)
            a.add_force(force)
            b.add_force(-force)
    
    def force(self, a, b):
        return Vector2(0, 0)


# Add Gravity, SpringForce, SpringRepulsion, AirDrag
class Gravity(SingleForce):
    def __init__(self, acc=(0,0), **kwargs):
        self.acc = Vector2(acc)
        super().__init__(**kwargs)

    def force(self, obj:PhysicsObject):
        return obj.mass*self.acc # force of gravity = m*g
    
class SpringForce(BondForce):
    def __init__(self, stiffness=0, length=0, damping=0, window=[0,0], **kwargs):
        self.stiffness = stiffness  # k
        self.length = length        # l
        self.damping = damping      # b
        self.window = window
        super().__init__(**kwargs)

    def force(self, a:PhysicsObject, b:PhysicsObject):
        r = a.pos - b.pos
        v = a.vel - b.vel
        return (-self.stiffness * (r.magnitude() - self.length) - self.damping * v.dot(r.normalize())) * r.normalize()
    
    def draw(self):
        for a, b in self.pairs_list:
            pygame.draw.line(self.window, (255,255,255), a.pos, b.pos, 1)

class AirDrag(SingleForce):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def force(self, obj:PhysicsObject):
        dragCoefficient = 0.005
        return -(dragCoefficient * (obj.mass / 1000) * (3.14 * obj.radius**2) * obj.vel.magnitude() * obj.vel) / 2

class SpringRepulsion(PairForce):
    def __init__(self, stiffness=0, **kwargs):
        self.stiffness = stiffness
        super().__init__(**kwargs)
    
    def force(self, a:PhysicsObject, b:PhysicsObject):
        r = a.pos - b.pos
        if (a.radius + b.radius - r.magnitude() > 0):
            repulsion = self.stiffness * (a.radius + b.radius - r.magnitude()) * r.normalize()
        else:
            repulsion = Vector2(0, 0)
        return repulsion
    
class FrictionForce(SingleForce):
    def __init__(self, mu=0.3, g=9.81):
        self.mu = mu
        self.g = g
    
    def apply(self,obj):
        if obj.vel.length() > 0:
            friction_force = -self.mu * obj.mass * self.g * obj.vel.normalize()
            obj.add_force(friction_force)
        else: 
            obj.vel =  Vector2(0,0)