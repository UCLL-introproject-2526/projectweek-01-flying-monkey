import pygame
import os
import math

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Shortcut to assets folder
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

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
        # make monkey a bit wider (idle)
        player_idle_img = pygame.transform.scale(monkey_original, (60, 60))
        # try to load walking frames (left-arm-up / right-arm-up)
        try:
            monkey_lau = pygame.image.load("assets/monkey_lau.png").convert_alpha()
        except Exception:
            monkey_lau = None
        try:
            monkey_rau = pygame.image.load("assets/monkey_rau.png").convert_alpha()
        except Exception:
            monkey_rau = None
        # scale frames if available
        player_walk_frames_right = []
        player_walk_frames_left = []
        if monkey_rau is not None and monkey_lau is not None:
            f0 = pygame.transform.scale(monkey_rau, (60, 60))
            f1 = pygame.transform.scale(monkey_lau, (60, 60))
            player_walk_frames_right = [f0, f1]
            # left-facing frames are flipped
            player_walk_frames_left = [pygame.transform.flip(f, True, False) for f in player_walk_frames_right]
        # create left-facing idle frame
        try:
            player_idle_left = pygame.transform.flip(player_idle_img, True, False)
        except Exception:
            player_idle_left = None
        # jumping frame (arms up) if available
        try:
            monkey_jumping = pygame.image.load("assets/monkey_jumping.png").convert_alpha()
            player_jump_right = pygame.transform.scale(monkey_jumping, (60, 60))
            player_jump_left = pygame.transform.flip(player_jump_right, True, False)
        except Exception:
            player_jump_right = None
            player_jump_left = None
        # keep backward-compatible name
        player_img = player_idle_img
    except:
        player_img = None
        player_idle_img = None
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

    # coin image (optional)
    try:
        coin_original = pygame.image.load("assets/coin.png").convert_alpha()
    except Exception:
        coin_original = None

    # wood image for small platforms (optional)
    try:
        wood_original = pygame.image.load("assets/wood.jpg").convert_alpha()
    except Exception:
        wood_original = None

    # Grond/Platform afbeelding (prefer new ground.jpg, fallback to grond.png)
    grond_img_loaded = False
    try:
        try:
            grond_original = pygame.image.load("assets/ground.jpg").convert_alpha()
        except Exception:
            grond_original = pygame.image.load("assets/grond.png").convert_alpha()
        grond_img_loaded = True
    except:
        grond_original = None
        print("Kan ground/grond image niet vinden.")

    # ====================
    # AUDIO (win sound)
    # ====================
    win_sound = None
    coin_sound = None
    enemy_die_sound = None
    try:
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception:
                pass
        win_sound_path = os.path.join("assets", "Sounds", "VSE.mp3")
        if os.path.exists(win_sound_path):
            try:
                win_sound = pygame.mixer.Sound(win_sound_path)
            except Exception:
                try:
                    pygame.mixer.music.load(win_sound_path)
                except Exception:
                    win_sound = None
        else:
            win_sound = None
    except Exception:
        win_sound = None

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        coin_path = os.path.join("assets", "sounds", "coin_sound.mp3")
        if os.path.exists(coin_path):
            coin_sound = pygame.mixer.Sound(coin_path)

        enemy_die_path = os.path.join("assets", "sounds", "roblox_oof.mp3")
        if os.path.exists(enemy_die_path):
            enemy_die_sound = pygame.mixer.Sound(enemy_die_path)

    except Exception as e:
        print("Sound loading error:", e)

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
    # widen the player's collision rect to match the wider sprite
    player = pygame.Rect(100, HEIGHT - 100, 60, 60)
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
    # player facing direction: 1 == right, -1 == left
    player_dir = 1
    # walking animation state (ms)
    walk_anim_time = 0
    walk_anim_interval = 200
    walk_frame = 0
    # flag animation state (plays once when reaching the castle)
    flag_animating = False
    flag_anim_time = 0.0
    flag_anim_duration = 4.0
    flag_anim_done = False
    score = 0
    
    # make the main ground a bit taller (was 50)
    platforms = [
        pygame.Rect(0, HEIGHT - 70, 40000, 70),
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

    # Reposition player, enemies and castle so they sit on top of the ground platform
    try:
        ground_plat = next((p for p in platforms if p.x == 0 and p.width >= 1000), platforms[0])
        # place player on ground
        player.y = ground_plat.top - player.height
        # place castle on ground
        castle.y = ground_plat.top - castle.height
        # align enemies on ground
        for e in enemies:
            e['rect'].y = ground_plat.top - e['rect'].height
    except Exception:
        pass


    # ====================
    # INTERNE FUNCTIES
    # ====================
    
    def reset_game():
        nonlocal player, player_vel_y, score, coins, enemies, win, on_ground, camera_x, game_over
        nonlocal flag_animating, flag_anim_time, flag_anim_done
        player.x = 100
        # place player on top of ground platform
        try:
            ground_plat = next((p for p in platforms if p.x == 0 and p.width >= 1000), platforms[0])
            player.y = ground_plat.top - player.height
        except Exception:
            player.y = HEIGHT - 120
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
        # align enemies and castle on ground after reset
        try:
            ground_plat = next((p for p in platforms if p.x == 0 and p.width >= 1000), platforms[0])
            castle.y = ground_plat.top - castle.height
            for e in enemies:
                e['rect'].y = ground_plat.top - e['rect'].height
        except Exception:
            pass

    def move_player_func(keys):
        nonlocal on_ground, player_vel_y, camera_x
        nonlocal player_dir
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -speed
            player_dir = -1
        if keys[pygame.K_RIGHT]:
            dx = speed
            player_dir = 1
        player.x += dx
        player_vel_y += gravity
        player.y += player_vel_y

        on_ground = False
        for plat in platforms:
            if player.colliderect(plat) and player_vel_y >= 0:
                # only land if player's feet crossed the platform top this frame
                try:
                    prev_bottom = player.y - player_vel_y + player.height
                    if prev_bottom <= plat.top and player.bottom >= plat.top:
                        player.bottom = plat.top
                        player_vel_y = 0
                        on_ground = True
                except Exception:
                    # fallback to previous behavior
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
                    if enemy_die_sound:
                        enemy_die_sound.play()
                else:
                    game_over = True


    def check_coin_collisions_func():
        nonlocal score
        for c in coins[:]:
            if player.colliderect(c):
                coins.remove(c)
                score += 1
                if coin_sound:
                    coin_sound.play()


    def draw_world_func():
        # Achtergrond (full-screen)
        if bg_img:
            # Draw the background to fill the whole screen (no horizontal tilt/offset)
            SCREEN.blit(bg_img, (0, 0))
        else:
            SCREEN.fill(SKY_BLUE)

        # === AANGEPASTE PLATFORMS ===
        for plat in platforms:
            # We definiëren de rechthoek die we gaan tekenen (rekening houdend met camera)
            draw_rect = (plat.x - camera_x, plat.y, plat.width, plat.height)

            # 1. Teken de binnenkant: gebruik wood blocks for small platforms, otherwise ground image
            try:
                is_main_ground = (plat.x == 0 and plat.width >= 1000)
                if not is_main_ground and wood_original is not None:
                    # tile wood blocks across the platform width
                    orig_w, orig_h = wood_original.get_size()
                    if orig_h == 0:
                        raise Exception("invalid wood image")
                    # scale block height to platform height
                    tile_h = plat.height
                    tile_w = int(orig_w * (tile_h / orig_h)) if orig_w and orig_h else tile_h
                    if tile_w <= 0:
                        tile_w = tile_h
                    tile_img = pygame.transform.scale(wood_original, (tile_w, tile_h))
                    # loop and blit across platform
                    x = 0
                    while x < plat.width:
                        blit_x = plat.x + x - camera_x
                        SCREEN.blit(tile_img, (blit_x, plat.y))
                        x += tile_w
                    # draw a small gradient shadow on top of the wood platform
                    try:
                        shadow_h = max(4, int(plat.height / 3))
                        shadow_surf = pygame.Surface((plat.width, shadow_h), pygame.SRCALPHA)
                        max_alpha = 100
                        for i in range(shadow_h):
                            alpha = int(max_alpha * ((i + 1) / shadow_h))
                            pygame.draw.rect(shadow_surf, (0, 0, 0, alpha), (0, i, plat.width, 1))
                        shadow_y = plat.y - shadow_h + 2
                        SCREEN.blit(shadow_surf, (plat.x - camera_x, shadow_y))
                    except Exception:
                        pass
                elif grond_img_loaded and grond_original is not None:
                    try:
                        # Tile the ground image horizontally to avoid stretching.
                        orig_w, orig_h = grond_original.get_size()
                        tile_h = plat.height
                        tile_w = int(orig_w * (tile_h / orig_h)) if orig_h else tile_h
                        if tile_w <= 0:
                            tile_w = tile_h
                        tile_img = pygame.transform.scale(grond_original, (tile_w, tile_h))

                        # Determine area to tile: from platform left until the castle,
                        # then place one additional tile after the castle to ensure coverage.
                        try:
                            castle_rel_x = max(0, castle.x - plat.x)
                            castle_w = castle.width
                        except Exception:
                            castle_rel_x = plat.width
                            castle_w = tile_w

                        # Tile up to castle right edge, plus one extra tile
                        target_end = min(plat.width, castle_rel_x + castle_w + tile_w)

                        x = 0
                        while x < target_end:
                            blit_x = plat.x + x - camera_x
                            SCREEN.blit(tile_img, (blit_x, plat.y))
                            x += tile_w

                        # Also make sure the visible screen area is fully covered (left/right)
                        # in case camera shows regions beyond the tiled target.
                        screen_start = camera_x - (camera_x % tile_w) - tile_w
                        screen_end = camera_x + WIDTH
                        x = screen_start - plat.x
                        while x < screen_end - plat.x:
                            blit_x = plat.x + x - camera_x
                            SCREEN.blit(tile_img, (blit_x, plat.y))
                            x += tile_w

                        # draw a small gradient shadow on top of the ground tiles
                        try:
                            shadow_h = max(4, int(plat.height / 3))
                            shadow_surf = pygame.Surface((plat.width, shadow_h), pygame.SRCALPHA)
                            max_alpha = 100
                            for i in range(shadow_h):
                                alpha = int(max_alpha * ((i + 1) / shadow_h))
                                pygame.draw.rect(shadow_surf, (0, 0, 0, alpha), (0, i, plat.width, 1))
                            shadow_y = plat.y - shadow_h + 2
                            SCREEN.blit(shadow_surf, (plat.x - camera_x, shadow_y))
                        except Exception:
                            pass
                    except Exception:
                        # fallback to single scaled blit if anything goes wrong
                        img = pygame.transform.scale(grond_original, (plat.width, plat.height))
                        SCREEN.blit(img, (plat.x - camera_x, plat.y))
                else:
                    pygame.draw.rect(SCREEN, GROUND, draw_rect)
            except Exception:
                pygame.draw.rect(SCREEN, GROUND, draw_rect)
            
            # 2. Teken de "Gloeiende" Rode Rand
            # De 4 aan het einde is de dikte van de lijn

        # Coins (draw coin image if available, otherwise fallback to yellow rect)
        for c in coins:
            if 'coin_original' in locals() and coin_original is not None:
                try:
                    # slower, gentle bobbing animation
                    t = pygame.time.get_ticks() / 1000.0
                    freq = 0.7  # cycles per second (slower)
                    amp = 6     # pixels (slightly larger bob)
                    bob = math.sin(t * 2 * math.pi * freq) * amp
                    # make coins bigger visually (scale up from rect)
                    new_w = max(1, int(c.width * 2.5))
                    new_h = max(1, int(c.height * 2.5))
                    img = pygame.transform.scale(coin_original, (new_w, new_h))
                    # center the larger coin on the original coin rect, and apply bob
                    blit_x = c.x - camera_x - (new_w - c.width) // 2
                    blit_y = int(c.y + bob - (new_h - c.height))
                    SCREEN.blit(img, (blit_x, blit_y))
                except Exception:
                    pygame.draw.rect(SCREEN, YELLOW, (c.x - camera_x, c.y, c.width, c.height))
            else:
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
        # draw a persistent pole at the end of the map (visible always)
        try:
            pole_w_static = 4
            # make pole touch the bottom of the screen, and be slightly shorter
            pole_x_static = flag_draw_x - pole_w_static - 4
            pole_top_static = (HEIGHT // 3) + 6
            pole_bottom_static = HEIGHT
            pole_h_static = pole_bottom_static - pole_top_static
            pygame.draw.rect(SCREEN, GRAY, (pole_x_static, pole_top_static, pole_w_static, pole_h_static))
        except Exception:
            pass
        # Only draw the in-world flag after the animation has completed
        if flag_anim_done and not flag_animating:
            flag_draw_y = flag_end_y
        else:
            flag_draw_y = None

        if flag_draw_y is not None:
            if 'flag_original' in locals() and flag_original is not None:
                try:
                    # scale flag to fit (make it wider)
                    flag_w = int(flag.width * 1.8)
                    flag_h = int(flag.height * 0.9)
                    flag_img = pygame.transform.scale(flag_original, (flag_w, flag_h))
                    # draw a gray pole (stick) left of the flag (thinner)
                    pole_w = 4
                    pole_x = flag_draw_x - pole_w - 4
                    try:
                        pygame.draw.rect(SCREEN, GRAY, (pole_x, int(flag_draw_y), pole_w, flag_h))
                    except Exception:
                        pass
                    SCREEN.blit(flag_img, (flag_draw_x, int(flag_draw_y)))
                except Exception:
                    # fallback: draw pole + rect
                    pole_w = 4
                    pole_x = flag_draw_x - pole_w - 4
                    try:
                        pygame.draw.rect(SCREEN, GRAY, (pole_x, int(flag_draw_y), pole_w, flag.height))
                    except Exception:
                        pass
                    pygame.draw.rect(SCREEN, GRAY, (flag_draw_x, flag_draw_y, flag.width, flag.height))
            else:
                pole_w = 4
                pole_x = flag_draw_x - pole_w - 4
                try:
                    pygame.draw.rect(SCREEN, GRAY, (pole_x, int(flag_draw_y), pole_w, flag.height))
                except Exception:
                    pass
                pygame.draw.rect(SCREEN, GRAY, (flag_draw_x, flag_draw_y, flag.width, flag.height))

    def draw_enemies_func():
        for e in enemies:
            draw_x = e["rect"].x - camera_x
            draw_y = e["rect"].y
            if enemy_imgs_loaded:
                try:
                    # scale enemy image to the enemy rect so the sprite stands on the platform
                    img = pygame.transform.scale(mushroom_original, (e["rect"].width, e["rect"].height))
                    if e["dir"] == -1:
                        blit_y = e["rect"].bottom - img.get_height()
                        SCREEN.blit(img, (draw_x, blit_y))
                    else:
                        img_flipped = pygame.transform.flip(img, True, False)
                        blit_y = e["rect"].bottom - img_flipped.get_height()
                        SCREEN.blit(img_flipped, (draw_x, blit_y))
                except Exception:
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

            # update walking animation timer
            try:
                dt_ms = CLOCK.get_time()
                moving_h = (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) and on_ground
                if moving_h:
                    walk_anim_time += dt_ms
                    if walk_anim_time >= walk_anim_interval:
                        walk_frame = 1 - walk_frame
                        walk_anim_time -= walk_anim_interval
                else:
                    walk_frame = 0
                    walk_anim_time = 0
            except Exception:
                pass

            # Only set win when player actually reaches the castle area (avoid false positives)
            # Require collision, horizontal proximity and that player is standing at castle level
            if (player.colliderect(castle)
                and player.x >= castle.x - 10
                and player.bottom >= castle.top - 5):
                win = True
                # play win sound (Sound preferred, fallback to music)
                try:
                    sound_enabled = getattr(pygame.mixer, 'SOUND_ON', True)
                    if sound_enabled:
                        if win_sound:
                            win_sound.play()
                        else:
                            try:
                                if pygame.mixer.get_init():
                                    pygame.mixer.music.play()
                            except Exception:
                                pass
                except Exception:
                    pass
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
            
            # choose player image based on walking animation and direction
            img_to_draw = None
            try:
                moving_h = (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) and on_ground
                # jumping takes precedence
                if not on_ground:
                    if player_dir == 1 and 'player_jump_right' in locals() and player_jump_right is not None:
                        img_to_draw = player_jump_right
                    elif player_dir == -1 and 'player_jump_left' in locals() and player_jump_left is not None:
                        img_to_draw = player_jump_left
                    else:
                        if player_dir == -1 and 'player_idle_left' in locals() and player_idle_left is not None:
                            img_to_draw = player_idle_left
                        else:
                            img_to_draw = player_idle_img if 'player_idle_img' in locals() else player_img
                elif moving_h and player_dir == 1 and player_walk_frames_right:
                    img_to_draw = player_walk_frames_right[walk_frame]
                elif moving_h and player_dir == -1 and player_walk_frames_left:
                    img_to_draw = player_walk_frames_left[walk_frame]
                else:
                    if player_dir == -1 and 'player_idle_left' in locals() and player_idle_left is not None:
                        img_to_draw = player_idle_left
                    else:
                        img_to_draw = player_idle_img if 'player_idle_img' in locals() else player_img
            except Exception:
                img_to_draw = player_img

            if img_to_draw:
                try:
                    img_h = img_to_draw.get_height()
                    blit_y = player.bottom - img_h
                    SCREEN.blit(img_to_draw, (player.x - camera_x, blit_y))
                except Exception:
                    SCREEN.blit(img_to_draw, (player.x - camera_x, player.y))
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
                # choose player image based on walking animation and direction
                img_to_draw = None
                try:
                    moving_h = ((keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) and on_ground)
                    if not on_ground:
                        if player_dir == 1 and 'player_jump_right' in locals() and player_jump_right is not None:
                            img_to_draw = player_jump_right
                        elif player_dir == -1 and 'player_jump_left' in locals() and player_jump_left is not None:
                            img_to_draw = player_jump_left
                        else:
                            img_to_draw = player_idle_img if 'player_idle_img' in locals() else player_img
                    elif moving_h and player_dir == 1 and player_walk_frames_right:
                        img_to_draw = player_walk_frames_right[walk_frame]
                    elif moving_h and player_dir == -1 and player_walk_frames_left:
                        img_to_draw = player_walk_frames_left[walk_frame]
                    else:
                        img_to_draw = player_idle_img if 'player_idle_img' in locals() else player_img
                except Exception:
                    img_to_draw = player_img

                if img_to_draw:
                    try:
                        img_h = img_to_draw.get_height()
                        blit_y = player.bottom - img_h
                        SCREEN.blit(img_to_draw, (player.x - camera_x, blit_y))
                    except Exception:
                        SCREEN.blit(img_to_draw, (player.x - camera_x, player.y))
                else:
                    pygame.draw.rect(SCREEN, (150, 100, 60), (player.x - camera_x, player.y, player.width, player.height))
                SCREEN.blit(FONT.render(f"Score: {score}", True, BLACK), (20, 20))

                # Draw the flag as a screen-space overlay to the left of the castle
                try:
                    # scale flag to a reasonable size (wider)
                    flag_w = max(32, int(flag.width * 2))
                    flag_h = max(16, int(flag.height * 0.6))
                    flag_img = pygame.transform.scale(flag_original, (flag_w, flag_h))

                    # pole x: left of the castle in screen coords (flag is to left)
                    pole_x_screen = (castle.x - camera_x) - flag_w - 10

                    # start below the screen, end at 1/3 of the screen height
                    start_y_screen = HEIGHT + flag_h + 40
                    end_y_screen = HEIGHT // 3
                    cur_y_screen = start_y_screen + (end_y_screen - start_y_screen) * progress

                    SCREEN.blit(flag_img, (pole_x_screen, int(cur_y_screen)))
                except Exception:
                    # fallback: draw a simple rect in screen-space plus a pole
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