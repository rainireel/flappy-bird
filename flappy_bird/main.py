# flappy_bird/main.py
"""
Step 1 — Blank Pygame window for PyFlappy.
Replace this file with later milestones as we add features.
"""
import os
import sys
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
        self.vel = 0.0  # pixels per second (positive downward)
        self.width = BIRD_WIDTH
        self.height = BIRD_HEIGHT
        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        # Try to load an image from assets if present (optional)
        self.image = None
        try:
            img_path = os.path.join(ASSETS_DIR, "bird1.png")
            if os.path.exists(img_path):
                self.image = pygame.image.load(img_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except Exception:
            self.image = None

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

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, (int(self.x), int(self.y)))
        else:
            # placeholder: yellow rectangle with black border
            pygame.draw.rect(surface, (255, 215, 0), self.rect)
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)

class Pipe:
    """A pair of pipes (top and bottom) that move left across the screen."""
    def __init__(self, x=SCREEN_WIDTH):
        self.x = float(x)
        
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

    # Simple font for on-screen instructions
    font = pygame.font.SysFont(None, 24)
    title_surf = font.render("PyFlappy — Step 5 (Pipes)", True, (255, 255, 255))
    instr_surf = font.render("Press SPACE to flap. Pipes scroll left.", True, (255, 255, 255))

    # Create game objects
    bird = Bird()
    ground = Ground()
    pipes = []  # List to hold active pipes
    time_since_last_pipe = 0.0  # Timer for pipe spawning

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
                elif event.key == pygame.K_SPACE:  # Flap on SPACE
                    bird.flap()

        # Update
        bird.update(dt)
        
        # Update pipes and spawn new ones
        time_since_last_pipe += dt
        if time_since_last_pipe >= PIPE_SPAWN_DELAY:
            try:
                pipes.append(Pipe())
                time_since_last_pipe = 0.0
            except Exception as e:
                print(f"Failed to create pipe: {e}")
                time_since_last_pipe = PIPE_SPAWN_DELAY  # Try again next frame
            
        # Update and filter out off-screen pipes
        pipes = [pipe for pipe in pipes if not pipe.is_offscreen()]
        for pipe in pipes:
            pipe.update(dt)

        # Drawing
        screen.fill(BG_COLOR)
        for pipe in pipes:  # Draw pipes behind bird
            pipe.draw(screen)
        bird.draw(screen)
        ground.draw(screen)  # Ground always on top

        # UI text on top of everything
        screen.blit(title_surf, (12, 12))
        screen.blit(instr_surf, (12, 36))

        # debug: show assets and sounds folder names and FPS
        debug_surf = font.render(f"assets: {os.path.basename(ASSETS_DIR)}  sounds: {os.path.basename(SOUNDS_DIR)}", True, (240, 240, 240))
        fps_surf = font.render(f"FPS: {int(clock.get_fps())}", True, (240, 240, 240))
        screen.blit(debug_surf, (12, SCREEN_HEIGHT - 36))
        screen.blit(fps_surf, (12, SCREEN_HEIGHT - 18))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()