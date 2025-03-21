import pygame

def play_sound(file_path: str):
    pygame.mixer.init()
    pygame.mixer.Sound(file_path).play()