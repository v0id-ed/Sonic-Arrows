import pygame
import random
import sys
import os
from PIL import Image, ImageSequence

pygame.init()

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Evo Run! Endless Arrow Lapse")
CLOCK = pygame.time.Clock()
FPS = 60

# ---------------- COLORS ----------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
YELLOW = (255, 251, 0)
GREEN = (0, 220, 0)
SONIC_BLUE = (0, 112, 221)

BAR_Y = HEIGHT // 2
BOX_SIZE = 40

FONT = pygame.font.SysFont(None, 36)
BIG_FONT = pygame.font.SysFont(None, 64)

READY_TIME = 800
GO_TIME = 600
POP_DURATION = 300

# ---------------- LOAD & ANIMATE SONIC GIF ----------------
GIF_PATH = os.path.join("gifs", "Sonic.gif")
gif = Image.open(GIF_PATH)

SONIC_FRAMES = []
SONIC_DURATIONS = []

MAX_WIDTH = WIDTH * 0.6
MAX_HEIGHT = HEIGHT * 0.4

for frame in ImageSequence.Iterator(gif):
    frame = frame.convert("RGBA")

    w, h = frame.size
    scale = min(MAX_WIDTH / w, MAX_HEIGHT / h, 1)
    new_size = (int(w * scale), int(h * scale))
    frame = frame.resize(new_size, Image.LANCZOS)

    surface = pygame.image.fromstring(
        frame.tobytes(), frame.size, frame.mode
    ).convert_alpha()

    SONIC_FRAMES.append(surface)
    SONIC_DURATIONS.append(frame.info.get("duration", 100))

sonic_frame_index = 0
sonic_last_update = pygame.time.get_ticks()

def draw_sonic_gif():
    global sonic_frame_index, sonic_last_update

    now = pygame.time.get_ticks()
    if now - sonic_last_update >= SONIC_DURATIONS[sonic_frame_index]:
        sonic_frame_index = (sonic_frame_index + 1) % len(SONIC_FRAMES)
        sonic_last_update = now

    frame = SONIC_FRAMES[sonic_frame_index]
    rect = frame.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    SCREEN.blit(frame, rect)

# ---------------- BUTTON ----------------
class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text

    def draw(self, color):
        pygame.draw.rect(SCREEN, color, self.rect, border_radius=8)
        txt = FONT.render(self.text, True, WHITE)
        SCREEN.blit(txt, txt.get_rect(center=self.rect.center))

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# ---------------- ARROW BOX ----------------
class ArrowBox:
    def __init__(self, arrow):
        self.arrow = arrow
        self.y = BAR_Y
        self.x = {
            "left": WIDTH * 0.25 - BOX_SIZE // 2,
            "right": WIDTH * 0.75 - BOX_SIZE // 2,
            "up": WIDTH // 2 - BOX_SIZE // 2,
            "down": WIDTH // 2 - BOX_SIZE // 2
        }[arrow]
        self.rect = pygame.Rect(self.x, self.y, BOX_SIZE, BOX_SIZE)

    def update(self, speed):
        self.y += speed
        self.rect.y = self.y

    def draw(self):
        pygame.draw.rect(SCREEN, SONIC_BLUE, self.rect, border_radius=6)
        cx, cy = self.rect.center
        s = 10
        shapes = {
            "up": [(cx, cy - s), (cx - s, cy + s), (cx + s, cy + s)],
            "down": [(cx, cy + s), (cx - s, cy - s), (cx + s, cy - s)],
            "left": [(cx - s, cy), (cx + s, cy - s), (cx + s, cy + s)],
            "right": [(cx + s, cy), (cx - s, cy - s), (cx - s, cy + s)]
        }
        pygame.draw.polygon(SCREEN, WHITE, shapes[self.arrow])

# ---------------- GAME STATE ----------------
def reset_game():
    return {
        "boxes": [],
        "queue": [],
        "spawn_timer": 0,
        "speed": 2.5,
        "start_time": 0,
        "game_over": False,
        "early_fail": False,
        "rank": None,
        "time_text": "",
        "countdown": True,
        "countdown_phase": "ready",
        "countdown_timer": pygame.time.get_ticks()
    }

game_started = False
game = reset_game()

start_button = Button((WIDTH // 2 - 75, BAR_Y + 100, 150, 50), "Start")
play_again_button = Button((WIDTH // 2 - 100, HEIGHT - 70, 200, 50), "Play Again")

# ---------------- GAME OVER ----------------
def trigger_game_over():
    game["game_over"] = True
    elapsed = (pygame.time.get_ticks() - game["start_time"]) / 1000

    if elapsed >= 180:
        game["rank"] = "S"
    elif elapsed >= 120:
        game["rank"] = "A"
    elif elapsed >= 60:
        game["rank"] = "B"
    elif elapsed >= 30:
        game["rank"] = "C"
    else:
        game["early_fail"] = True

    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    game["time_text"] = f"{minutes}:{seconds:02d}"

# ---------------- MAIN LOOP ----------------
while True:
    CLOCK.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if not game_started:
            if start_button.clicked(event) or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN
            ):
                game_started = True
                game = reset_game()

        elif game["game_over"]:
            if play_again_button.clicked(event) or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN
            ):
                game_started = False
                game = reset_game()

        elif not game["countdown"] and event.type == pygame.KEYDOWN and game["queue"]:
            key_map = {
                pygame.K_LEFT: "left",
                pygame.K_RIGHT: "right",
                pygame.K_UP: "up",
                pygame.K_DOWN: "down"
            }
            if event.key in key_map:
                if key_map[event.key] == game["queue"][0]:
                    game["queue"].pop(0)
                    game["boxes"].pop(0)
                else:
                    trigger_game_over()

    SCREEN.fill(BLACK)
    pygame.draw.rect(SCREEN, SONIC_BLUE, (0, BAR_Y - 4, WIDTH, 8))

    # -------- START SCREEN --------
    if not game_started:
        draw_sonic_gif()

        SCREEN.blit(
            BIG_FONT.render("Sonic Arrow lapse!", True, SONIC_BLUE),
            (WIDTH // 2 - 195, BAR_Y // 2 - 40)
        )
        start_button.draw(SONIC_BLUE)

    # -------- GAME RUNNING --------
    elif not game["game_over"]:
        if game["countdown"]:
            now = pygame.time.get_ticks()
            elapsed = now - game["countdown_timer"]
            text = "Ready?" if game["countdown_phase"] == "ready" else "Go!"
            total = READY_TIME if text == "Ready?" else GO_TIME

            scale = min(elapsed / POP_DURATION, 1) * 0.5 + 0.5
            txt = pygame.transform.rotozoom(
                BIG_FONT.render(text, True, GREEN), 0, scale
            )
            SCREEN.blit(txt, txt.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.7))))

            if elapsed >= total:
                if game["countdown_phase"] == "ready":
                    game["countdown_phase"] = "go"
                    game["countdown_timer"] = now
                else:
                    game["countdown"] = False
                    game["start_time"] = pygame.time.get_ticks()
        else:
            game["spawn_timer"] += 1
            if game["spawn_timer"] >= 35:
                arrow = random.choice(["left", "right", "up", "down"])
                game["boxes"].append(ArrowBox(arrow))
                game["queue"].append(arrow)
                game["spawn_timer"] = 0
                game["speed"] += 0.05

            for box in game["boxes"]:
                box.update(game["speed"])
                box.draw()
                if box.y > HEIGHT:
                    trigger_game_over()

    # -------- GAME OVER --------
    else:
        pygame.draw.rect(SCREEN, RED, (0, BAR_Y, WIDTH, BAR_Y))
        SCREEN.blit(
            BIG_FONT.render("GAME OVER", True, BLACK),
            (WIDTH // 2 - 140, BAR_Y + BAR_Y // 2 - 40)
        )
        play_again_button.draw(SONIC_BLUE)

    pygame.display.flip()
