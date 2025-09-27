# flappy_bird/main.py
"""
Step 1 — Blank Pygame window for PyFlappy.
Replace this file with later milestones as we add features.
"""
import os
import sys
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
    pygame.display.set_caption("PyFlappy — Step 4")
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
    title_surf = font.render("PyFlappy — Step 4 (Ground Collision)", True, (255, 255, 255))
    instr_surf = font.render("Press SPACE to flap. Bird stops at ground.", True, (255, 255, 255))

    # Create instances (Step 4)
    bird = Bird()
    ground = Ground()

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

        # Drawing
        screen.fill(BG_COLOR)
        bird.draw(screen)
        ground.draw(screen) # Draw ground on top of background

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