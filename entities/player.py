import pygame

class Player:
    def __init__(self, x, y, assets):
        self.rect = pygame.Rect(x, y, 60, 60)
        self.vel_y = 0
        self.speed = 5
        self.jump_power = -15
        self.gravity = 1
        self.on_ground = False
        self.dir = 1  # 1 right, -1 left
        self.walk_anim_time = 0
        self.walk_anim_interval = 200
        self.walk_frame = 0
        self.assets = assets

    def move(self, keys, platforms):
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -self.speed
            self.dir = -1
        if keys[pygame.K_RIGHT]:
            dx = self.speed
            self.dir = 1

        self.rect.x += dx
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat) and self.vel_y >= 0:
                prev_bottom = self.rect.y - self.vel_y + self.rect.height
                if prev_bottom <= plat.top and self.rect.bottom >= plat.top:
                    self.rect.bottom = plat.top
                    self.vel_y = 0
                    self.on_ground = True

    def update_animation(self, dt_ms, keys):
        moving_h = (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) and self.on_ground
        if moving_h:
            self.walk_anim_time += dt_ms
            if self.walk_anim_time >= self.walk_anim_interval:
                self.walk_frame = 1 - self.walk_frame
                self.walk_anim_time -= self.walk_anim_interval
        else:
            self.walk_frame = 0
            self.walk_anim_time = 0

    def get_image(self, keys):
        moving_h = (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) and self.on_ground
        if not self.on_ground:
            if self.dir == 1 and self.assets.player_jump_right:
                return self.assets.player_jump_right
            elif self.dir == -1 and self.assets.player_jump_left:
                return self.assets.player_jump_left
            else:
                return self.assets.player_idle_left if self.dir == -1 and self.assets.player_idle_left else self.assets.player_idle_img
        elif moving_h and self.dir == 1 and self.assets.player_walk_frames_right:
            return self.assets.player_walk_frames_right[self.walk_frame]
        elif moving_h and self.dir == -1 and self.assets.player_walk_frames_left:
            return self.assets.player_walk_frames_left[self.walk_frame]
        else:
            return self.assets.player_idle_left if self.dir == -1 and self.assets.player_idle_left else self.assets.player_idle_img

    def draw(self, screen, camera_x):
        img = self.get_image(pygame.key.get_pressed())
        if img:
            img_h = img.get_height()
            blit_y = self.rect.bottom - img_h
            screen.blit(img, (self.rect.x - camera_x, blit_y))
        else:
            pygame.draw.rect(screen, (150, 100, 60), (self.rect.x - camera_x, self.rect.y, self.rect.width, self.rect.height))