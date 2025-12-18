import pygame

class Enemy:
    def __init__(self, rect, dir, assets):
        self.rect = rect.copy()
        self.dir = dir
        self.assets = assets

    def move(self):
        self.rect.x += self.dir * 2
        if self.rect.x < 300:
            self.dir = 1
        elif self.rect.x > 1900:
            self.dir = -1

    def draw(self, screen, camera_x):
        draw_x = self.rect.x - camera_x
        if self.assets.enemy_img_left and self.assets.enemy_img_right:
            img = self.assets.enemy_img_right if self.dir == 1 else self.assets.enemy_img_left
            img_scaled = pygame.transform.scale(img, (self.rect.width, self.rect.height))
            blit_y = self.rect.bottom - img_scaled.get_height()
            screen.blit(img_scaled, (draw_x, blit_y))
        else:
            pygame.draw.rect(screen, (0, 120, 0), (draw_x, self.rect.y, self.rect.width, self.rect.height))