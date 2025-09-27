# flappy_bird/main.py
"""
Step 1 — Blank Pygame window for PyFlappy.
Replace this file with later milestones as we add features.
"""
import os
import sys
import math
import random  # for pipe gap positioning
import pygame

# Paths (defined early to avoid reference-order issues)
ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(ROOT, "assets")
SOUNDS_DIR = os.path.join(ROOT, "sounds")
SCORE_FILE = os.path.join(ROOT, "score.txt")

# Optional pixel font support
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
FONT_CANDIDATES = [
    # Common file names to look for (place in assets/fonts/)
    "StardewValley.ttf",
    "Stardew_Valley.ttf",
    "stardewvalley.ttf",
    "Stardew-Valley.ttf",
    "PressStart2P.ttf",
    "PressStart2P-Regular.ttf",
    "Press_Start_2P.ttf",
    "Press_Start_2P-Regular.ttf",
    "Joystix.ttf",
    "joystix monospace.ttf",
    "PixelOperator.ttf",
    "PixelOperator8.ttf",
]

FONT_AA = False  # Disable antialiasing for crisp pixel look
SHADOW_OFFSET = (1, 1)

def find_font_file():
    """Return a path to a pixel font TTF if available, otherwise None.
    Look in assets/ and assets/fonts/ for common pixel font filenames.
    """
    search_dirs = [ASSETS_DIR, FONTS_DIR]
    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for name in FONT_CANDIDATES:
            p = os.path.join(d, name)
            if os.path.exists(p):
                return p
    return None

FONT_PATH = find_font_file()

def get_font(size):
    """Load the pixel font if available, else fallback to a retro-like sysfont."""
    if FONT_PATH:
        try:
            return pygame.font.Font(FONT_PATH, size)
        except Exception:
            pass
    # Fallbacks: try some mono/retro system fonts in order
    fallback_names = [
        "stardew valley", "pressstart2p", "joystix monospace", "joystix", "m6x11", "vt323", "menlo", "monaco", "couriernew", "courier", "monospace"
    ]
    for name in fallback_names:
        try:
            f = pygame.font.SysFont(name, size)
            if f:
                try:
                    f.set_bold(True)
                except Exception:
                    pass
                return f
        except Exception:
            continue
    # Last resort: default font
    return pygame.font.SysFont(None, size)

def render_text(text, font, color, shadow=True, outline=0, outline_color=(0, 0, 0)):
    """Render text with optional drop shadow and pixel outline for a bold, readable look.
    outline: integer pixels of outline thickness (0 for none).
    """
    main = font.render(text, FONT_AA, color).convert_alpha()

    # Prepare base surface size
    extra_w = abs(SHADOW_OFFSET[0]) if shadow else 0
    extra_h = abs(SHADOW_OFFSET[1]) if shadow else 0
    pad = max(0, outline)
    w = main.get_width() + extra_w + pad * 2
    h = main.get_height() + extra_h + pad * 2
    out = pygame.Surface((w, h), pygame.SRCALPHA)

    # Outline pass
    if outline > 0:
        outline_surf = font.render(text, FONT_AA, outline_color).convert_alpha()
        # 8-directional outline for chunky pixel border
        for dx in range(-outline, outline + 1):
            for dy in range(-outline, outline + 1):
                if dx == 0 and dy == 0:
                    continue
                out.blit(outline_surf, (pad + dx, pad + dy))

    # Shadow pass (drawn after outline to peek outside)
    if shadow:
        shadow_surf = font.render(text, FONT_AA, (0, 0, 0)).convert_alpha()
        out.blit(shadow_surf, (pad + SHADOW_OFFSET[0], pad + SHADOW_OFFSET[1]))

    # Main text
    out.blit(main, (pad, pad))
    return out

# --- Constants ---
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
FPS = 60
BG_COLOR = (78, 192, 202)  # sky blue
 
# Bird physics
BIRD_START_X = SCREEN_WIDTH // 4
BIRD_START_Y = SCREEN_HEIGHT // 2
BIRD_WIDTH = 34
BIRD_HEIGHT = 24
GRAVITY = 800.0  # pixels per second^2 (tunable)
MAX_FALL_SPEED = 1000.0
FLAP_STRENGTH = 300.0  # initial upward velocity applied on flap (pixels/sec)

# Pipe settings
PIPE_WIDTH = 52
PIPE_GAP = 100  # vertical gap between pipes
PIPE_SPEED = 120  # pixels per second
PIPE_SPAWN_DELAY = 2.0  # seconds between pipe spawns
PIPE_MIN_HEIGHT = 50  # minimum height of pipe
PIPE_COLOR = (67, 176, 71)  # green color for pipes

# Game states
GAME_MENU = 'menu'      # Initial menu state
GAME_READY = 'ready'    # Bird is visible, waiting for first flap
GAME_RUNNING = 'running'
GAME_OVER = 'game_over'

# Colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 215, 0)  # Score color
BLACK = (0, 0, 0)
BRONZE = (205, 127, 50)
SILVER = (192, 192, 192)
GOLD = (255, 215, 0)
PLATINUM = (229, 228, 226)

# Fonts
TITLE_FONT_SIZE = 34
SCORE_FONT_SIZE = 40
MENU_FONT_SIZE = 18
DEBUG_FONT_SIZE = 14

# Medal thresholds
MEDAL_SCORES = [
    (30, "Platinum", PLATINUM),
    (20, "Gold", GOLD),
    (10, "Silver", SILVER),
    (5, "Bronze", BRONZE)
]

# Animation
BIRD_IDLE_RANGE = 20  # pixels up/down
BIRD_IDLE_SPEED = 2   # complete cycles per second

# Ground
GROUND_HEIGHT = 112
GROUND_Y = SCREEN_HEIGHT - GROUND_HEIGHT
# Keep pipes below this HUD area to avoid overlapping score/title
HUD_TOP_MARGIN = 68

def load_high_score():
    """Load the high score from score.txt."""
    try:
        with open(SCORE_FILE, 'r') as f:
            return int(f.read().strip())
    except (IOError, ValueError):
        return 0

def save_high_score(score):
    """Save the high score to score.txt."""
    try:
        with open(SCORE_FILE, 'w') as f:
            f.write(str(score))
    except IOError:
        print(f"Warning: Could not save high score to {SCORE_FILE}")

def get_medal(score):
    """Return (medal_name, color) tuple based on score, or None if no medal."""
    for threshold, name, color in MEDAL_SCORES:
        if score >= threshold:
            return name, color
    return None

def init_pygame():
    """Initialize pygame and return (screen, clock)."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("PyFlappy — Step 5")
    clock = pygame.time.Clock()
    return screen, clock

class Bird:
    """Simple bird with vertical physics (gravity). No flap yet.

    Position and velocity are float to avoid jitter; rect is used for drawing
    and collision checks in later milestones.
    """
    def __init__(self, x=BIRD_START_X, y=BIRD_START_Y):
        self.x = float(x)
        self.y = float(y)
        self.start_y = float(y)  # For menu animation
        self.vel = 0.0  # pixels per second (positive downward)
        
        self.frames = []
        self.current_frame = 0
        self.animation_speed = 10 # frames per second
        self.animation_time = 0.0

        try:
            spritesheet = pygame.image.load(os.path.join(ASSETS_DIR, "bird1.png")).convert_alpha()
            
            # Assuming 3 frames in a horizontal strip
            frame_width = spritesheet.get_width() // 3
            frame_height = spritesheet.get_height()
            
            scale_factor = 2
            self.width = int(frame_width * scale_factor)
            self.height = int(frame_height * scale_factor)

            for i in range(3):
                frame = spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                frame = pygame.transform.scale(frame, (self.width, self.height))
                self.frames.append(frame)
            
            self.image = self.frames[0]

        except Exception as e:
            print(f"Failed to load bird spritesheet: {e}")
            self.image = None
            self.width = BIRD_WIDTH
            self.height = BIRD_HEIGHT

        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def update_menu(self, dt):
        """Update bird's menu idle animation."""
        self.animation_time += dt * BIRD_IDLE_SPEED
        # Smooth sine wave animation
        offset = math.sin(self.animation_time * 2 * math.pi) * BIRD_IDLE_RANGE
        self.y = self.start_y + offset
        self.rect.y = int(self.y)

    def update(self, dt):
        """Update bird physics. dt is seconds since last frame."""
        # Animate the bird
        self.animation_time += dt
        if self.animation_time > 1 / self.animation_speed:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.animation_time = 0

        # Integrate gravity
        self.vel += GRAVITY * dt
        if self.vel > MAX_FALL_SPEED:
            self.vel = MAX_FALL_SPEED

        # Update position
        self.y += self.vel * dt

        # Update rect for drawing / collisions
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Ground collision check (simple version for now)
        if self.rect.bottom > GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.y = self.rect.y
            self.vel = 0

    def flap(self):
        """Apply an instantaneous upward velocity to the bird (flap).

        This sets the bird's vertical velocity to a fixed negative value so the
        next update will move the bird upward against gravity.
        """
        # Negative velocity moves the bird upward because positive vel = down
        self.vel = -FLAP_STRENGTH

    def check_collision(self, pipes, ground):
        """Check if bird collides with pipes or ground."""
        # Ground collision
        if self.rect.bottom >= ground.rect.top:
            return True
            
        # Pipe collision
        for pipe in pipes:
            if self.rect.colliderect(pipe.top_rect) or \
               self.rect.colliderect(pipe.bottom_rect):
                return True
        
        return False

    def draw(self, surface, game_state):
        """Draw the bird, with red tint if game over."""
        if self.image:
            if game_state == GAME_OVER:
                # Create a red surface for tinting
                red_surface = pygame.Surface(self.image.get_size()).convert_alpha()
                red_surface.fill(RED)
                temp_image = self.image.copy()
                temp_image.blit(red_surface, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(temp_image, (int(self.x), int(self.y)))
            else:
                surface.blit(self.image, (int(self.x), int(self.y)))
        else:
            # placeholder: yellow rectangle with black border (red if game over)
            color = RED if game_state == GAME_OVER else (255, 215, 0)
            pygame.draw.rect(surface, color, self.rect)
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)

class Pipe:
    """A pair of pipes (top and bottom) that move left across the screen."""
    def __init__(self, x=SCREEN_WIDTH):
        self.x = float(x)
        self.scored = False  # Flag to ensure we only score once per pipe
        
        # Randomly position the gap
        gap_y = random.randint(
            max(PIPE_MIN_HEIGHT + PIPE_GAP, HUD_TOP_MARGIN + PIPE_GAP // 2),
            GROUND_Y - PIPE_MIN_HEIGHT - PIPE_GAP
        )
        
        # Create the top and bottom pipe rectangles
        self.top_rect = pygame.Rect(
            int(self.x),
            0,
            PIPE_WIDTH,
            gap_y - PIPE_GAP // 2
        )
        
        self.bottom_rect = pygame.Rect(
            int(self.x),
            gap_y + PIPE_GAP // 2,
            PIPE_WIDTH,
            GROUND_Y - (gap_y + PIPE_GAP // 2)
        )
        
        # Optional: Load pipe image
        self.image = None
        try:
            img_path = os.path.join(ASSETS_DIR, "pipe.png")
            if os.path.exists(img_path):
                self.image = pygame.image.load(img_path).convert_alpha()
                # We'll need to scale and flip for top pipe
        except Exception:
            self.image = None
    
    def update(self, dt):
        """Move pipe left at constant speed."""
        self.x -= PIPE_SPEED * dt
        self.top_rect.x = int(self.x)
        self.bottom_rect.x = int(self.x)
    
    def is_offscreen(self):
        """Return True if pipe has moved completely off the left side."""
        return self.x + PIPE_WIDTH < 0
    
    def draw(self, surface):
        if self.image:
            # Draw top pipe (flipped)
            flipped_image = pygame.transform.flip(self.image, False, True)
            surface.blit(flipped_image, (self.top_rect.x, self.top_rect.bottom - flipped_image.get_height()))

            # Draw bottom pipe
            surface.blit(self.image, self.bottom_rect.topleft)
        else:
            # Placeholder: green rectangles with black borders
            pygame.draw.rect(surface, PIPE_COLOR, self.top_rect)
            pygame.draw.rect(surface, (0, 0, 0), self.top_rect, 2)
            pygame.draw.rect(surface, PIPE_COLOR, self.bottom_rect)
            pygame.draw.rect(surface, (0, 0, 0), self.bottom_rect, 2)


class Ground:
    """A simple static ground for rendering and collision."""
    def __init__(self):
        self.rect = pygame.Rect(0, GROUND_Y, SCREEN_WIDTH, GROUND_HEIGHT)
        # Optional: Load ground image
        self.image = None
        try:
            img_path = os.path.join(ASSETS_DIR, "ground.png")
            if os.path.exists(img_path):
                self.image = pygame.image.load(img_path).convert()
                self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, GROUND_HEIGHT))
        except Exception:
            self.image = None

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect)
        else:
            # Placeholder: brown rectangle
            pygame.draw.rect(surface, (222, 184, 135), self.rect) # BurlyWood color
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)


def main():
    """Main loop — shows a bird that falls and stops at the ground."""
    try:
        screen, clock = init_pygame()
    except Exception as e:
        print("Failed to initialize pygame:", e)
        sys.exit(1)

    # Fonts for different purposes (pixel font if available)
    title_font = get_font(TITLE_FONT_SIZE)
    menu_font = get_font(MENU_FONT_SIZE)
    score_font = get_font(SCORE_FONT_SIZE)
    debug_font = get_font(DEBUG_FONT_SIZE)
    
    # Static text surfaces (rendered with shadow for contrast)
    title_surf = render_text("PyFlappy", title_font, WHITE, shadow=False, outline=1)
    menu_surf = render_text("Press SPACE to Start", menu_font, WHITE, shadow=False, outline=1)
    ready_surf = render_text("READY! Press SPACE to Flap!", menu_font, WHITE, shadow=False, outline=1)
    game_over_surf = render_text("Game Over! Press SPACE to Restart", menu_font, (240, 80, 80), shadow=False, outline=1)
    menu_quit_surf = render_text("ESC to Quit", debug_font, WHITE, shadow=False, outline=1)

    def reset_game(to_menu=False):
        """Reset the game state for a new attempt."""
        nonlocal bird, pipes, time_since_last_pipe, game_state, current_score
        bird = Bird()
        pipes = []
        time_since_last_pipe = 0.0
        game_state = GAME_MENU if to_menu else GAME_READY
        current_score = 0

    # Create game objects and score tracking
    bird = Bird()
    ground = Ground()
    pipes = []  # List to hold active pipes
    time_since_last_pipe = 0.0  # Timer for pipe spawning
    game_state = GAME_MENU  # Start in menu state
    current_score = 0
    best_score = load_high_score()  # Load the all-time best score

    running = True
    last_time = pygame.time.get_ticks() / 1000.0
    while running:
        now = pygame.time.get_ticks() / 1000.0
        dt = now - last_time
        last_time = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if game_state == GAME_MENU:
                        game_state = GAME_READY
                    elif game_state == GAME_READY:
                        game_state = GAME_RUNNING
                        bird.flap()  # Initial flap
                    elif game_state == GAME_RUNNING:
                        bird.flap()
                    elif game_state == GAME_OVER:
                        reset_game(to_menu=True)

        # Update game objects based on state
        if game_state == GAME_MENU or game_state == GAME_READY:
            bird.update_menu(dt)
        elif game_state == GAME_RUNNING:
            bird.update(dt)
            
            # Check for collisions
            if bird.check_collision(pipes, ground):
                game_state = GAME_OVER
                # Update and save high score if needed
                if current_score > best_score:
                    best_score = current_score
                    save_high_score(best_score)
            
            # Update pipes and spawn new ones
            time_since_last_pipe += dt
            if time_since_last_pipe >= PIPE_SPAWN_DELAY:
                try:
                    pipes.append(Pipe())
                    time_since_last_pipe = 0.0
                except Exception as e:
                    print(f"Failed to create pipe: {e}")
                    time_since_last_pipe = PIPE_SPAWN_DELAY  # Try again next frame

            # Check for score increases
            for pipe in pipes:
                if not pipe.scored and pipe.x + PIPE_WIDTH < bird.x:
                    current_score += 1
                    pipe.scored = True  # Mark as scored
                    if current_score > best_score:
                        best_score = current_score
                
            # Update and filter out off-screen pipes
            pipes = [pipe for pipe in pipes if not pipe.is_offscreen()]
            for pipe in pipes:
                pipe.update(dt)

        # Drawing
        screen.fill(BG_COLOR)
        for pipe in pipes:  # Draw pipes behind bird
            pipe.draw(screen)
        bird.draw(screen, game_state)
        ground.draw(screen)  # Ground always on top

        # Always show title at top
        title_rect = title_surf.get_rect(midtop=(SCREEN_WIDTH // 2, 6))
        screen.blit(title_surf, title_rect)

        # State-specific UI
        if game_state == GAME_MENU:
            # Center the "Press SPACE to Start" text
            menu_rect = menu_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(menu_surf, menu_rect)
            # Show quit instruction at bottom
            quit_rect = menu_quit_surf.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
            screen.blit(menu_quit_surf, quit_rect)

        elif game_state == GAME_READY:
            ready_rect = ready_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(ready_surf, ready_rect)

        elif game_state == GAME_RUNNING:
            # Score display (centered, clean with shadow only)
            score_text = str(current_score)
            score_surf = render_text(score_text, score_font, YELLOW, shadow=False, outline=1)
            score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, 48))
            screen.blit(score_surf, score_rect)

        elif game_state == GAME_OVER:
            center_y = SCREEN_HEIGHT // 2

            # Show game over text at top
            game_over_rect = game_over_surf.get_rect(center=(SCREEN_WIDTH // 2, center_y - 80))
            screen.blit(game_over_surf, game_over_rect)
            
            # Show final and best scores (shadowed for contrast)
            final_score_surf = render_text(f"Score: {current_score}", menu_font, WHITE, shadow=False, outline=1)
            best_score_surf = render_text(f"Best: {best_score}", menu_font, YELLOW, shadow=False, outline=1)
            
            final_score_rect = final_score_surf.get_rect(center=(SCREEN_WIDTH // 2, center_y - 20))
            best_score_rect = best_score_surf.get_rect(center=(SCREEN_WIDTH // 2, center_y + 20))
            
            screen.blit(final_score_surf, final_score_rect)
            screen.blit(best_score_surf, best_score_rect)

            # Show medal if earned
            medal = get_medal(current_score)
            if medal:
                medal_name, medal_color = medal
                medal_surf = render_text(f"{medal_name} Medal!", menu_font, medal_color, shadow=False, outline=1)
                medal_rect = medal_surf.get_rect(center=(SCREEN_WIDTH // 2, center_y + 60))
                
                # Draw medal circle background
                circle_radius = 30
                circle_pos = (medal_rect.centerx, medal_rect.centery + 40)
                pygame.draw.circle(screen, medal_color, circle_pos, circle_radius)
                pygame.draw.circle(screen, BLACK, circle_pos, circle_radius, 2)
                
                # Draw star or trophy in medal (simple version)
                star_points = []
                for i in range(5):
                    angle = -math.pi/2 + (2*math.pi*i)/5
                    x = circle_pos[0] + circle_radius*0.7 * math.cos(angle)
                    y = circle_pos[1] + circle_radius*0.7 * math.sin(angle)
                    star_points.append((int(x), int(y)))
                pygame.draw.polygon(screen, BLACK, star_points, 2)
                
                screen.blit(medal_surf, medal_rect)

        # Debug info at bottom-left
        debug_surf = render_text(
            f"assets: {os.path.basename(ASSETS_DIR)}  sounds: {os.path.basename(SOUNDS_DIR)}",
            debug_font,
            (240, 240, 240),
            shadow=False,
            outline=1,
        )
        fps_surf = render_text(
            f"FPS: {int(clock.get_fps())}",
            debug_font,
            (240, 240, 240),
            shadow=False,
            outline=1,
        )
        screen.blit(debug_surf, (12, SCREEN_HEIGHT - 36))
        screen.blit(fps_surf, (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 36))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
