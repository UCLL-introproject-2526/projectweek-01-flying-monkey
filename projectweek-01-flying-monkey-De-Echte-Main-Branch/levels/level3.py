import pygame

def speel(screen, pause_menu, assets, sfx_on):
    # Placeholder for Level 3 logic
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    result = pause_menu(screen)
                    if result == "MENU":
                        return "MENU"
                    elif result == "RESUME":
                        continue
        screen.fill((50, 50, 100))
        font = pygame.font.SysFont(None, 120)
        text = font.render("Level 3 - Placeholder", True, (255,255,255))
        screen.blit(text, (screen.get_width()//2 - text.get_width()//2, screen.get_height()//2 - text.get_height()//2))
        pygame.display.update()
        pygame.time.Clock().tick(60)
    return "MENU"
