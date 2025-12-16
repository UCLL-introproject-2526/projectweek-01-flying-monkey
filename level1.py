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
        # Achtergrond
        bg_original = pygame.image.load("assets/background.jpg").convert()
        bg_img = pygame.transform.scale(bg_original, (WIDTH + 100, HEIGHT))
    except:
        bg_img = None
        print("Kan background.jpg niet vinden.")

    try:
        # Speler
        monkey_original = pygame.image.load("assets/monkey.png").convert_alpha()
        player_img = pygame.transform.scale(monkey_original, (40, 50))
    except:
        player_img = None
        print("Kan monkey.png niet vinden.")

    # NIEUW: Mushroom vijand laden EN spiegelen
    enemy_imgs_loaded = False # Een vlag om te weten of het laden gelukt is
    try:
        mushroom_original = pygame.image.load("assets/mushroom.png").convert_alpha()
        # 1. Het normale plaatje (kijkt naar links)
        enemy_img_left = pygame.transform.scale(mushroom_original, (65, 65))
        # 2. Het gespiegelde plaatje (kijkt naar rechts). True voor horizontaal flippen.
        enemy_img_right = pygame.transform.flip(enemy_img_left, True, False)
        enemy_imgs_loaded = True
    except:
        print("Kan mushroom.png niet vinden (gebruik groen blokje als fallback).")

    # ====================
    # KLEUREN
    # ====================
    SKY_BLUE = (135, 206, 235)
    GROUND = (50, 50, 50)
    RED = (220, 50, 50)
    BLACK = (20, 20, 20)
    GRAY = (160, 160, 160)
    YELLOW = (255, 223, 0)
    GREEN = (0, 120, 0) # Kleur voor vijand als plaatje mist

    # ====================
    # GAME VARIABELEN (STATE)
    # ====================
    # Speler
    player = pygame.Rect(100, HEIGHT - 120, 40, 50)
    player_vel_y = 0
    speed = 5
    jump_power = -15
    gravity = 1
    on_ground = False

    # Camera
    camera_x = 0

    # Game status
    win = False
    score = 0
    
    # Wereld Objecten (Platforms)
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

    # Coins
    coins_original = [
        pygame.Rect(660, HEIGHT - 140, 20, 20),
        pygame.Rect(910, HEIGHT - 290, 20, 20),
        pygame.Rect(930, HEIGHT - 290, 20, 20),
    ]
    coins = [c.copy() for c in coins_original]

    # Enemies (3 stuks)
    # dir: -1 is naar links, 1 is naar rechts
    enemies_def = [
        {"rect": pygame.Rect(450, HEIGHT - 100, 50, 40), "dir": -1},  # Vijand 1
        {"rect": pygame.Rect(750, HEIGHT - 100, 50, 40), "dir": 1},   # Vijand 2
        {"rect": pygame.Rect(1100, HEIGHT - 100, 50, 40), "dir": -1}, # Vijand 3
        {"rect": pygame.Rect(820, HEIGHT - 100, 50, 40), "dir": -1}, # Vijand 3
        {"rect": pygame.Rect(990, HEIGHT - 100, 50, 40), "dir": -1}, # Vijand 3
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

        # Reset coins
        coins = [c.copy() for c in coins_original]

        # Reset enemies
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

        # gravity
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
            # Beweeg snelheid * richting
            e["rect"].x += e["dir"] * 2
            
            # Vijanden draaien om als ze te ver lopen (simpele AI)
            if e["rect"].x < 300: # Iets eerder omdraaien links
                e["dir"] = 1
            elif e["rect"].x > 1900:
                e["dir"] = -1

    def check_enemy_collisions_func():
        nonlocal player_vel_y
        
        for e in enemies[:]:
            if player.colliderect(e["rect"]):
                # MARIO LOGICA: Spring je op zijn kop?
                if player_vel_y > 0 and player.bottom < e["rect"].centery:
                    enemies.remove(e)
                    player_vel_y = -10 # Sprongetje
                else:
                    # Anders: Game Over
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

        # Platforms
        for plat in platforms:
            pygame.draw.rect(SCREEN, GROUND, (plat.x - camera_x, plat.y, plat.width, plat.height))

        # Coins
        for c in coins:
            pygame.draw.rect(SCREEN, YELLOW, (c.x - camera_x, c.y, c.width, c.height))

        # Flag & Castle
        pygame.draw.rect(SCREEN, GRAY, (flag.x - camera_x, flag.y, flag.width, flag.height))
        pygame.draw.rect(SCREEN, RED, (castle.x - camera_x, castle.y, castle.width, castle.height))

    # NIEUW: Aangepaste tekenfunctie voor vijanden
    def draw_enemies_func():
        for e in enemies:
            # Bereken positie ten opzichte van camera
            draw_x = e["rect"].x - camera_x
            draw_y = e["rect"].y
            
            # Als de afbeeldingen succesvol geladen zijn
            if enemy_imgs_loaded:
                # Check de richting
                if e["dir"] == -1:
                    # Loopt naar links -> teken het linker plaatje
                    SCREEN.blit(enemy_img_left, (draw_x, draw_y))
                else:
                    # Loopt naar rechts -> teken het rechter (gespiegelde) plaatje
                    SCREEN.blit(enemy_img_right, (draw_x, draw_y))
            else:
                # Fallback: groen vierkant als er geen plaatje is
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
                
                # Restart knop
                if event.key == pygame.K_r and win:
                    reset_game()

        keys = pygame.key.get_pressed()

        if not win:
            move_player_func(keys)
            move_enemies_func()
            check_enemy_collisions_func()
            check_coin_collisions_func()

            # Win check
            if player.colliderect(castle):
                win = True

            # Camera logic
            camera_x = player.x - WIDTH // 3
            camera_x = max(0, camera_x)

            # Tekenen
            draw_world_func()
            draw_enemies_func()
            
            # Player tekenen
            if player_img:
                SCREEN.blit(player_img, (player.x - camera_x, player.y))
            else:
                pygame.draw.rect(SCREEN, (150, 100, 60), (player.x - camera_x, player.y, player.width, player.height))

            SCREEN.blit(FONT.render(f"Score: {score}", True, BLACK), (20, 20))

        else:
            # Win scherm
            if bg_img:
                SCREEN.blit(bg_img, (0, 0))
            else:
                SCREEN.fill(SKY_BLUE)
                
            text = BIG_FONT.render(f"YOU WIN! Score: {score}", True, BLACK)
            restart_text = FONT.render("Press R to play again", True, BLACK)
            
            SCREEN.blit(text, (WIDTH//2 - 150, HEIGHT//2 - 20))
            SCREEN.blit(restart_text, (WIDTH//2 - 110, HEIGHT//2 + 40))

        pygame.display.update()