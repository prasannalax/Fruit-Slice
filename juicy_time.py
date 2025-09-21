import pygame
import random
import sys
import string
import cv2

pygame.init()

# ----------- Window -------------
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Slash Typing Game")
clock = pygame.time.Clock()

# ----------- Colors -------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (220, 20, 60)
GREEN = (0, 200, 0)
BLUE  = (0, 0, 200)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (180,180,180)

# ----------- Fonts --------------
font = pygame.font.SysFont("arial", 28)
big_font = pygame.font.SysFont("arial", 48)

# ----------- Sounds -------------
try: cut_sound = pygame.mixer.Sound("cut.wav")
except: cut_sound = None
try: fill_sound = pygame.mixer.Sound("fill.wav")
except: fill_sound = None
try: win_sound = pygame.mixer.Sound("win.wav")
except: win_sound = None
try: lose_sound = pygame.mixer.Sound("lose.wav")
except: lose_sound = None

# ----------- Images -------------
def load_image(name, color, size=(70,70)):
    try:
        img = pygame.image.load(name).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (size[0]//2, size[1]//2), size[0]//2)
        return surf

fruit_images = {
    "Apple": load_image("apple.png", RED),
    "Banana": load_image("banana.png", YELLOW),
    "Mango": load_image("mango.png", ORANGE),
    "Grape": load_image("grape.png", PURPLE),
    "Orange": load_image("orange.png", ORANGE),
    "Strawberry": load_image("strawberry.png", RED),
}
fruit_colors = {
    "Apple": RED, "Banana": YELLOW, "Mango": ORANGE,
    "Grape": PURPLE, "Orange": ORANGE, "Strawberry": RED,
}

# ----------- Game Variables -----
FPS = 60
score = 0
timer = 50
fruit_speed = 5
current_fruit = None
game_over = False
game_win = False
missed = 0
MAX_MISSES = 3
start_ticks = pygame.time.get_ticks()
lose_reason = ""
popup_message = ""
popup_timer = 0
POPUP_DURATION = 1000
LEVEL = 1
FRUITS_TO_FILL = 5  # Level 1 fill requirement

# Boxes setup for fruit fill
box_width = 120
box_height = 150
box_gap = 20
fruit_list = list(fruit_images.keys())[:5]
box_start_x = (WIDTH - (box_width*len(fruit_list) + box_gap*(len(fruit_list)-1)))//2
boxes = []
for i, name in enumerate(fruit_list):
    boxes.append({
        "fruit": name,
        "x": box_start_x + i*(box_width+box_gap),
        "y": HEIGHT - box_height - 60,
        "fill":0
    })

# ----------- Helper Functions ----------
def draw_text_with_outline(text, size, color, outline_color, x, y, center=True):
    f = pygame.font.SysFont("arial", size, bold=True)
    surf = f.render(text, True, color)
    outline = f.render(text, True, outline_color)
    rect = surf.get_rect()
    if center: rect.center = (x,y)
    else: rect.topleft = (x,y)
    for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
        screen.blit(outline, rect.move(dx,dy))
    screen.blit(surf, rect)

def play_background_music():
    """Play looping background music."""
    try:
        pygame.mixer.music.load("game_bg.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except:
        print("Warning: Could not play background music.")

# ----------- Front Page ----------
def front_page():
    try:
        bg_image = pygame.image.load("menu_bg.jpg").convert()
        bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    except:
        bg_image = None

    play_background_music()

    fruit_icons = []
    for f_name, img in fruit_images.items():
        icon = pygame.transform.scale(img, (50, 50))
        fruit_icons.append({"image": icon,
                            "x": random.randint(0, WIDTH-50),
                            "y": random.randint(0, HEIGHT//2),
                            "speed": random.uniform(0.5, 1.5)})

    running_menu = True
    while running_menu:
        screen.fill(WHITE)
        if bg_image:
            screen.blit(bg_image, (0,0))
        else:
            for i in range(HEIGHT):
                color = (255 - i//3, 255, 255 - i//3)
                pygame.draw.line(screen, color, (0,i), (WIDTH,i))

        for icon in fruit_icons:
            icon["y"] += icon["speed"]
            if icon["y"] > HEIGHT:
                icon["y"] = -50
                icon["x"] = random.randint(0, WIDTH-50)
            screen.blit(icon["image"], (icon["x"], icon["y"]))

        draw_text_with_outline("FRUIT SLASH TYPING GAME", 60, ORANGE, BLACK, WIDTH//2, HEIGHT//4)
        start_button = pygame.Rect(WIDTH//2-100, HEIGHT//2, 200, 60)
        quit_button = pygame.Rect(WIDTH//2-100, HEIGHT//2+100, 200, 60)

        pygame.draw.rect(screen, GREEN, start_button, border_radius=10)
        pygame.draw.rect(screen, RED, quit_button, border_radius=10)

        draw_text_with_outline("START GAME", 36, WHITE, BLACK, start_button.centerx, start_button.centery)
        draw_text_with_outline("QUIT", 36, WHITE, BLACK, quit_button.centerx, quit_button.centery)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    running_menu=False
                elif quit_button.collidepoint(event.pos):
                    pygame.quit(); sys.exit()

# ----------- Video Intro ----------
def play_video_intro(filename, musicfile):
    pygame.mixer.music.stop()  # Stop any background music
    try:
        pygame.mixer.music.load(musicfile)
        pygame.mixer.music.set_volume(0.7)
        pygame.mixer.music.play()
    except:
        print("Warning: Could not play video music.")

    cap = cv2.VideoCapture(filename)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.transpose(frame)
        frame = pygame.surfarray.make_surface(frame)
        frame = pygame.transform.scale(frame, (WIDTH, HEIGHT))

        screen.blit(frame, (0,0))
        pygame.display.update()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                sys.exit()

    cap.release()
    pygame.mixer.music.stop()

# ----------- Gift Box Mini-Game ----------
def gift_box_unlock():
    try:
        box_img = pygame.image.load("box.png").convert_alpha()
        box_img = pygame.transform.scale(box_img, (120,150))
    except:
        box_img = pygame.Surface((120,150))
        box_img.fill(BLUE)
    
    try:
        key_img = pygame.image.load("key.png").convert_alpha()
        key_img = pygame.transform.scale(key_img, (60,60))
    except:
        key_img = pygame.Surface((60,60))
        key_img.fill(YELLOW)

    gap = 50
    start_x = (WIDTH - (3*120 + 2*gap)) // 2
    boxes_pos = [pygame.Rect(start_x + i*(120+gap), HEIGHT//2-75, 120,150) for i in range(3)]
    key_index = random.randint(0,2)
    unlocked = False
    popup_msg = ""
    reveal_key = False

    play_background_music()  # Start mini-game background music

    while not unlocked:
        screen.fill(WHITE)
        draw_text_with_outline("Choose the box with the key 🔑", 40, GREEN, BLACK, WIDTH//2, HEIGHT//4)

        for i, rect in enumerate(boxes_pos):
            screen.blit(box_img, (rect.x, rect.y))
            if reveal_key and i == key_index:
                screen.blit(key_img, (rect.centerx-30, rect.centery-30))

        if popup_msg:
            draw_text_with_outline(popup_msg, 32, RED, BLACK, WIDTH//2, HEIGHT//2 + 120)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(boxes_pos):
                    if rect.collidepoint(event.pos):
                        if i == key_index:
                            popup_msg = "You are right!"
                            reveal_key = True
                            pygame.display.flip()
                            pygame.time.delay(1000)
                            unlocked = True
                        else:
                            popup_msg = "You are wrong! Try again!"

# ----------- Game Functions ----------
def get_available_fruits():
    return [b["fruit"] for b in boxes if b["fill"] < 1]

def spawn_fruit():
    global current_fruit
    available = get_available_fruits()
    if not available:
        current_fruit = None
        return
    c = random.choice(available)
    current_fruit = {
        "type": c,
        "image": fruit_images[c],
        "x": random.randint(50, WIDTH-100),
        "y": -80,
        "letter": random.choice(string.ascii_uppercase),
        "cut": False,
        "cut_anim": 0
    }

def reset_game(level=1):
    global score, timer, current_fruit, game_over, game_win, missed, start_ticks, FRUITS_TO_FILL
    score = 0
    timer = 50
    current_fruit = None
    game_over = False
    game_win = False
    missed = 0
    start_ticks = pygame.time.get_ticks()
    FRUITS_TO_FILL = 5 if level==1 else 6
    for b in boxes: b["fill"] = 0
    spawn_fruit()
    play_background_music()

# ----------- Draw Boxes & Screens ----------
def draw_boxes():
    for b in boxes:
        rect = pygame.Rect(b["x"],b["y"],box_width,box_height)
        pygame.draw.rect(screen, GRAY, rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, rect,3,border_radius=10)
        fill_h = int(b["fill"] * box_height)
        if fill_h>0:
            pygame.draw.rect(screen, fruit_colors[b["fruit"]],
                             (b["x"],b["y"]+box_height-fill_h, box_width, fill_h), border_radius=5)
        draw_text_with_outline(b["fruit"],20,BLACK,WHITE,rect.centerx,b["y"]+box_height+15)

def game_over_screen():
    global game_over
    pygame.mixer.music.stop()
    if lose_sound:
        lose_sound.play()

    screen.fill(BLACK)
    draw_text_with_outline("GAME OVER!",64,RED,WHITE,WIDTH//2,HEIGHT//3)
    draw_text_with_outline(f"Score: {score}",40,WHITE,BLACK,WIDTH//2,HEIGHT//2)
    if lose_reason:
        draw_text_with_outline(lose_reason,30,YELLOW,BLACK,WIDTH//2,HEIGHT//2+50)
    
    button_rect = pygame.Rect(WIDTH//2-100, HEIGHT//2+110, 200, 60)
    pygame.draw.rect(screen, BLUE, button_rect, border_radius=10)
    draw_text_with_outline("RESTART",36,WHITE,BLACK,WIDTH//2, HEIGHT//2+140)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    reset_game(level=LEVEL)
                    waiting=False

def level_completion_screen():
    global LEVEL
    pygame.mixer.music.stop()
    if win_sound:
        win_sound.play()

    screen.fill(BLACK)
    draw_text_with_outline(f"Level {LEVEL} Completed!", 64, GREEN, BLACK, WIDTH//2, HEIGHT//3)
    draw_text_with_outline(f"Score: {score}", 40, WHITE, BLACK, WIDTH//2, HEIGHT//2)

    continue_rect = pygame.Rect(WIDTH//2-120, HEIGHT//2+100, 100, 50)
    quit_rect = pygame.Rect(WIDTH//2+20, HEIGHT//2+100, 100, 50)
    pygame.draw.rect(screen, BLUE, continue_rect, border_radius=10)
    pygame.draw.rect(screen, RED, quit_rect, border_radius=10)
    draw_text_with_outline("CONTINUE",28,WHITE,BLACK,continue_rect.centerx, continue_rect.centery)
    draw_text_with_outline("QUIT",28,WHITE,BLACK,quit_rect.centerx, quit_rect.centery)

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if continue_rect.collidepoint(event.pos):
                    LEVEL += 1
                    reset_game(level=LEVEL)
                    waiting = False
                elif quit_rect.collidepoint(event.pos):
                    pygame.quit(); sys.exit()
        pygame.display.flip()
        clock.tick(FPS)

def game_win_screen():
    # Redirect to level completion screen
    level_completion_screen()

# ----------- Main Loop ----------
def main_game_loop():
    global current_fruit, game_over, game_win, score, timer, missed, popup_message, popup_timer, lose_reason
    reset_game(LEVEL)
    while True:
        dt = clock.tick(FPS)
        screen.fill(WHITE)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if not game_over and not game_win and event.type==pygame.KEYDOWN:
                key = event.unicode.upper()
                if current_fruit and not current_fruit["cut"] and current_fruit["letter"]==key:
                    current_fruit["cut"] = True
                    current_fruit["cut_anim"] = 10
                    score += 1
                    for b in boxes:
                        if b["fruit"]==current_fruit["type"]:
                            b["fill"] += 1/FRUITS_TO_FILL
                            if b["fill"]>1: b["fill"]=1
                            break
                    if fill_sound: fill_sound.play()
                    if cut_sound: cut_sound.play()
                elif current_fruit:
                    game_over=True
                    lose_reason = "Wrong key pressed!"
                    popup_message = "Wrong key!"
                    popup_timer = pygame.time.get_ticks()

        # Timer
        if not game_over and not game_win:
            seconds = (pygame.time.get_ticks()-start_ticks)//1000
            timer=50-seconds
            if timer<=0:
                game_over=True
                lose_reason = "Time's up!"

        # Update fruit
        if current_fruit:
            if not current_fruit["cut"]:
                current_fruit["y"] += fruit_speed
                if current_fruit["y"] > HEIGHT:
                    missed += 1
                    popup_message = "Missed a fruit!"
                    popup_timer = pygame.time.get_ticks()
                    if missed >= MAX_MISSES:
                        game_over = True
                        lose_reason = "Too many fruits missed!"
                    current_fruit = None
            elif current_fruit["cut_anim"] > 0:
                current_fruit["cut_anim"] -= 1
                current_fruit["y"] -= 2
            else:
                current_fruit = None

        # Spawn next fruit
        if not current_fruit and not game_over and not game_win:
            spawn_fruit()

        # Draw current fruit
        if current_fruit:
            screen.blit(current_fruit["image"], (current_fruit["x"], current_fruit["y"]))
            draw_text_with_outline(current_fruit["letter"], 28, WHITE, BLACK,
                                   current_fruit["x"]+35, current_fruit["y"]-20)

        # Draw boxes
        draw_boxes()

        # HUD
        draw_text_with_outline(f"Score: {score}",28,BLACK,WHITE,10,10,center=False)
        draw_text_with_outline(f"Time: {timer}",28,BLACK,WHITE,WIDTH-150,10,center=False)
        draw_text_with_outline(f"Missed: {missed}/{MAX_MISSES}",28,RED,WHITE,10,50,center=False)

        # Popup
        if popup_message and pygame.time.get_ticks() - popup_timer < POPUP_DURATION:
            draw_text_with_outline(popup_message,30,ORANGE,BLACK,WIDTH//2,80)

        # Game over / win
        if game_over:
            game_over_screen()
        if all(b["fill"] >= 1 for b in boxes):
            game_win = True
            game_win_screen()

        pygame.display.flip()

# ----------- Run Everything ----------
front_page()
play_video_intro("starting.mp4", "video_music.mp3")
gift_box_unlock()
main_game_loop()