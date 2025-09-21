import pygame
import random
import sys

# -------- Initialization --------
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Juice Typing Game")
clock = pygame.time.Clock()
FPS = 60

# -------- Colors -------------
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (220,20,60)
GREEN = (0,200,0)
BLUE = (0,0,200)
ORANGE = (255,165,0)
YELLOW = (255,255,0)
PURPLE = (128,0,128)
GRAY = (180,180,180)

# -------- Fonts -------------
font = pygame.font.SysFont("arial",28)
big_font = pygame.font.SysFont("arial",48)
small_font = pygame.font.SysFont("arial",20)

# -------- Sounds -------------
def load_sound(file):
    try:
        return pygame.mixer.Sound(file)
    except:
        class Dummy:
            def play(self): pass
        return Dummy()
cut_sound = load_sound("cut.wav")
fill_sound = load_sound("fill.wav")
game_over_sound = load_sound("gameover.wav")

try:
    pygame.mixer.music.load("background.mp3")
    pygame.mixer.music.play(-1)
except:
    pass

# -------- Fruits & Boxes --------
def load_image(name,color):
    try:
        img = pygame.image.load(name).convert_alpha()
        return pygame.transform.scale(img,(70,70))
    except:
        surf = pygame.Surface((70,70),pygame.SRCALPHA)
        pygame.draw.circle(surf,color,(35,35),35)
        return surf

fruit_images = {
    "Apple": load_image("apple.png",RED),
    "Banana": load_image("banana.png",YELLOW),
    "Mango": load_image("mango.png",ORANGE),
    "Grape": load_image("grape.png",PURPLE),
    "Orange": load_image("orange.png",ORANGE),
    "Strawberry": load_image("strawberry.png",RED)
}

fruit_colors = {
    "Apple":RED,"Banana":YELLOW,"Mango":ORANGE,"Grape":PURPLE,
    "Orange":ORANGE,"Strawberry":RED
}

fruit_letters = {
    "Apple":"A","Banana":"B","Mango":"M","Grape":"G",
    "Orange":"O","Strawberry":"S"
}

# 5 boxes
box_width = 120
box_height = 150
box_gap = 20
box_start_x = (WIDTH-(5*box_width + 4*box_gap))//2
boxes = []
for i,name in enumerate(list(fruit_images.keys())[:5]):
    boxes.append({"fruit":name,"x":box_start_x + i*(box_width+box_gap),
                  "y":HEIGHT-box_height-20,"fill":0,"score_given":False})

# -------- Game Variables --------
level = 1
max_level = 5
score = 0
timer = 40
fruit_speed = 1.2
fruits=[]
missed=0
MAX_MISS = 3
start_ticks = pygame.time.get_ticks()
game_over=False
level_complete=False

# -------- Functions ---------
def spawn_fruits():
    global fruits
    fruits=[]
    choices=random.sample(list(fruit_images.keys())[:5],3)
    positions=[]
    for c in choices:
        while True:
            x=random.randint(50,WIDTH-120)
            if all(abs(x-p)<80 for p in positions)==False:
                positions.append(x)
                break
        fruits.append({"type":c,"image":fruit_images[c],
                       "x":x,"y":-80,"letter":fruit_letters[c],
                       "cut":False})

def reset_game():
    global score,timer,fruit_speed,fruits,game_over,missed,start_ticks,boxes,level,level_complete
    score=0
    timer=40
    fruit_speed=1.2
    fruits=[]
    missed=0
    start_ticks=pygame.time.get_ticks()
    level=1
    game_over=False
    level_complete=False
    for b in boxes:
        b["fill"]=0
        b["score_given"]=False
    spawn_fruits()

def draw_text(text,size,color,x,y,center=True):
    f=pygame.font.SysFont("arial",size,bold=True)
    surf=f.render(text,True,color)
    rect=surf.get_rect()
    if center:
        rect.center=(x,y)
    else:
        rect.topleft=(x,y)
    screen.blit(surf,rect)

def draw_boxes():
    for b in boxes:
        rect=pygame.Rect(b["x"],b["y"],box_width,box_height)
        pygame.draw.rect(screen,GRAY,rect,border_radius=10)
        pygame.draw.rect(screen,BLACK,rect,3,border_radius=10)
        draw_text(b["fruit"],20,BLACK,rect.centerx,rect.y-10)
        fill_h=int(b["fill"]*box_height)
        if fill_h>0:
            pygame.draw.rect(screen,fruit_colors[b["fruit"]],
                             (b["x"],b["y"]+box_height-fill_h,box_width,fill_h),border_radius=5)

def level_screen():
    screen.fill(WHITE)
    draw_text(f"LEVEL {level}",50,BLUE,WIDTH//2,HEIGHT//2-50)
    cont_rect = pygame.Rect(WIDTH//2-80, HEIGHT//2+10,160,50)
    quit_rect = pygame.Rect(WIDTH//2-80, HEIGHT//2+90,160,50)
    pygame.draw.rect(screen, GREEN, cont_rect, border_radius=10)
    pygame.draw.rect(screen, RED, quit_rect, border_radius=10)
    draw_text("Continue",28,WHITE,cont_rect.centerx,cont_rect.centery)
    draw_text("Quit",28,WHITE,quit_rect.centerx,quit_rect.centery)
    pygame.display.flip()
    waiting=True
    while waiting:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit();sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if cont_rect.collidepoint(event.pos):
                    waiting=False
                if quit_rect.collidepoint(event.pos):
                    pygame.quit();sys.exit()

def game_over_screen():
    try: pygame.mixer.music.stop()
    except: pass
    if game_over_sound: game_over_sound.play()
    screen.fill(BLACK)
    draw_text("GAME OVER!",64,RED,WIDTH//2,HEIGHT//3)
    draw_text(f"Score: {score}",40,WHITE,WIDTH//2,HEIGHT//2)
    button_rect=pygame.Rect(WIDTH//2-100,HEIGHT//2+60,200,60)
    pygame.draw.rect(screen,BLUE,button_rect,border_radius=10)
    draw_text("RESTART",36,WHITE,WIDTH//2,HEIGHT//2+90)
    pygame.display.flip()
    waiting=True
    while waiting:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit();sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    reset_game()
                    waiting=False

# -------- Main Loop ---------
spawn_fruits()
running=True
while running:
    dt=clock.tick(FPS)
    screen.fill(WHITE)

    # Events
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        if not game_over and not level_complete and event.type==pygame.KEYDOWN:
            key=event.unicode.upper()
            found=False
            for f in fruits:
                if not f["cut"] and f["letter"]==key:
                    f["cut"]=True
                    # Fill box
                    for b in boxes:
                        if b["fruit"]==f["type"]:
                            b["fill"]+=0.2
                            if b["fill"]>1:b["fill"]=1
                            if fill_sound: fill_sound.play()
                    if cut_sound: cut_sound.play()
                    found=True
                    break
            if not found:
                game_over=True

    # Timer
    if not game_over and not level_complete:
        seconds=(pygame.time.get_ticks()-start_ticks)//1000
        timer=40-seconds
        if timer<=0:
            game_over=True

    # Update fruits
    if not game_over and not level_complete:
        for f in fruits[:]:
            if not f["cut"]:
                f["y"]+=fruit_speed
                if f["y"]>HEIGHT:
                    missed+=1
                    if missed>=MAX_MISS:
                        game_over=True
                    fruits.remove(f)
        # Respawn fruits when all cut or missed
        if all(f["cut"] or f["y"]>HEIGHT for f in fruits):
            spawn_fruits()
            fruit_speed+=0.1

    # Draw fruits
    for f in fruits:
        if not f["cut"]:
            screen.blit(f["image"],(f["x"],f["y"]))
            draw_text(f["letter"],28,BLACK,f["x"]+35,f["y"]+10)

    # Draw boxes
    draw_boxes()

    # HUD
    draw_text(f"Score: {score}",28,BLACK,10,10,center=False)
    draw_text(f"Time: {timer}",28,BLACK,WIDTH-150,10,center=False)
    draw_text(f"Missed: {missed}/{MAX_MISS}",28,RED,10,50,center=False)

    # Check level complete
    if all(b["fill"]>=1 for b in boxes) and not game_over:
        level_complete=True
        if level<max_level:
            level+=1
            level_screen()
            # Reset boxes fill
            for b in boxes:
                b["fill"]=0
                b["score_given"]=False
            missed=0
            timer=40
            start_ticks=pygame.time.get_ticks()
            fruit_speed=1.2
            spawn_fruits()
            level_complete=False
        else:
            # Last level completed
            draw_text("YOU COMPLETED ALL LEVELS!",36,BLUE,WIDTH//2,HEIGHT//2)
            pygame.display.flip()
            pygame.time.wait(3000)
            pygame.quit();sys.exit()

    if game_over:
        game_over_screen()

    pygame.display.flip()

pygame.quit()