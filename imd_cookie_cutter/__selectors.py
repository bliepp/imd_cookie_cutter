#!/usr/bin/python3

import abc


class ISelectorStrategy(abc.ABC):
    def __init__(self, position):
        self.position = position

    @abc.abstractmethod
    def contains(self, point):
        return False


class SphereSelector(ISelectorStrategy):
    def __init__(self, position, radius):
        super().__init__(position)
        self.radius = radius

    def contains(self, point, strict=False):
        rel = (point - self.position).length
        return (
            ( rel < self.radius and strict ) 
            or ( rel <= self.radius and not strict )
            )


class BoxSelector(ISelectorStrategy):
    def __init__(self, position, size):
        super().__init__(position)
        self.size = size

    def contains(self, point, strict=False):
        rel = (point - self.position).components
        maximum = self.size.components
        for i in range(len(self.size.components)):
            cond = (
                ( (rel[i] <= 0 or rel[i] >= maximum[i]) and strict )
                or ( (rel[i] < 0 or rel[i] > maximum[i]) and not strict )
                ) # out of boundaries
            if cond: return False
        return True # "global" else
