import pygame

class Castle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, asset_manager, sfx_on=True):
        super().__init__()
        self.am = asset_manager
        self.rect = pygame.Rect(x, y, width, height)
        self.win_state = False
        self.anim_progress = 0.0
        self.sfx_on = sfx_on

    def draw(self, screen, camera_x, screen_height):
        castle_img = self.am.get("castle")
        # ...existing code...
        if castle_img:
            scale_factor = 1.5
            w = int(self.rect.width * scale_factor)
            h = int(self.rect.height * scale_factor)
            draw_x = self.rect.x - camera_x
            draw_y = self.rect.bottom - h
            screen.blit(pygame.transform.scale(castle_img, (w, h)), (draw_x, draw_y))
        else:
            pygame.draw.rect(screen, (200, 50, 50), (self.rect.x - camera_x, self.rect.bottom - self.rect.height, 120, 150))

        # Teken altijd de paal, vlag alleen als win_state
        pole_x = (self.rect.x - camera_x) - 30
        pole_y = self.rect.top - 50
        pole_height = 300
        pygame.draw.rect(screen, (100, 100, 100), (pole_x, pole_y, 5, pole_height))

        # Teken Vlag Animatie als we gewonnen hebben
        if self.win_state and self.am.get("flag"):
            self._draw_flag(screen, camera_x, screen_height, pole_x, pole_y)

    def _draw_flag(self, screen, camera_x, screen_height, pole_x, pole_y):
        # Haal flag image op
        flag_img = self.am.get("flag")
        flag_w = int(self.rect.width)
        flag_h = int(self.rect.height * 0.35)
        img = pygame.transform.scale(flag_img, (flag_w, flag_h))
        # Animatie: vlag komt van onder het scherm naar boven
        start_y = screen_height + flag_h
        end_y = pole_y
        # anim_progress van 0 tot 1 over 4 seconden
        current_y = start_y + (end_y - start_y) * self.anim_progress
        screen.blit(img, (pole_x, current_y))

    def update_animation(self):
        # 4 seconden animatie
        if self.win_state:
            if not hasattr(self, 'anim_start_time'):
                self.anim_start_time = pygame.time.get_ticks()
                # Play win sound only once and only if sfx_on is True
                win_sound = self.am.get("win_sound")
                if win_sound and self.sfx_on:
                    try:
                        pygame.mixer.music.load(win_sound)
                        pygame.mixer.music.play()
                    except:
                        pass
            elapsed = (pygame.time.get_ticks() - self.anim_start_time) / 1000.0
            self.anim_progress = min(elapsed / 4.0, 1.0)
            return self.anim_progress < 1.0
        return False