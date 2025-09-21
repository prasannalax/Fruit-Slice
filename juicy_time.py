import pygame
import random
import sys
import string

pygame.init()

# ----------- Window -------------
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Slash Typing Game")

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
try:
    pygame.mixer.music.load("background.mp3")
    pygame.mixer.music.play(-1)
except: pass

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
clock = pygame.time.Clock()
FPS = 60
score = 0
timer = 50
fruit_speed = 5
current_fruit = None  # Only one fruit at a time
game_over = False
game_win = False
missed = 0
MAX_MISSES = 3
start_ticks = pygame.time.get_ticks()
lose_reason = ""
popup_message = ""
popup_timer = 0
POPUP_DURATION = 1000

# Boxes setup
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

# ----------- Functions ----------
def get_available_fruits():
    """Return list of fruits whose boxes are not yet full"""
    available = [b["fruit"] for b in boxes if b["fill"] < 1]
    return available

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

def reset_game():
    global score, timer, current_fruit, game_over, game_win, missed, start_ticks
    score = 0
    timer = 50
    current_fruit = None
    game_over = False
    game_win = False
    missed = 0
    start_ticks = pygame.time.get_ticks()
    for b in boxes: b["fill"] = 0
    spawn_fruit()

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

def game_over_screen():
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
                    reset_game()
                    waiting=False

def game_win_screen():
    screen.fill(BLACK)
    draw_text_with_outline("🎉 YOU WIN! 🎉",64,GREEN,BLACK,WIDTH//2,HEIGHT//3)
    draw_text_with_outline(f"Final Score: {score}",40,WHITE,BLACK,WIDTH//2,HEIGHT//2)
    button_rect = pygame.Rect(WIDTH//2-100, HEIGHT//2+110, 200, 60)
    pygame.draw.rect(screen, BLUE, button_rect, border_radius=10)
    draw_text_with_outline("PLAY AGAIN",36,WHITE,BLACK,WIDTH//2, HEIGHT//2+140)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    reset_game()
                    waiting=False

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

# ----------- Main Loop ----------
reset_game()
running = True
while running:
    dt = clock.tick(FPS)
    screen.fill(WHITE)

    # Events
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        if not game_over and not game_win and event.type==pygame.KEYDOWN:
            key = event.unicode.upper()
            if current_fruit and not current_fruit["cut"] and current_fruit["letter"]==key:
                current_fruit["cut"] = True
                current_fruit["cut_anim"] = 10
                score += 1
                for b in boxes:
                    if b["fruit"]==current_fruit["type"]:
                        b["fill"] += 0.2
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

    # Spawn next fruit if none exists
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
    if game_win or all(b["fill"] >= 1 for b in boxes):
        game_win = True
        game_win_screen()

    pygame.display.flip()

pygame.quit()
