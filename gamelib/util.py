import os

import pygame
from pygame.locals import *

IMAGE_CACHE = {}

def load_image(filename):
    if filename not in IMAGE_CACHE:
        img = pygame.image.load(os.path.join("data", "images", filename)).convert_alpha()
        IMAGE_CACHE[filename] = img
    return IMAGE_CACHE[filename]

def load_images(*files):
    imgs = []
    for f in files:
        imgs.append(load_image(f))
    return imgs

def load_strip(filename, width):
    imgs = []
    img = load_image(filename)
    for x in range(img.get_width()/width):
        i = img.subsurface(pygame.Rect(x*width, 0, width, img.get_height()))
        imgs.append(i)
    return imgs

def load_sheet(filename, width, height):
    imgs = []
    img = load_image(filename)
    for y in range(img.get_height()/height):
        row = []
        for x in range(img.get_width()/width):
            i = img.subsurface(pygame.Rect(x*width, y*height, width, height))
            row.append(i)
        imgs.append(row)
    return imgs

def flip_images(images):
    imgs = []
    for i in images:
        imgs.append(pygame.transform.flip(i, 1, 0))
    return imgs

def load_sound(filename):
    return pygame.mixer.Sound(os.path.join("data", filename))
