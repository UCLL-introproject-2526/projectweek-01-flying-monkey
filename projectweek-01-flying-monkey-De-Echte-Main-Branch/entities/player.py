import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, asset_manager):
        super().__init__()
        self.am = asset_manager # We slaan de asset manager op
        
        # Start image (fallback vierkant als plaatje mist)
        self.image = self.am.get("idle")
        if not self.image:
            self.image = pygame.Surface((60, 60))
            self.image.fill((255, 0, 0))
            
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Status variabelen
        self.direction = 1 # 1 = rechts, -1 = links
        self.walk_frame = 0
        self.width = 60
        self.height = 60

    def update_visuals(self, vel_y, on_ground, direction, walk_frame, is_moving):
        """Update het plaatje van de speler gebaseerd op wat hij doet"""
        self.direction = direction
        self.walk_frame = walk_frame

        # 1. Springen
        if not on_ground:
            if self.direction == 1 and self.am.get("jump_right"):
                new_image = self.am.get("jump_right")
            elif self.direction == -1 and self.am.get("jump_left"):
                new_image = self.am.get("jump_left")
            else:
                new_image = self.am.get("idle")
        # 2. Lopen (alleen als daadwerkelijk moving)
        elif is_moving and on_ground and self.am.get("walk_right"):
            if self.direction == 1:
                idx = self.walk_frame % 2
                new_image = self.am.get("walk_right")[idx]
            elif self.direction == -1:
                idx = self.walk_frame % 2
                new_image = self.am.get("walk_left")[idx]
            else:
                new_image = self.am.get("idle")
        else:
            # Idle monkey.png faces last direction
            idle_img = self.am.get("idle")
            if self.direction == -1 and idle_img:
                new_image = pygame.transform.flip(idle_img, True, False)
            else:
                new_image = idle_img

        if new_image:
            self.image = new_image

    def draw(self, screen, camera_x):
        """Teken de speler rekening houdend met de camera"""
        draw_pos = (self.rect.x - camera_x, self.rect.y)
        # Correctie als sprites verschillende hoogtes hebben (voorkomt zweven)
        screen.blit(self.image, draw_pos)