#!/usr/bin/python3

import abc
import math

class Vector(abc.ABC):
    def __init__(self, *components):
        self.__d = len(components)
        self.__components = components

    @property
    def components(self):
        return self.__components
    
    @property
    def dimension(self):
        return self.__d
    
    @property
    def length(self):
        return math.sqrt(self*self)

    # overrides
    def __repr__(self):
       return "<{}, {}>".format(
               self.__class__.__name__,
               self.__components
               )
 
    def __add__(self, other):
        if isinstance(other, (int, float, bool)):
            return self.__class__(*[
                other + self.components[i] for i in range(self.__d)
                ])
        elif isinstance(other, self.__class__):
            return self.__class__(*[
                other.components[i] + self.components[i] for i in range(self.__d)
                ])
        else:
            return NotImplemented

    def __radd__(self, other):
        return self+other

    def __sub__(self, other): # rsub does not make sense
        return self+(-1*other)

    def __mul__(self, other):
        if isinstance(other, (int, float, bool)):
            return self.__class__(*[
                other * self.components[i] for i in range(self.__d)
                ])
        elif isinstance(other, self.__class__):
            return sum([
                self.components[i]*other.components[i] for i in range(self.__d)
                ])
        else:
            return NotImplemented

    def __rmul__(self, other):
        return self*other


class Vector3D(Vector):
    def __init__(self, x, y, z):
        super().__init__(x,y,z)


class Vector2D(Vector):
    def __init__(self, x, y):
        super().__init__(x, y)
