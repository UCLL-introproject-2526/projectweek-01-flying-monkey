import pygame
import random

# Hoofdfunctie voor het spelen van Level 2
def speel(SCREEN):
    # Schermgrootte
    WIDTH, HEIGHT = 800, 450

    # Clock regelt de FPS (frames per seconde)
    CLOCK = pygame.time.Clock()

    # Lettertypes voor tekst
    FONT = pygame.font.SysFont(None, 32)
    BIG_FONT = pygame.font.SysFont(None, 64)

    # ====================
    # 1. AFBEELDINGEN LADEN
    # ====================

    # Achtergrond laden
    try:
        bg_original = pygame.image.load("assets/background.jpg")
        bg_img = pygame.transform.scale(bg_original, (WIDTH, HEIGHT))
    except:
        # Als laden mislukt, gebruiken we een effen kleur
        bg_img = None  

    # Speler (aap)
    original_image = pygame.image.load("assets/monkey.png")
    player_img = pygame.transform.scale(original_image, (40, 50))

    # Vijand (vallend mes)
    knife_original = pygame.image.load("assets/knifes.png")
    knife_img = pygame.transform.scale(knife_original, (50, 100))

    # ====================
    # KLEUREN (RGB)
    # ====================
    SKY = (135, 206, 235)
    GROUND_COLOR = (110, 180, 90)
    RED = (220, 50, 50)
    BLACK = (20, 20, 20)
    GRAY = (160, 160, 160)

    # ====================
    # BASIS VARIABELEN
    # ====================

    # Speler rechthoek (positie + grootte)
    player = pygame.Rect(100, HEIGHT - 120, 32, 45)

    # Verticale snelheid van de speler
    player_vel_y = 0

    # Check of speler op de grond staat
    on_ground = False

    # Camera-offset (scrolling)
    camera_x = 0

    # Spelstatus
    game_over = False
    win = False

    # Lijst met vijanden (messen)
    enemies = []

    # ====================
    # LEVEL GENEREREN (PLATFORMS)
    # ====================

    # Startplatform
    platforms = [pygame.Rect(0, HEIGHT - 50, 500, 50)]
    current_x = 500

    last_platform_y = HEIGHT - 50

    # SPRONG LIMIETEN (afgestemd op jouw speler)
    MAX_JUMP_X = 120              # maximale horizontale sprong
    MAX_JUMP_Y = 120              # maximale verticale sprong omhoog
    HALF_SCREEN_Y = HEIGHT // 2   # hoger dan dit mag NIET

    while current_x < 3000:
        # Horizontale afstand tussen platforms
        gap = random.randint(40, MAX_JUMP_X)

        # Breedte van platform
        w = random.randint(120, 250)

        # Verticale grenzen gebaseerd op vorige platform
        min_y = last_platform_y - MAX_JUMP_Y
        max_y = last_platform_y + 40  # lager is altijd oké

        # 🔒 HARD LIMITS
        min_y = max(HALF_SCREEN_Y, min_y)          # nooit hoger dan halve scherm
        max_y = min(HEIGHT - 60, max_y)            # nooit onder de grond

        # Definitieve hoogte
        h = random.randint(min_y, max_y)

        # Platform toevoegen
        current_x += gap
        platforms.append(pygame.Rect(current_x, h, w, 20))

        # Vorige platform onthouden
        last_platform_y = h
        current_x += w


    # Kasteel aan het einde van het level
    castle_x = current_x + 100
    platforms.append(pygame.Rect(castle_x - 100, HEIGHT - 50, 500, 50))
    castle = pygame.Rect(castle_x, HEIGHT - 200, 120, 150)

    # Vlag bij het kasteel
    flag = pygame.Rect(castle_x - 50, HEIGHT - 250, 10, 200)

    # ====================
    # FYSICA INSTELLINGEN
    # ====================
    speed = 5           # loopsnelheid
    jump_power = -15    # sprongkracht
    gravity = 1         # zwaartekracht

    # ====================
    # GAME LOOP
    # ====================
    running = True
    while running:
        CLOCK.tick(60)  # max 60 FPS

        # ====================
        # ACHTERGROND TEKENEN
        # ====================
        if bg_img:
            SCREEN.blit(bg_img, (0, 0))
        else:
            SCREEN.fill(SKY)

        # ====================
        # EVENTS (toetsen, sluiten)
        # ====================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            if event.type == pygame.KEYDOWN:
                # Terug naar menu
                if event.key == pygame.K_ESCAPE:
                    return "MENU"

                # Springen
                if event.key == pygame.K_UP and on_ground and not game_over and not win:
                    player_vel_y = jump_power

                # Restart bij game over of win
                if event.key == pygame.K_r and (game_over or win):
                    return speel(SCREEN)

        keys = pygame.key.get_pressed()

        # ====================
        # GAME LOGICA
        # ====================
        if not win and not game_over:

            # Beweging links/rechts
            if keys[pygame.K_LEFT]:
                player.x -= speed
            if keys[pygame.K_RIGHT]:
                player.x += speed

            # Zwaartekracht toepassen
            player_vel_y += gravity
            player.y += player_vel_y

            # Check botsing met platforms
            on_ground = False
            for plat in platforms:
                if player.colliderect(plat) and player_vel_y >= 0:
                    if player.bottom <= plat.top + 20:
                        player.bottom = plat.top
                        player_vel_y = 0
                        on_ground = True

            # Val buiten scherm → game over
            if player.y > HEIGHT:
                game_over = True

            # Raak kasteel → win
            if player.colliderect(castle):
                win = True

            # ====================
            # MESSEN (VIJANDEN)
            # ====================

            # Nieuwe messen spawnen
            if len(enemies) < 12:                                                       #MAXIMAAL
                if len(enemies) < 4 or random.randint(0, 100) < 2:                      #WANNEER
                    spawn_x = random.randint(int(camera_x), int(camera_x + WIDTH))      #WAAR
                    enemies.append(pygame.Rect(spawn_x, -100, 30, 80))                 #x = spawn_x
                                                                                        #y = -100 → boven het scherm
                                                                                        #50x100 = grootte mes

            # Vijanden laten vallen
            for enemy in enemies[:]:
                enemy.y += 5                            # valsnelheid
                if player.colliderect(enemy):
                    game_over = True
                if enemy.y > HEIGHT:
                    enemies.remove(enemy)

            # ====================
            # CAMERA LOGICA
            # ====================
            target = player.x - WIDTH // 3
            if target < 0:
                target = 0
            camera_x = target

            # ====================
            # TEKENEN VAN OBJECTEN
            # ====================

            # Platforms
            for plat in platforms:
                pygame.draw.rect(
                    SCREEN,
                    GROUND_COLOR,
                    (plat.x - camera_x, plat.y, plat.width, plat.height)
                )

            # Vlag en kasteel
            pygame.draw.rect(SCREEN, GRAY, (flag.x - camera_x, flag.y, flag.width, flag.height))
            pygame.draw.rect(SCREEN, RED, (castle.x - camera_x, castle.y, castle.width, castle.height))

            # Vijanden tekenen
            for e in enemies:
                SCREEN.blit(knife_img, (e.x - camera_x, e.y))

            # Speler tekenen
            SCREEN.blit(player_img, (player.x - camera_x, player.y))

            # Leveltekst
            SCREEN.blit(
                FONT.render("Level 2 - Survival (Pas op voor messen!)", True, BLACK),
                (20, 20)
            )

        # ====================
        # GAME OVER SCHERM
        # ====================
        elif game_over:
            SCREEN.fill(BLACK)
            SCREEN.blit(BIG_FONT.render("GAME OVER", True, RED), (250, 200))
            SCREEN.blit(FONT.render("Druk R voor retry, ESC voor menu", True, SKY), (220, 260))

        # ====================
        # WIN SCHERM
        # ====================
        else:
            if bg_img:
                SCREEN.blit(bg_img, (0, 0))
            else:
                SCREEN.fill(SKY)

            SCREEN.blit(BIG_FONT.render("GEWONNEN!", True, BLACK), (250, 200))
            SCREEN.blit(FONT.render("Druk R voor retry, ESC voor menu", True, BLACK), (220, 260))

        # Scherm verversen
        pygame.display.update()
