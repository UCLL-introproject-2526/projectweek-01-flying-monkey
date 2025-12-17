import pygame
import sys
import level1  # We importeren je level bestanden
import level2

# Setup
pygame.init()
#Een liedje toevoegen
pygame.mixer.init()

pygame.mixer.music.load("projectweek-01-flying-monkey//assets//songMario.mp3")
WIDTH, HEIGHT = 800, 450
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Monkey Game Menu")
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 50)
SMALL_FONT = pygame.font.SysFont(None, 30)

# Kleuren voor menu
BG_COLOR = (30, 30, 50)
WHITE = (255, 255, 255)
HOVER_COLOR = (100, 100, 150)

def draw_text_centered(text, font, y, color):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(WIDTH // 2, y))
    SCREEN.blit(surface, rect)

# ====================
# MENU LOOP
# ====================
while True:
    #play song when game starts
    pygame.mixer.music.play()
    SCREEN.fill(BG_COLOR)
    
    # Tekst op het scherm
    draw_text_centered("MONKEY ADVENTURE", FONT, 100, WHITE)
    draw_text_centered("Druk op 1 voor Level 1 (Simpel)", SMALL_FONT, 200, WHITE)
    draw_text_centered("Druk op 2 voor Level 2 (Survival)", SMALL_FONT, 250, WHITE)
    draw_text_centered("Druk op Q om te stoppen", SMALL_FONT, 350, WHITE)

    pygame.display.update()
    CLOCK.tick(60)

    # Input checken
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                sys.exit()
            
            # Start Level 1
            if event.key == pygame.K_1:
                # We roepen de functie 'speel' aan uit het bestand 'level1'
                # We geven 'SCREEN' mee zodat hij op hetzelfde scherm tekent
                resultaat = level1.speel(SCREEN)
                
                # Als level 'QUIT' terugstuurt (kruisje geklikt), stoppen we alles
                if resultaat == "QUIT":
                    pygame.quit()
                    sys.exit()
            
            # Start Level 2
            if event.key == pygame.K_2:
                resultaat = level2.speel(SCREEN)
                if resultaat == "QUIT":
                    pygame.quit()
                    sys.exit()