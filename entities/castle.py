import pygame

class Castle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, asset_manager):
        super().__init__()
        self.am = asset_manager
        self.rect = pygame.Rect(x, y, width, height)
        self.win_state = False
        self.anim_progress = 0.0

    def draw(self, screen, camera_x, screen_height):
        castle_img = self.am.get("castle")
        
        # Teken Kasteel
        if castle_img:
            scale_factor = 1.5
            w = int(self.rect.width * scale_factor)
            h = int(self.rect.height * scale_factor)
            # Kasteel staat iets hoger of breder, pas positie aan
            draw_y = self.rect.bottom - h
            screen.blit(pygame.transform.scale(castle_img, (w, h)), (self.rect.x - camera_x, draw_y))
        else:
            pygame.draw.rect(screen, (200, 50, 50), (self.rect.x - camera_x, self.rect.y, 120, 150))

        # Teken Vlag Animatie als we gewonnen hebben
        if self.win_state and self.am.get("flag"):
            self._draw_flag(screen, camera_x, screen_height)

    def _draw_flag(self, screen, camera_x, screen_height):
        # Haal flag image op
        flag_img = self.am.get("flag")
        
        # Bereken afmetingen
        flag_w = int(self.rect.width * 2) # vlag is breed
        flag_h = int(self.rect.height * 0.7)
        img = pygame.transform.scale(flag_img, (flag_w, flag_h))
        
        # Bereken animatie positie
        start_y = screen_height + 50
        end_y = self.rect.top - 50
        current_y = start_y + (end_y - start_y) * self.anim_progress
        
        pole_x = (self.rect.x - camera_x) - 30
        
        # Teken paal en vlag
        pygame.draw.rect(screen, (100, 100, 100), (pole_x, current_y, 5, 300))
        screen.blit(img, (pole_x, current_y))

    def update_animation(self, speed=0.01):
        if self.win_state and self.anim_progress < 1.0:
            self.anim_progress += speed
            if self.anim_progress > 1.0:
                self.anim_progress = 1.0
            return True # Animatie is nog bezig
        return False # Animatie klaar of niet gestart