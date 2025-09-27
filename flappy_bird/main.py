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

# Fonts
TITLE_FONT_SIZE = 48
SCORE_FONT_SIZE = 64
MENU_FONT_SIZE = 32
DEBUG_FONT_SIZE = 20

# Animation
BIRD_IDLE_RANGE = 20  # pixels up/down
BIRD_IDLE_SPEED = 2   # complete cycles per second

# Ground
GROUND_HEIGHT = 112
GROUND_Y = SCREEN_HEIGHT - GROUND_HEIGHT

# Paths
ROOT = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(ROOT, "assets")
SOUNDS_DIR = os.path.join(ROOT, "sounds")

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
        self.width = BIRD_WIDTH
        self.height = BIRD_HEIGHT
        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        self.animation_time = 0.0  # For menu idle animation
        # Try to load an image from assets if present (optional)
        self.image = None
        try:
            img_path = os.path.join(ASSETS_DIR, "bird1.png")
            if os.path.exists(img_path):
                self.image = pygame.image.load(img_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except Exception:
            self.image = None

    def update_menu(self, dt):
        """Update bird's menu idle animation."""
        self.animation_time += dt * BIRD_IDLE_SPEED
        # Smooth sine wave animation
        offset = math.sin(self.animation_time * 2 * math.pi) * BIRD_IDLE_RANGE
        self.y = self.start_y + offset
        self.rect.y = int(self.y)

    def update(self, dt):
        """Update bird physics. dt is seconds since last frame."""
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
            PIPE_MIN_HEIGHT + PIPE_GAP,
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
            scaled_image = pygame.transform.scale(
                self.image,
                (PIPE_WIDTH, self.top_rect.height)
            )
            flipped_image = pygame.transform.flip(scaled_image, False, True)
            surface.blit(flipped_image, self.top_rect)
            
            # Draw bottom pipe
            scaled_image = pygame.transform.scale(
                self.image,
                (PIPE_WIDTH, self.bottom_rect.height)
            )
            surface.blit(scaled_image, self.bottom_rect)
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

    # Fonts for different purposes
    title_font = pygame.font.SysFont(None, TITLE_FONT_SIZE)
    menu_font = pygame.font.SysFont(None, MENU_FONT_SIZE)
    score_font = pygame.font.SysFont(None, SCORE_FONT_SIZE)
    debug_font = pygame.font.SysFont(None, DEBUG_FONT_SIZE)
    
    # Static text surfaces
    title_surf = title_font.render("PyFlappy", True, WHITE)
    menu_surf = menu_font.render("Press SPACE to Start", True, WHITE)
    ready_surf = menu_font.render("READY! Press SPACE to Flap!", True, WHITE)
    game_over_surf = menu_font.render("Game Over! Press SPACE to Restart", True, RED)
    menu_quit_surf = debug_font.render("ESC to Quit", True, WHITE)

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
    best_score = 0  # Best score this session

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
        title_rect = title_surf.get_rect(midtop=(SCREEN_WIDTH // 2, 20))
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
            # Score display (centered, large)
            score_text = str(current_score)
            score_surf = score_font.render(score_text, True, YELLOW)
            score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, 80))
            screen.blit(score_surf, score_rect)

        elif game_state == GAME_OVER:
            # Show game over text
            game_over_rect = game_over_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(game_over_surf, game_over_rect)
            
            # Show final and best scores
            final_score_surf = menu_font.render(f"Score: {current_score}", True, WHITE)
            best_score_surf = menu_font.render(f"Best: {best_score}", True, YELLOW)
            
            final_score_rect = final_score_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
            best_score_rect = best_score_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            
            screen.blit(final_score_surf, final_score_rect)
            screen.blit(best_score_surf, best_score_rect)

        # Debug info at bottom-left
        debug_surf = debug_font.render(
            f"assets: {os.path.basename(ASSETS_DIR)}  sounds: {os.path.basename(SOUNDS_DIR)}", 
            True, (240, 240, 240)
        )
        fps_surf = debug_font.render(f"FPS: {int(clock.get_fps())}", True, (240, 240, 240))
        screen.blit(debug_surf, (12, SCREEN_HEIGHT - 36))
        screen.blit(fps_surf, (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 36))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()