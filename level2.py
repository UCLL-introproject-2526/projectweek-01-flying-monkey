import pygame
import random

def speel(SCREEN, pause_func=None):
    WIDTH, HEIGHT = 800, 450
    CLOCK = pygame.time.Clock()
    FONT = pygame.font.SysFont(None, 32)
    BIG_FONT = pygame.font.SysFont(None, 64)

    # 1. AFBEELDINGEN LADEN
    try:
        bg_original = pygame.image.load("assets/BACKKKground.jpg")
        bg_img = pygame.transform.scale(bg_original, (WIDTH, HEIGHT))
    except:
        bg_img = None 

    try:
        platform_original = pygame.image.load("assets/aaagrond.png")
    except:
        platform_original = None

    original_image = pygame.image.load("assets/monkey.png")
    player_img = pygame.transform.scale(original_image, (40, 50))

    knife_original = pygame.image.load("assets/knifes.png")
    knife_img = pygame.transform.scale(knife_original, (50, 100))

    # KLEUREN
    SKY = (135, 206, 235)
    GROUND_COLOR = (110, 180, 90)
    RED = (220, 50, 50)
    BLACK = (20, 20, 20)
    GRAY = (160, 160, 160)

    # SETUP VARIABELEN
    player = pygame.Rect(100, HEIGHT - 120, 40, 50)
    player_vel_y = 0
    on_ground = False
    camera_x = 0
    game_over = False
    win = False
    enemies = []
    
    # ==========================================
    # LEVEL GENEREREN (VERBETERDE VERSIE)
    # ==========================================
    platforms = [pygame.Rect(0, HEIGHT - 50, 500, 50)]
    current_x = 500
    
    # We onthouden de hoogte van het laatste platform om de volgende te berekenen
    last_platform_y = HEIGHT - 50 

    while current_x < 3000:
        # 1. Bepaal afstand (Gap)
        # Iets kleiner dan 150 om veilig te zijn
        gap = random.randint(50, 130) 
        
        # 2. Bepaal breedte
        w = random.randint(100, 300)

        # 3. Bepaal hoogte (Relatief aan vorig platform)
        # Standaard mag je ~100px omhoog springen
        max_jump_up = 100 

        # MAAR: Als de sprong ver is, mag hij minder hoog zijn (natuurkunde)
        if gap > 90:
            max_jump_up = 60  
        if gap > 110:
            max_jump_up = 20 # Bijna vlak blijven bij verre sprong

        # Bereken de limieten voor de Y-positie
        # (Let op: min_y is het hoogste punt op het scherm, want Y=0 is boven)
        min_y = last_platform_y - max_jump_up  
        max_y = last_platform_y + 100          # Naar beneden springen is makkelijk

        # Zorg dat platforms niet buiten beeld gaan (Plafond & Vloer)
        if min_y < 100: min_y = 100             # Niet te hoog (plafond)
        if max_y > HEIGHT - 50: max_y = HEIGHT - 50 # Niet te laag (vloer)
        
        # Veiligheidscheck: als min per ongeluk groter is dan max, draai ze om
        if min_y > max_y:
            min_y = max_y - 20

        # Kies de definitieve hoogte
        h = random.randint(min_y, max_y)

        # Toevoegen en updaten
        current_x += gap
        platforms.append(pygame.Rect(current_x, h, w, 20))
        current_x += w
        last_platform_y = h  # Onthoud deze hoogte voor de volgende ronde!
    
    # Kasteel plaatsen
    castle_x = current_x + 100
    platforms.append(pygame.Rect(castle_x - 100, HEIGHT - 50, 500, 50))
    castle = pygame.Rect(castle_x, HEIGHT - 200, 120, 150)
    flag = pygame.Rect(castle_x - 50, HEIGHT - 250, 10, 200)

    # Fysica
    speed = 5
    jump_power = -15
    gravity = 1

    # ====================
    # GAME LOOP LEVEL 2
    # ====================
    running = True
    while running:
        CLOCK.tick(60)

        if bg_img:
            SCREEN.blit(bg_img, (0, 0))
        else:
            SCREEN.fill(SKY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if pause_func and not (game_over or win):
                        res = pause_func(SCREEN)
                        if res == "MENU":
                            return "MENU"
                    else:
                        return "MENU"
                if event.key == pygame.K_UP and on_ground and not game_over and not win:
                    player_vel_y = jump_power
                
                if event.key == pygame.K_r and (game_over or win):
                    return speel(SCREEN, pause_func)
                if event.key == pygame.K_RETURN and game_over:
                    return speel(SCREEN, pause_func)

        keys = pygame.key.get_pressed()

        if not win and not game_over:
            if keys[pygame.K_LEFT]: player.x -= speed
            if keys[pygame.K_RIGHT]: player.x += speed
            player_vel_y += gravity
            player.y += player_vel_y

            on_ground = False
            for plat in platforms:
                if player.colliderect(plat) and player_vel_y >= 0:
                    if player.bottom <= plat.top + 20:
                        player.bottom = plat.top
                        player_vel_y = 0
                        on_ground = True
            
            if player.y > HEIGHT: game_over = True
            if player.colliderect(castle): win = True

            # Messen Logic
            if len(enemies) < 17:
                if len(enemies) < 4 or random.randint(0, 100) < 2:
                    spawn_x = random.randint(int(camera_x), int(camera_x + WIDTH))
                    enemies.append(pygame.Rect(spawn_x, -100, 37, 70))
            
            for enemy in enemies[:]:
                enemy.y += 7                        #valsnelheid
                if player.colliderect(enemy): game_over = True
                if enemy.y > HEIGHT: enemies.remove(enemy)

            # Camera logic
            target = player.x - WIDTH // 3
            if target < 0: target = 0
            camera_x = target

            # Tekenen
            # Platforms tekenen
            for plat in platforms:
                if platform_original:
                    # We schalen het plaatje naar de breedte/hoogte van DIT specifieke platform
                    # (want elk platform is anders van grootte)
                    scaled_plat = pygame.transform.scale(platform_original, (plat.width, plat.height))
                    SCREEN.blit(scaled_plat, (plat.x - camera_x, plat.y))
                else:
                    # Fallback: als plaatje niet geladen is, teken groen blok
                    pygame.draw.rect(SCREEN, GROUND_COLOR, (plat.x - camera_x, plat.y, plat.width, plat.height))
            
            pygame.draw.rect(SCREEN, GRAY, (flag.x - camera_x, flag.y, flag.width, flag.height))
            pygame.draw.rect(SCREEN, RED, (castle.x - camera_x, castle.y, castle.width, castle.height))
            
            for e in enemies:
                SCREEN.blit(knife_img, (e.x - camera_x, e.y))
            
            SCREEN.blit(player_img, (player.x - camera_x, player.y))
            SCREEN.blit(FONT.render("Level 2 - Survival", True, BLACK), (20, 20))

        elif game_over:
            SCREEN.fill(BLACK)
            SCREEN.blit(BIG_FONT.render("YOU DIED", True, RED), (250, 200))
            SCREEN.blit(FONT.render("Press Enter to restart", True, SKY), (220, 260))
        else:
            if bg_img: SCREEN.blit(bg_img, (0, 0))
            else: SCREEN.fill(SKY)
            SCREEN.blit(BIG_FONT.render("GEWONNEN!", True, BLACK), (250, 200))
            SCREEN.blit(FONT.render("Druk R voor retry", True, BLACK), (220, 260))

        pygame.display.update()