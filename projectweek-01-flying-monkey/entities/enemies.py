import pygame
import random
import math

# ==========================================
# DE BASIS KLASSE (OUDER)
# ==========================================
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, asset_manager, image_key):
        super().__init__()
        self.am = asset_manager
        
        # Basis eigenschappen
        self.rect = pygame.Rect(x, y, width, height)
        self.image_key = image_key
        
        # Probeer plaatje te laden om de fallback te voorkomen
        self.image = self.am.get(image_key)
        
    def draw(self, screen, camera_x):
        # We halen het plaatje op uit de manager
        img = self.am.get(self.image_key)
        
        if img:
            # Teken het plaatje
            # We passen de positie iets aan zodat het plaatje mooi op de hitbox staat
            draw_pos = (self.rect.x - camera_x, self.rect.bottom - img.get_height())
            
            # Flip logic (wordt door kind-klassen gebruikt, standaard False)
            if hasattr(self, 'direction') and self.direction == 1:
                img = pygame.transform.flip(img, True, False)
                
            screen.blit(img, draw_pos)
        else:
            # Fallback rood blokje
            pygame.draw.rect(screen, (255, 0, 0), (self.rect.x - camera_x, self.rect.y, self.rect.width, self.rect.height))


# ==========================================
# LEVEL 1 VIJAND: PADDENSTOEL/SLANG (KIND)
# ==========================================
class PatrolEnemy(Enemy):
    def __init__(self, x, y, direction, min_x, max_x, asset_manager):
        # Animation: slang (snake) and slang_tong (snake with tongue)
        super().__init__(x, y, 60, 40, asset_manager, "slang")
        self.direction = direction # 1 = rechts, -1 = links
        self.min_x = min_x
        self.max_x = max_x
        self.speed = 2
        self.anim_timer = 0
        self.anim_frame = 0
        # Preload both images for animation
        self.snake_imgs = [
            pygame.transform.scale(self.am.get("slang"), (50, 50)) if self.am.get("slang") else None,
            pygame.transform.scale(self.am.get("slang_tong"), (50, 50)) if self.am.get("slang_tong") else None
        ]
        # If not found, fallback to enemy
        if not self.snake_imgs[0]:
            self.snake_imgs[0] = self.am.get("enemy")
        if not self.snake_imgs[1]:
            self.snake_imgs[1] = self.snake_imgs[0]
        # Store the ground level (bottom) for flush alignment
        # y is the platform top, so ground_y should be y (platform top) + platform height
        # To keep the snake above ground, set ground_y to y (platform top)
        self.ground_y = y  # Use platform top as ground
        self.snake_offset_y = 10  # Offset for visual floating

    def update(self):
        # Animation: switch frame every 0.25s
        self.anim_timer += 1
        if self.anim_timer >= 15:  # ~0.25s at 60fps
            self.anim_frame = 1 - self.anim_frame
            self.anim_timer = 0
        # Move
        self.rect.x += self.direction * self.speed
        # Keep bottom flush to ground (so image sits on top of platform, not inside)
        self.rect.bottom = self.ground_y
        # Keer om als we de grenzen raken
        if self.rect.x < self.min_x:
            self.direction = 1
        elif self.rect.x > self.max_x:
            self.direction = -1

    def update(self):
        # Animation: switch frame every 0.25s
        self.anim_timer += 1
        if self.anim_timer >= 15:  # ~0.25s at 60fps
            self.anim_frame = 1 - self.anim_frame
            self.anim_timer = 0
        # Move
        self.rect.x += self.direction * self.speed
        # Keer om als we de grenzen raken
        if self.rect.x < self.min_x:
            self.direction = 1
        elif self.rect.x > self.max_x:
            self.direction = -1

    def draw(self, screen, camera_x, camera_y=0):
        img = self.snake_imgs[self.anim_frame]
        if img:
            # Always align bottom to ground, but float above by offset
            draw_pos = (self.rect.x - camera_x, self.rect.bottom - img.get_height() - self.snake_offset_y - camera_y)
            if self.direction == 1:
                img = pygame.transform.flip(img, True, False)
            screen.blit(img, draw_pos)
        else:
            pygame.draw.rect(screen, (0, 200, 0), (self.rect.x - camera_x, self.rect.y - camera_y, self.rect.width, self.rect.height))


# ==========================================
# LEVEL 2 VIJAND: VALLEND MES (KIND)
# ==========================================
class FallingEnemy(Enemy):
    def __init__(self, x, y, asset_manager):
        # Messen zijn smal en hoog (30x80)
        super().__init__(x, y, 30, 80, asset_manager, "knife")
        self.speed_y = 6.5

    def update(self):
        # Val naar beneden
        self.rect.y += self.speed_y

# ==========================================
# LEVEL 3 BOSS: CLOUD (BOSS)
# ==========================================
class BossEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, asset_manager):
        super().__init__()
        self.am = asset_manager
        self.rect = pygame.Rect(x, y, width, height)

        # Movement
        self.speed = 5
        self.direction = 1

        # Visual
        self.image = self.am.get("cloud")

        # Attack logic
        self.knife_timer = 0
        self.knife_interval = 1000

        self.curtain_timer = 0
        self.curtain_cooldown = random.randint(5000, 10000)
        self.curtain_active = False

    def update(self, dt, screen_width):
        # Movement
        self.rect.x += self.speed * self.direction
        if self.rect.left <= 0 or self.rect.right >= screen_width:
            self.direction *= -1

        # Timers
        self.knife_timer += dt
        self.curtain_timer += dt

    def draw(self, screen):
        if self.image:
            scale_factor = 1.7
            new_size = (int(self.image.get_width() * scale_factor), int(self.image.get_height() * scale_factor))
            big_cloud = pygame.transform.smoothscale(self.image, new_size)
            cloud_rect = big_cloud.get_rect(center=self.rect.center)
            screen.blit(big_cloud, cloud_rect.topleft)
        else:
            pygame.draw.rect(screen, (255, 0, 0), self.rect)

    def get_lightning_spawn(self):
        if self.image:
            scale_factor = 1.7
            new_size = (int(self.image.get_width() * scale_factor), int(self.image.get_height() * scale_factor))
            big_cloud = pygame.transform.smoothscale(self.image, new_size)
            cloud_rect = big_cloud.get_rect(center=self.rect.center)
            # Offset the lightning spawn point slightly downward (e.g., 10 pixels)
            offset = 10
            return cloud_rect.centerx, cloud_rect.bottom + offset
        return self.rect.centerx, self.rect.bottom

    def handle_attacks(self, knives, ammo_speed):
        # Normal attack
        if not self.curtain_active and self.knife_timer >= self.knife_interval:
            self.knife_timer = 0
            x, y = self.get_lightning_spawn()
            knives.append({
                "rect": pygame.Rect(x - 5, y, 10, 20),
                "vx": 0,
                "vy": ammo_speed
            })

        # Curtain attack
        if not self.curtain_active and self.curtain_timer >= self.curtain_cooldown:
            self.curtain_active = True
            self.curtain_timer = 0
            self.curtain_cooldown = random.randint(5000, 10000)

            x, y = self.get_lightning_spawn()
            for i in range(10):
                angle = -0.6 + i * (1.2 / 9)
                vx = int(ammo_speed * math.sin(angle))
                vy = int(ammo_speed * math.cos(angle))
                knives.append({
                    "rect": pygame.Rect(x - 5, y, 10, 20),
                    "vx": vx,
                    "vy": vy
                })

        # End curtain burst
        if self.curtain_active and self.knife_timer >= 200:
            self.curtain_active = False
            self.knife_timer = 0