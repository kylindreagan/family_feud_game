import pygame

def play_sound(file_path: str):
    pygame.mixer.init()
    sound = pygame.mixer.Sound(file_path)
    sound.play()
    return sound

def stop_sound(sound):
    sound.stop()