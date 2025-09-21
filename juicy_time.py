import pygame
import random
import sys

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
try:
    cut_sound = pygame.mixer.Sound("cut.wav")
except:
    cut_sound = None

try:
    fill_sound = pygame.mixer.Sound("fill.wav")
except:
    fill_sound = None

try:
    pygame.mixer.music.load("background.mp3")
    pygame.mixer.music.play(-1)
except:
    pass

# ----------- Images (Fruits) ----
def load_image(name, color):
    try:
        img = pygame.image.load(name).convert_alpha()
        return pygame.transform.scale(img, (70,70))
    except:
        surf = pygame.Surface((70,70), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (35,35), 35)
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
    "Apple": RED,
    "Banana": YELLOW,
    "Mango": ORANGE,
    "Grape": PURPLE,
    "Orange": ORANGE,
    "Strawberry": RED,
}

fruit_letters = {
    "Apple":"A",
    "Banana":"B",
    "Mango":"M",
    "Grape":"G",
    "Orange":"O",
    "Strawberry":"S"
}

# ----------- Game Variables -----
clock = pygame.time.Clock()
FPS = 60
score = 0
timer = 40
fruit_speed = 1.5  
fruits = []
game_over = False
missed = 0
MAX_MISSES = 3
start_ticks = pygame.time.get_ticks()
lose_reason = ""   # Game over reason

# Popup message variables
popup_message = ""
popup_timer = 0
POPUP_DURATION = 1000  # 1 second in ms

# Boxes setup
box_width = 120
box_height = 150
box_gap = 20
box_start_x = (WIDTH - (box_width*5 + box_gap*4))//2
boxes = []
for i, name in enumerate(list(fruit_images.keys())[:5]):
    boxes.append({
        "fruit":name,
        "x": box_start_x + i*(box_width+box_gap),
        "y": HEIGHT - box_height - 20,
        "fill":0  
    })

# ----------- Functions ----------
def generate_positions(num):
    """Generate non-overlapping random x positions."""
    positions = []
    while len(positions) < num:
        x = random.randint(50, WIDTH-100)
        if all(abs(x - p) > 120 for p in positions):
            positions.append(x)
    return positions

def spawn_fruits():
    global fruits
    fruits = []
    choices = random.sample(list(fruit_images.keys()), 3)
    xs = generate_positions(3)
    for i, c in enumerate(choices):
        fruits.append({
            "type": c,
            "image": fruit_images[c],
            "x": xs[i],
            "y": -80 - random.randint(0,150),  # staggered height
            "letter": fruit_letters[c],
            "cut": False
        })

def reset_game():
    global score, timer, fruit_speed, fruits, game_over, missed, start_ticks, boxes, lose_reason
    global popup_message, popup_timer
    score = 0
    timer = 40
    fruit_speed = 1.5  
    fruits = []
    game_over = False
    missed = 0
    lose_reason = ""
    popup_message = ""
    popup_timer = 0
    start_ticks = pygame.time.get_ticks()
    for b in boxes:
        b["fill"] = 0
    spawn_fruits()

def draw_text(text,size,color,x,y,center=True):
    f = pygame.font.SysFont("arial", size, bold=True)
    surf = f.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x,y)
    else:
        rect.topleft = (x,y)
    screen.blit(surf, rect)

def game_over_screen():
    screen.fill(BLACK)
    draw_text("GAME OVER!",64,RED,WIDTH//2,HEIGHT//3)
    draw_text(f"Score: {score}",40,WHITE,WIDTH//2,HEIGHT//2)
    if lose_reason:
        draw_text(lose_reason,30,YELLOW,WIDTH//2,HEIGHT//2+40)
    button_rect = pygame.Rect(WIDTH//2-100, HEIGHT//2+90, 200, 60)
    pygame.draw.rect(screen, BLUE, button_rect, border_radius=10)
    draw_text("RESTART",36,WHITE,WIDTH//2, HEIGHT//2+120)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    reset_game()
                    waiting=False

def draw_boxes():
    for b in boxes:
        rect = pygame.Rect(b["x"],b["y"],box_width,box_height)
        pygame.draw.rect(screen, GRAY, rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, rect,3,border_radius=10)
        draw_text(b["fruit"],20,BLACK,rect.centerx,rect.y-10)
        fill_h = int(b["fill"] * box_height)
        if fill_h>0:
            pygame.draw.rect(screen, fruit_colors[b["fruit"]],
                             (b["x"],b["y"]+box_height-fill_h, box_width, fill_h), border_radius=5)

# ----------- Main Loop ----------
spawn_fruits()
running = True
while running:
    dt = clock.tick(FPS)
    screen.fill(WHITE)

    # Events
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        if not game_over and event.type==pygame.KEYDOWN:
            key = event.unicode.upper()
            found=False
            for f in fruits:
                if not f["cut"] and f["letter"]==key:
                    f["cut"]=True
                    score+=1
                    for b in boxes:
                        if b["fruit"]==f["type"]:
                            b["fill"]+=0.2
                            if b["fill"]>1: b["fill"]=1
                            if fill_sound: fill_sound.play()
                    if cut_sound: cut_sound.play()
                    found=True
                    break
            if not found:   # Wrong key pressed
                game_over=True
                lose_reason = "Wrong key pressed!"
                popup_message = "Wrong key!"
                popup_timer = pygame.time.get_ticks()

    # Timer
    if not game_over:
        seconds=(pygame.time.get_ticks()-start_ticks)//1000
        timer=40-seconds
        if timer<=0:
            game_over=True
            lose_reason = "Time's up!"

    # Update fruits
    if not game_over:
        for f in fruits[:]:
            if not f["cut"]:
                f["y"]+=fruit_speed
                if f["y"]>HEIGHT:
                    missed += 1
                    popup_message = "Missed a fruit!"
                    popup_timer = pygame.time.get_ticks()
                    if missed >= MAX_MISSES:
                        game_over = True
                        lose_reason = "Too many fruits missed!"
                    fruits.remove(f)
        if all(f["cut"] or f["y"]>HEIGHT for f in fruits):
            spawn_fruits()
            fruit_speed += 0.15  

    # Draw fruits
    for f in fruits:
        if not f["cut"]:
            screen.blit(f["image"],(f["x"],f["y"]))
            draw_text(f["letter"],28,BLACK,f["x"]+35,f["y"]+10)

    # Draw boxes
    draw_boxes()

    # Draw HUD
    draw_text(f"Score: {score}",28,BLACK,10,10,center=False)
    draw_text(f"Time: {timer}",28,BLACK,WIDTH-150,10,center=False)
    draw_text(f"Missed: {missed}/{MAX_MISSES}",28,RED,10,50,center=False)

    # Draw popup messages
    if popup_message and pygame.time.get_ticks() - popup_timer < POPUP_DURATION:
        draw_text(popup_message,30,ORANGE,WIDTH//2,80)

    # Game over
    if game_over:
        game_over_screen()

    pygame.display.flip()

pygame.quit()
