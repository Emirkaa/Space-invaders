import pygame

class Laser(pygame.sprite.Sprite):
    def __init__(self, pos, speed, screen_hight):
        super().__init__()
        self.image = pygame.Surface((3,15))
        self.image.fill('white')
        self.rect = self.image.get_rect(center = pos)
        self.speed = speed
        self.height_constraint = screen_hight

    def destroy(self):
        if self.rect.y <= -50 or self.rect.y >= self.height_constraint + 50:
            self.kill()

    def update(self):
        self.rect.y += self.speed
        self.destroy()