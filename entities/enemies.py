import pygame
import random

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
        # We maken hem 40x40 (kleiner, zoals je vroeg)
        # We roepen de __init__ van de ouder aan
        super().__init__(x, y, 40, 40, asset_manager, "enemy")
        
        self.direction = direction # 1 = rechts, -1 = links
        self.min_x = min_x
        self.max_x = max_x
        self.speed = 2

    def update(self):
        # Beweeg heen en weer
        self.rect.x += self.direction * self.speed
        
        # Keer om als we de grenzen raken
        if self.rect.x < self.min_x:
            self.direction = 1
        elif self.rect.x > self.max_x:
            self.direction = -1


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