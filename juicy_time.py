import pygame
import random
import sys

# ---------------- Initialization ----------------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Glass Game")
clock = pygame.time.Clock()
FPS = 60
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Fonts
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

# ---------------- Game Variables ----------------
score = 0
level = 1
timer = 40
fruit_speed = 5
spawn_rate = 1500
last_spawn = pygame.time.get_ticks()
game_over = False

# Load fruit images
fruit_images = {
    "Apple": pygame.image.load("apple.png"),
    "Orange": pygame.image.load("orange.png"),
    "Cherry": pygame.image.load("cherry.png"),
    "Mango": pygame.image.load("mango.png")
}
fruit_scale = (50, 50)
for key in fruit_images:
    fruit_images[key] = pygame.transform.scale(fruit_images[key], fruit_scale)

fruits = list(fruit_images.keys())
fruit_positions = []

# Glasses
glasses = [{"x": 150 + i*200, "y": 450, "filled": 0, "fruit": ""} for i in range(3)]

# Timer event
TIMER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TIMER_EVENT, 1000)

# Load sounds
cut_sound = pygame.mixer.Sound("cut.wav")
fill_sound = pygame.mixer.Sound("fill.wav")
game_over_sound = pygame.mixer.Sound("gameover.wav")
pygame.mixer.music.load("background.mp3")
pygame.mixer.music.play(-1)

# ---------------- Functions ----------------
def spawn_fruit():
    x = random.randint(50, WIDTH - 50)
    y = -50
    fruit_type = random.choice(fruits)
    fruit_positions.append({"x": x, "y": y, "type": fruit_type, "cut": False})

def draw_game():
    screen.fill(WHITE)
    
    # Draw fruits
    for f in fruit_positions:
        if not f["cut"]:
            screen.blit(fruit_images[f["type"]], (f["x"] - 25, int(f["y"]) - 25))
            name_text = small_font.render(f["type"], True, BLACK)
            screen.blit(name_text, (f["x"] - name_text.get_width()//2, f["y"] - 40))
    
    # Draw glasses
    for g in glasses:
        pygame.draw.rect(screen, BLACK, (g["x"], g["y"], 50, 100), 2)
        fill_height = int((g["filled"]/5)*100)
        pygame.draw.rect(screen, BLUE, (g["x"], g["y"]+100-fill_height, 50, fill_height))
        if g["fruit"]:
            glass_text = small_font.render(g["fruit"], True, BLACK)
            screen.blit(glass_text, (g["x"] + 25 - glass_text.get_width()//2, g["y"] + 110))
    
    # Score, Level, Timer
    score_text = font.render(f"Score: {score}", True, BLACK)
    level_text = font.render(f"Level: {level}", True, BLACK)
    timer_text = font.render(f"Time: {timer}", True, RED if timer <= 10 else BLACK)
    
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 50))
    screen.blit(timer_text, (WIDTH-150, 10))
    
    pygame.display.flip()

def cpu_assign_glass(fruit_type):
    # Match fruit type or pick empty / least filled glass
    for g in glasses:
        if g["fruit"] == fruit_type:
            g["filled"] += 1
            fill_sound.play()
            return g
    empty_glasses = [g for g in glasses if g["filled"] == 0]
    if empty_glasses:
        chosen = random.choice(empty_glasses)
    else:
        chosen = min(glasses, key=lambda x: x["filled"])
    chosen["fruit"] = fruit_type
    chosen["filled"] += 1
    fill_sound.play()
    return chosen

def check_fruit_click(pos):
    global score
    for f in fruit_positions:
        fruit_rect = pygame.Rect(f["x"]-25, f["y"]-25, 50, 50)
        if fruit_rect.collidepoint(pos) and not f["cut"]:
            f["cut"] = True
            cut_sound.play()
            cpu_assign_glass(f["type"])
            score += 10
            return

def show_game_over():
    pygame.mixer.music.stop()
    game_over_sound.play()
    screen.fill(WHITE)
    over_text = font.render(f"Game Over! Score: {score}", True, RED)
    screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 50))
    
    replay_text = font.render("Click to Replay", True, BLACK)
    screen.blit(replay_text, (WIDTH//2 - replay_text.get_width()//2, HEIGHT//2 + 20))
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
                reset_game()

def reset_game():
    global score, level, timer, fruit_speed, spawn_rate, last_spawn, fruit_positions, glasses, game_over
    score = 0
    level = 1
    timer = 40
    fruit_speed = 2
    spawn_rate = 1500
    last_spawn = pygame.time.get_ticks()
    fruit_positions = []
    glasses = [{"x": 150 + i*200, "y": 450, "filled": 0, "fruit": ""} for i in range(3)]
    game_over = False
    pygame.mixer.music.play(-1)

# ---------------- Main Loop ----------------
while True:
    clock.tick(FPS)
    current_time = pygame.time.get_ticks()
    
    if not game_over and current_time - last_spawn > spawn_rate:
        spawn_fruit()
        last_spawn = current_time
    
    # Move fruits
    for f in fruit_positions:
        if not f["cut"]:
            f["y"] += fruit_speed
            if f["y"] > HEIGHT:
                fruit_positions.remove(f)
    
    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            check_fruit_click(event.pos)
        if event.type == TIMER_EVENT and not game_over:
            timer -= 1
            if timer <= 0:
                game_over = True
    
    if game_over:
        show_game_over()
    
    draw_game()
    
    # Level up
    if score >= level * 50 and not game_over:
        level += 1
        timer = 40
        fruit_speed += 1
        spawn_rate = max(500, spawn_rate - 200)