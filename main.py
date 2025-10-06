#!/usr/bin/env python

print("Hello")

from enum import IntEnum

class Status(IntEnum):
    SUCCESS = 1
    FAILURE = 2
    PENDING = 3

    def __new__(cls, value):
        obj = int.__new__(cls, value)
        obj._description_ = f"Code {value}"  # attach extra attribute
        return obj

# class A:
#     def x():
#         print("x")
#     class B(A):
#         def __init__(self):
#             print("Class B")

print(Status.SUCCESS._description_)   # "Code 1"
print(Status.FAILURE._description_)   # "Code 2"

# A.B()

class Instr:
    def __init__(self, id, **kwargs):   # <-- **kwargs
        self.id = id
        self.kwargs = kwargs            # dict of keyword args
    
    def exec(self, emu):
        pass

    def __str__(self):
        return self.__class__.__name__


class Sys(Instr):
    def __init__(self, **kwargs):       # <-- **kwargs
        super().__init__("0NNN", **kwargs)


x = Sys(N=123, X=23)
print(x)           # Sys
print(x.kwargs)    # {'N': 123, 'X': 23}