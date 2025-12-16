import pygame
import os

def speel(SCREEN):
    # ====================
    # INITIAL SETUP
    # ====================
    WIDTH, HEIGHT = 800, 450
    CLOCK = pygame.time.Clock()
    FONT = pygame.font.SysFont(None, 32)
    BIG_FONT = pygame.font.SysFont(None, 64)

    # ====================
    # ASSETS LADEN
    # ====================
    try:
        bg_original = pygame.image.load("assets/background.jpg").convert()
        bg_img = pygame.transform.scale(bg_original, (WIDTH + 100, HEIGHT))
    except:
        bg_img = None
        print("Kan background.jpg niet vinden.")

    try:
        monkey_original = pygame.image.load("assets/ehcte.png").convert_alpha()
        player_img = pygame.transform.scale(monkey_original, (50, 60))
    except:
        player_img = None
        print("Kan monkey.png niet vinden.")

    enemy_imgs_loaded = False 
    try:
        mushroom_original = pygame.image.load("assets/mushroom.png").convert_alpha()
        enemy_img_left = pygame.transform.scale(mushroom_original, (65, 65))
        enemy_img_right = pygame.transform.flip(enemy_img_left, True, False)
        enemy_imgs_loaded = True
    except:
        print("Kan mushroom.png niet vinden.")

    # Grond/Platform afbeelding
    grond_img_loaded = False
    try:
        grond_original = pygame.image.load("assets/grond.png").convert_alpha()
        grond_img_loaded = True
    except:
        grond_original = None
        print("Kan grond.png niet vinden.")

    # ====================
    # KLEUREN
    # ====================
    SKY_BLUE = (135, 206, 235)
    GROUND = (17, 184, 2)      # De vulling van de blokken
    RED = (220, 50, 50)
    BLACK = (20, 20, 20)
    GRAY = (160, 160, 160)
    YELLOW = (255, 223, 0)
    GREEN = (0, 120, 0) 

    # ====================
    # GAME VARIABELEN (STATE)
    # ====================
    player = pygame.Rect(100, HEIGHT - 120, 40, 50)
    player_vel_y = 0
    speed = 5
    jump_power = -15
    gravity = 1
    on_ground = False

    camera_x = 0
    win = False
    score = 0
    
    platforms = [
        pygame.Rect(0, HEIGHT - 50, 2000, 50),
        pygame.Rect(300, HEIGHT - 150, 120, 20),
        pygame.Rect(520, HEIGHT - 220, 120, 20),
        pygame.Rect(800, HEIGHT - 170, 120, 20),
        pygame.Rect(650, HEIGHT - 100, 80, 20),
        pygame.Rect(900, HEIGHT - 250, 100, 20),
    ]

    castle = pygame.Rect(1800, HEIGHT - 200, 120, 150)
    flag = pygame.Rect(1750, HEIGHT - 250, 10, 200)

    coins_original = [
        pygame.Rect(660, HEIGHT - 140, 20, 20),
        pygame.Rect(910, HEIGHT - 290, 20, 20),
        pygame.Rect(930, HEIGHT - 290, 20, 20),
    ]
    coins = [c.copy() for c in coins_original]

    enemies_def = [
        {"rect": pygame.Rect(450, HEIGHT - 100, 50, 40), "dir": -1},
        {"rect": pygame.Rect(750, HEIGHT - 100, 50, 40), "dir": 1},
        {"rect": pygame.Rect(1100, HEIGHT - 100, 50, 40), "dir": -1},
        {"rect": pygame.Rect(820, HEIGHT - 100, 50, 40), "dir": -1},
        {"rect": pygame.Rect(990, HEIGHT - 100, 50, 40), "dir": -1},
    ]
    
    enemies = []
    for e in enemies_def:
        enemies.append({"rect": e["rect"].copy(), "dir": e["dir"]})


    # ====================
    # INTERNE FUNCTIES
    # ====================
    
    def reset_game():
        nonlocal player, player_vel_y, score, coins, enemies, win, on_ground, camera_x
        player.x, player.y = 100, HEIGHT - 120
        player_vel_y = 0
        score = 0
        camera_x = 0
        win = False
        on_ground = False
        coins = [c.copy() for c in coins_original]
        enemies = []
        for e in enemies_def:
            enemies.append({"rect": e["rect"].copy(), "dir": e["dir"]})

    def move_player_func(keys):
        nonlocal on_ground, player_vel_y, camera_x
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -speed
        if keys[pygame.K_RIGHT]:
            dx = speed
        player.x += dx
        player_vel_y += gravity
        player.y += player_vel_y

        on_ground = False
        for plat in platforms:
            if player.colliderect(plat) and player_vel_y >= 0:
                player.bottom = plat.top
                player_vel_y = 0
                on_ground = True

    def move_enemies_func():
        for e in enemies:
            e["rect"].x += e["dir"] * 2
            if e["rect"].x < 300: 
                e["dir"] = 1
            elif e["rect"].x > 1900:
                e["dir"] = -1

    def check_enemy_collisions_func():
        nonlocal player_vel_y
        for e in enemies[:]:
            if player.colliderect(e["rect"]):
                if player_vel_y > 0 and player.bottom < e["rect"].centery:
                    enemies.remove(e)
                    player_vel_y = -10
                else:
                    reset_game()

    def check_coin_collisions_func():
        nonlocal score
        for c in coins[:]:
            if player.colliderect(c):
                coins.remove(c)
                score += 1

    def draw_world_func():
        # Achtergrond
        if bg_img:
            tilt_offset = (player.x - WIDTH // 2) * 0.05
            tilt_offset = max(0, min(tilt_offset, 100)) 
            SCREEN.blit(bg_img, (-tilt_offset, 0))
        else:
            SCREEN.fill(SKY_BLUE)

        # === AANGEPASTE PLATFORMS ===
        for plat in platforms:
            # We definiëren de rechthoek die we gaan tekenen (rekening houdend met camera)
            draw_rect = (plat.x - camera_x, plat.y, plat.width, plat.height)
            
            # 1. Teken de binnenkant: gebruik afbeelding indien beschikbaar, anders kleur
            if grond_img_loaded and grond_original is not None:
                try:
                    img = pygame.transform.scale(grond_original, (plat.width, plat.height))
                    SCREEN.blit(img, (plat.x - camera_x, plat.y))
                except Exception:
                    pygame.draw.rect(SCREEN, GROUND, draw_rect)
            else:
                pygame.draw.rect(SCREEN, GROUND, draw_rect)
            
            # 2. Teken de "Gloeiende" Rode Rand
            # De 4 aan het einde is de dikte van de lijn

        # Coins
        for c in coins:
            pygame.draw.rect(SCREEN, YELLOW, (c.x - camera_x, c.y, c.width, c.height))

        # Flag & Castle
        pygame.draw.rect(SCREEN, GRAY, (flag.x - camera_x, flag.y, flag.width, flag.height))
        pygame.draw.rect(SCREEN, RED, (castle.x - camera_x, castle.y, castle.width, castle.height))

    def draw_enemies_func():
        for e in enemies:
            draw_x = e["rect"].x - camera_x
            draw_y = e["rect"].y
            if enemy_imgs_loaded:
                if e["dir"] == -1:
                    SCREEN.blit(enemy_img_left, (draw_x, draw_y))
                else:
                    SCREEN.blit(enemy_img_right, (draw_x, draw_y))
            else:
                pygame.draw.rect(SCREEN, GREEN, (draw_x, draw_y, e["rect"].width, e["rect"].height))


    # ====================
    # MAIN LOOP
    # ====================
    running = True
    while running:
        CLOCK.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "MENU"
                if event.key == pygame.K_UP and on_ground:
                    player_vel_y = jump_power
                if event.key == pygame.K_r and win:
                    reset_game()

        keys = pygame.key.get_pressed()

        if not win:
            move_player_func(keys)
            move_enemies_func()
            check_enemy_collisions_func()
            check_coin_collisions_func()

            if player.colliderect(castle):
                win = True

            camera_x = player.x - WIDTH // 3
            camera_x = max(0, camera_x)

            draw_world_func()
            draw_enemies_func()
            
            if player_img:
                SCREEN.blit(player_img, (player.x - camera_x, player.y))
            else:
                pygame.draw.rect(SCREEN, (150, 100, 60), (player.x - camera_x, player.y, player.width, player.height))

            SCREEN.blit(FONT.render(f"Score: {score}", True, BLACK), (20, 20))

        else:
            if bg_img:
                SCREEN.blit(bg_img, (0, 0))
            else:
                SCREEN.fill(SKY_BLUE)
            text = BIG_FONT.render(f"YOU WIN! Score: {score}", True, BLACK)
            restart_text = FONT.render("Press R to play again", True, BLACK)
            SCREEN.blit(text, (WIDTH//2 - 150, HEIGHT//2 - 20))
            SCREEN.blit(restart_text, (WIDTH//2 - 110, HEIGHT//2 + 40))

        pygame.display.update()