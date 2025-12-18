import pygame
import math

class Coin:
    def __init__(self, rect):
        self.rect = rect.copy()

    def draw(self, screen, camera_x, assets):
        if assets.coin_img:
            t = pygame.time.get_ticks() / 1000.0
            freq = 0.7
            amp = 6
            bob = math.sin(t * 2 * math.pi * freq) * amp
            new_w = max(1, int(self.rect.width * 2.5))
            new_h = max(1, int(self.rect.height * 2.5))
            img = pygame.transform.scale(assets.coin_img, (new_w, new_h))
            blit_x = self.rect.x - camera_x - (new_w - self.rect.width) // 2
            blit_y = int(self.rect.y + bob - (new_h - self.rect.height))
            screen.blit(img, (blit_x, blit_y))
        else:
            pygame.draw.rect(screen, (255, 223, 0), (self.rect.x - camera_x, self.rect.y, self.rect.width, self.rect.height))