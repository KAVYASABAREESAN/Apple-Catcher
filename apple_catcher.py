import pygame
import random
import sqlite3
import tkinter as tk
from tkinter import simpledialog

# Setup DB
conn = sqlite3.connect("apple_game.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS player_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        score INTEGER NOT NULL
    );
""")
conn.commit()

# Use tkinter to get player name via GUI
root = tk.Tk()
root.withdraw()  # Hide the main tkinter window
player_name = simpledialog.askstring("Player Name", "Enter your name:")
if not player_name:
    player_name = "Player"

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 600, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🍎 Apple Catcher Game")

font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
APPLE_RED = (255, 0, 0)
BROWN = (139, 69, 19)
GRAY = (100, 100, 100)

# Game variables
basket = pygame.Rect(WIDTH // 2 - 40, HEIGHT - 50, 80, 20)
basket_speed = 7

apples = []
obstacles = []
score = 0
misses = 0
game_over = False

# Apple fall speed (reduced for smoother play)
fall_speed = 4

def draw_text(text, x, y, color=BLACK):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def drop_objects():
    if random.randint(1, 20) == 1:
        apples.append(pygame.Rect(random.randint(0, WIDTH - 20), 0, 20, 20))
    if random.randint(1, 30) == 1:
        obstacles.append(pygame.Rect(random.randint(0, WIDTH - 20), 0, 20, 20))

def move_objects(objects, speed=fall_speed):
    for obj in objects:
        obj.y += speed

def remove_offscreen(objects):
    return [obj for obj in objects if obj.y < HEIGHT]

def check_collisions():
    global score, misses
    for apple in apples[:]:
        if basket.colliderect(apple):
            apples.remove(apple)
            score += 1
    for obs in obstacles[:]:
        if basket.colliderect(obs):
            obstacles.remove(obs)
            misses += 1

# Main game loop
while not game_over:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and basket.left > 0:
        basket.x -= basket_speed
    if keys[pygame.K_RIGHT] and basket.right < WIDTH:
        basket.x += basket_speed

    drop_objects()
    move_objects(apples)
    move_objects(obstacles)
    check_collisions()

    apples = remove_offscreen(apples)
    obstacles = remove_offscreen(obstacles)

    pygame.draw.rect(screen, BROWN, basket)
    for apple in apples:
        pygame.draw.ellipse(screen, APPLE_RED, apple)
    for obs in obstacles:
        pygame.draw.rect(screen, GRAY, obs)

    draw_text(f"Score: {score}", 10, 10)
    draw_text(f"Misses: {misses}/5", 10, 40)

    if misses >= 5:
        game_over = True

    pygame.display.flip()
    clock.tick(60)

# Game over screen
screen.fill(WHITE)
draw_text("Game Over!", WIDTH // 2 - 80, HEIGHT // 2 - 30)
draw_text(f"Final Score: {score}", WIDTH // 2 - 90, HEIGHT // 2 + 10)
pygame.display.flip()
pygame.time.wait(2000)

# Save score to database
cursor.execute("INSERT INTO player_scores (name, score) VALUES (?, ?)", (player_name, score))
conn.commit()

# Display previous scores
print("\n🏆 Players who have played the game:")
cursor.execute("SELECT name, score FROM player_scores ORDER BY score DESC")
results = cursor.fetchall()
for row in results:
    print(f"{row[0]}: {row[1]}")

conn.close()
pygame.quit()
