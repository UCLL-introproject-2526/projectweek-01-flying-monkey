import pygame
import os

def speel(SCREEN, pause_func=None):
    # ====================
    # INITIAL SETUP
    # ====================
    # Use the actual screen size so the background can fill the whole window
    WIDTH, HEIGHT = SCREEN.get_size()
    CLOCK = pygame.time.Clock()
    FONT = pygame.font.SysFont(None, 32)
    BIG_FONT = pygame.font.SysFont(None, 64)

    # ====================
    # ASSETS LADEN
    # ====================
    try:
        bg_original = pygame.image.load("assets/background.jpg").convert()
        # scale background to the actual screen size
        bg_img = pygame.transform.scale(bg_original, (WIDTH, HEIGHT))
    except:
        bg_img = None
        print("Kan background.jpg niet vinden.")

    try:
        monkey_original = pygame.image.load("assets/monkey.png").convert_alpha()
        player_img = pygame.transform.scale(monkey_original, (50, 60))
    except:
        player_img = None
        print("Kan monkey.png niet vinden.")

    # Castle and flag images
    try:
        castle_original = pygame.image.load("assets/castle.png").convert_alpha()
    except:
        castle_original = None
        # print optional: not necessary
    try:
        flag_original = pygame.image.load("assets/flag.png").convert_alpha()
    except:
        flag_original = None

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
    WHITE = (255, 255, 255)
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
    # pause_func: optional callback provided by main.py; when called it should
    # present a pause menu and return either "RESUME" or "MENU".

    camera_x = 0
    win = False
    game_over = False
    # flag animation state (plays once when reaching the castle)
    flag_animating = False
    flag_anim_time = 0.0
    flag_anim_duration = 3.0
    flag_anim_done = False
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
    # Make flag a bit wider so it's more visible
    flag = pygame.Rect(1750, HEIGHT - 250, 24, 200)

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
        nonlocal player, player_vel_y, score, coins, enemies, win, on_ground, camera_x, game_over
        nonlocal flag_animating, flag_anim_time, flag_anim_done
        player.x, player.y = 100, HEIGHT - 120
        player_vel_y = 0
        score = 0
        camera_x = 0
        win = False
        game_over = False
        flag_animating = False
        flag_anim_time = 0.0
        flag_anim_done = False
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
        nonlocal player_vel_y, game_over
        for e in enemies[:]:
            if player.colliderect(e["rect"]):
                if player_vel_y > 0 and player.bottom < e["rect"].centery:
                    enemies.remove(e)
                    player_vel_y = -10
                else:
                    # set game over instead of instantly resetting so we can show a death screen
                    game_over = True

    def check_coin_collisions_func():
        nonlocal score
        for c in coins[:]:
            if player.colliderect(c):
                coins.remove(c)
                score += 1

    def draw_world_func():
        # Achtergrond (full-screen)
        if bg_img:
            # Draw the background to fill the whole screen (no horizontal tilt/offset)
            SCREEN.blit(bg_img, (0, 0))
        else:
            SCREEN.fill(SKY_BLUE)

        # === AANGEPASTE PLATFORMS ===
        for plat in platforms:
            # Skip drawing the large ground platform (visual removed) while keeping other platforms
            # The original ground spans from x==0 and had a very large width (2000), so we detect
            # that case and don't draw it. This preserves gameplay/platform collisions but
            # removes the visible ground.
            if plat.x == 0 and plat.width >= 1000:
                continue
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

        # Flag & Castle (use images if available)
        # Castle (draw slightly bigger but keep world position)
        castle_draw_x = castle.x - camera_x
        if 'castle_original' in locals() and castle_original is not None:
            try:
                # Make the in-world castle 1.5x bigger for a grander appearance
                castle_scale = 1.5
                scale_w = int(castle.width * castle_scale)
                scale_h = int(castle.height * castle_scale)
                # Align base of scaled castle with original castle base
                castle_draw_y = castle.y - (scale_h - castle.height)
                castle_img = pygame.transform.scale(castle_original, (scale_w, scale_h))
                SCREEN.blit(castle_img, (castle_draw_x, castle_draw_y))
            except Exception:
                pygame.draw.rect(SCREEN, RED, (castle_draw_x, castle.y, castle.width, castle.height))
        else:
            pygame.draw.rect(SCREEN, RED, (castle_draw_x, castle.y, castle.width, castle.height))

        # Flag (drawn near the castle).
        # Hide the in-world flag until the overlay animation has run; this prevents
        # the flag appearing prematurely when the player approaches the castle.
        flag_draw_x = flag.x - camera_x
        # default end position (world coord)
        flag_end_y = flag.y
        # Only draw the in-world flag after the animation has completed
        if flag_anim_done and not flag_animating:
            flag_draw_y = flag_end_y
        else:
            flag_draw_y = None

        if flag_draw_y is not None:
            if 'flag_original' in locals() and flag_original is not None:
                try:
                    # scale flag to fit
                    flag_w = int(flag.width)
                    flag_h = int(flag.height)
                    flag_img = pygame.transform.scale(flag_original, (flag_w, flag_h))
                    SCREEN.blit(flag_img, (flag_draw_x, int(flag_draw_y)))
                except Exception:
                    pygame.draw.rect(SCREEN, GRAY, (flag_draw_x, flag_draw_y, flag.width, flag.height))
            else:
                pygame.draw.rect(SCREEN, GRAY, (flag_draw_x, flag_draw_y, flag.width, flag.height))

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
                # ESC: if in win state -> go to menu, else call pause_func if available
                if event.key == pygame.K_ESCAPE:
                    if win:
                        return "MENU"
                    else:
                        if pause_func:
                            res = pause_func(SCREEN)
                            if res == "MENU":
                                return "MENU"
                            # if RESUME, we simply continue the game loop
                # Restart after win
                if event.key == pygame.K_r and win:
                    reset_game()
                # Restart after death (Enter)
                if event.key == pygame.K_RETURN and game_over:
                    reset_game()
                # Jump (only when not in a win state or dead)
                if event.key == pygame.K_UP and on_ground and not win and not game_over:
                    player_vel_y = jump_power

        keys = pygame.key.get_pressed()

        # If the player is alive and has not won, update and draw the world
        if not win and not game_over:
            # Update movement/collisions
            move_player_func(keys)
            move_enemies_func()
            check_enemy_collisions_func()
            check_coin_collisions_func()

            # Only set win when player actually reaches the castle area (avoid false positives)
            # Require collision, horizontal proximity and that player is standing at castle level
            if (player.colliderect(castle)
                and player.x >= castle.x - 10
                and player.bottom >= castle.top - 5):
                win = True
                # start flag animation (plays in-world) if asset exists
                if flag_original is not None:
                    flag_animating = True
                    flag_anim_time = 0.0
                    flag_anim_done = False

            if not win:
                camera_x = player.x - WIDTH // 3
                camera_x = max(0, camera_x)

            # Draw world and entities
            draw_world_func()
            draw_enemies_func()
            
            if player_img:
                SCREEN.blit(player_img, (player.x - camera_x, player.y))
            else:
                pygame.draw.rect(SCREEN, (150, 100, 60), (player.x - camera_x, player.y, player.width, player.height))

            SCREEN.blit(FONT.render(f"Score: {score}", True, BLACK), (20, 20))

        # win/game_over handling continues below

        elif game_over:
            # Draw a death screen over the current frame
            if bg_img:
                SCREEN.blit(bg_img, (0, 0))
            else:
                SCREEN.fill(SKY_BLUE)
            text = BIG_FONT.render("YOU DIED", True, RED)
            restart_text = FONT.render("Press Enter to restart", True, BLACK)
            SCREEN.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 30))
            SCREEN.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 30))

        else:
            # Win state: keep the world/castle in place and animate only the flag
            if flag_animating and flag_original is not None:
                # update animation timer
                dt = CLOCK.get_time() / 1000.0
                flag_anim_time = min(flag_anim_time + dt, flag_anim_duration)
                progress = flag_anim_time / flag_anim_duration

                # Draw the normal world (so castle stays where it is)
                draw_world_func()
                draw_enemies_func()
                if player_img:
                    SCREEN.blit(player_img, (player.x - camera_x, player.y))
                else:
                    pygame.draw.rect(SCREEN, (150, 100, 60), (player.x - camera_x, player.y, player.width, player.height))
                SCREEN.blit(FONT.render(f"Score: {score}", True, BLACK), (20, 20))

                # Draw the flag as a screen-space overlay to the left of the castle
                try:
                    # scale flag to a reasonable size
                    flag_w = max(16, int(flag.width))
                    flag_h = max(16, int(flag.height * 0.6))
                    flag_img = pygame.transform.scale(flag_original, (flag_w, flag_h))

                    # pole x: left of the castle in screen coords
                    pole_x_screen = (castle.x - camera_x) - flag_w - 10

                    # start below the screen, end at 1/3 of the screen height
                    start_y_screen = HEIGHT + flag_h + 40
                    end_y_screen = HEIGHT // 3
                    cur_y_screen = start_y_screen + (end_y_screen - start_y_screen) * progress

                    SCREEN.blit(flag_img, (pole_x_screen, int(cur_y_screen)))
                except Exception:
                    # fallback: draw a simple rect in screen-space
                    pole_x_screen = (castle.x - camera_x) - flag.width - 10
                    start_y_screen = HEIGHT + flag.height + 40
                    end_y_screen = HEIGHT // 3
                    cur_y_screen = start_y_screen + (end_y_screen - start_y_screen) * progress
                    pygame.draw.rect(SCREEN, GRAY, (pole_x_screen, int(cur_y_screen), flag.width, flag.height))

                if progress >= 1.0:
                    flag_animating = False
                    flag_anim_done = True

            else:
                # show final win screen overlaid on the background
                if bg_img:
                    SCREEN.blit(bg_img, (0, 0))
                else:
                    SCREEN.fill(SKY_BLUE)
                text = BIG_FONT.render(f"YOU WIN! Score: {score}", True, WHITE)
                restart_text = FONT.render("Press R to play again", True, WHITE)
                SCREEN.blit(text, (WIDTH//2 - 150, HEIGHT//2 - 20))
                SCREEN.blit(restart_text, (WIDTH//2 - 110, HEIGHT//2 + 40))

        pygame.display.update()