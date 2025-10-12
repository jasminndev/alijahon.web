# import re
# from os import getpid
#
# print(getpid())
import os
import time
from dataclasses import dataclass

import django
from PIL.ImageChops import logical_or

from apps.tasks import add

# tmp = lambda a , b: a  + b
# print(tmp(1, 2))
# print(tmp(2, 3))

# lambda + comprehension + val if con else val + map() , filter()

# def tmp(a,/,*,b):
#     pass
#
# tmp(1 , b=4)

# def tmp():
#     a = 10
#     def tmp2():
#         nonlocal a
#         b = 20
#         a = 30
#     tmp2()
#     print(a)
#
# tmp()


# @dataclass
# class A:
#     a : int = None
#     b : int = None
#     c : int = None
#
# @dataclass
# class B(A):
#     d : int = None
#     z : int = None
#
# print(B(1, 2, 3, 4))


# class A:
#     __slots__ = ("a","b","c")
#     def __init__(self , a , b , c):
#         self.a = a
#         self.b = b
#         self.c = c

# l = [1,2,3,4,5]
# print(id(l))
# print(l)
# logic
# for i in range(len(l)):
#     l[i] = l[i]**2
# l = []
# print(id(l))
# print(l)

# def tmp(a , b):
#     pass
#
# tmp(1,b=2)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')
django.setup()
start = time.time()
add.delay(1,2)
end = time.time()
print(f"Ish bajarildi ! Tekishirib ko'rishingiz mumkin ! Time: {end-start}")


