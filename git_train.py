#!/usr/bin/env python3
"""
Epic Git Commit Train Visualizer
Shows your commits as train cars with animated scenery
Run: python git_train.py
Press ESC to exit
"""

import subprocess
import os
import sys
import random
import math
from datetime import datetime
import pygame
from pygame import gfxdraw

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
FPS = 60

# Colors
SKY_BLUE = (135, 206, 235)
SKY_DARKER = (100, 180, 220)
CLOUD_WHITE = (255, 255, 255)
CLOUD_SHADOW = (220, 220, 230)
GROUND_GREEN = (34, 139, 34)
GROUND_DARK = (25, 100, 25)
RAIL_BROWN = (101, 67, 33)
RAIL_DARK = (80, 50, 25)
RAIL_METAL = (192, 192, 192)
TRAIN_RED = (220, 20, 60)
TRAIN_DARK_RED = (139, 0, 0)
TRAIN_GOLD = (255, 215, 0)
TRAIN_BLACK = (30, 30, 30)
TRAIN_WHITE = (255, 255, 255)
WINDOW_BLUE = (173, 216, 230)
WHEEL_DARK = (40, 40, 40)
WHEEL_GRAY = (128, 128, 128)
COMMIT_GREEN = (50, 205, 50)
COMMIT_YELLOW = (255, 255, 0)
COMMIT_ORANGE = (255, 140, 0)
COMMIT_RED = (255, 69, 0)
COMMIT_BLUE = (30, 144, 255)
COMMIT_PURPLE = (138, 43, 226)
TREE_GREEN = (0, 100, 0)
TREE_DARK = (0, 60, 0)
TREE_TRUNK = (101, 67, 33)

class Cloud:
    def __init__(self, x, y, speed=1):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = random.randint(60, 120)
        self.puffs = []
        for _ in range(random.randint(4, 7)):
            offset_x = random.randint(-self.size//2, self.size//2)
            offset_y = random.randint(-self.size//4, self.size//4)
            radius = random.randint(self.size//4, self.size//2)
            self.puffs.append((offset_x, offset_y, radius))
    
    def update(self):
        # Move clouds to the right
        self.x += self.speed
        # Reset when they go off the RIGHT side
        if self.x > SCREEN_WIDTH + 200:
            self.x = -200
            self.y = random.randint(50, 200)
    
    def draw(self, screen):
        for offset_x, offset_y, radius in self.puffs:
            pygame.draw.circle(screen, CLOUD_WHITE, (int(self.x + offset_x), int(self.y + offset_y)), radius)
            pygame.draw.circle(screen, CLOUD_SHADOW, (int(self.x + offset_x), int(self.y + offset_y + 5)), radius - 5)

class Tree:
    def __init__(self, x, y, speed=3):
        self.x = x
        self.y = y
        self.speed = speed
        self.height = random.randint(80, 150)
        self.width = random.randint(40, 70)
        self.phase = random.uniform(0, 2 * math.pi)
    
    def update(self):
        # Move trees to the right
        self.x += self.speed
        # Reset when they go off the RIGHT side
        if self.x > SCREEN_WIDTH + 100:
            self.x = -100
            self.height = random.randint(80, 150)
    
    def draw(self, screen):
        # Trunk
        trunk_width = self.width // 4
        pygame.draw.rect(screen, TREE_TRUNK, (int(self.x - trunk_width//2), int(self.y - self.height * 0.3), trunk_width, int(self.height * 0.3)))
        
        # Leaves (triangle)
        leaf_height = self.height * 0.7
        points = [
            (int(self.x), int(self.y - self.height)),
            (int(self.x - self.width), int(self.y - leaf_height * 0.3)),
            (int(self.x + self.width), int(self.y - leaf_height * 0.3))
        ]
        pygame.draw.polygon(screen, TREE_GREEN, points)
        pygame.draw.polygon(screen, TREE_DARK, points, 3)
        
        # Add some detail
        pygame.draw.circle(screen, (0, 120, 0), (int(self.x), int(self.y - self.height * 0.6)), self.width // 4)

class TrainCar:
    def __init__(self, x, y, width=150, height=100, car_type="locomotive", commit_info=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.car_type = car_type
        self.commit_info = commit_info
        self.wheel_angle = 0
        self.bounce_offset = 0
        self.bounce_phase = random.uniform(0, 2 * math.pi)
    
    def update(self, wheel_rotation):
        self.wheel_angle = wheel_rotation
        self.bounce_phase += 0.05
        self.bounce_offset = math.sin(self.bounce_phase) * 2
    
    def draw(self, screen):
        car_y = self.y + self.bounce_offset
        
        if self.car_type == "locomotive":
            self.draw_locomotive(screen, car_y)
        else:
            self.draw_commit_car(screen, car_y)
    
    def draw_wheels(self, screen, car_x, car_y, num_wheels=4):
        wheel_radius = 15
        for i in range(num_wheels):
            wheel_x = car_x + 20 + (i * (self.width - 40) // max(1, num_wheels - 1))
            wheel_y = car_y + self.height - 10
            
            # Wheel
            pygame.draw.circle(screen, WHEEL_DARK, (int(wheel_x), int(wheel_y)), wheel_radius)
            pygame.draw.circle(screen, WHEEL_GRAY, (int(wheel_x), int(wheel_y)), wheel_radius - 3)
            
            # Spokes - rotate clockwise for forward motion (train moving left to right)
            for spoke in range(4):
                angle = -self.wheel_angle + (spoke * math.pi / 2)  # Negative for clockwise
                end_x = wheel_x + math.cos(angle) * (wheel_radius - 2)
                end_y = wheel_y + math.sin(angle) * (wheel_radius - 2)
                pygame.draw.line(screen, WHEEL_DARK, (int(wheel_x), int(wheel_y)), (int(end_x), int(end_y)), 2)
            
            # Hub
            pygame.draw.circle(screen, TRAIN_GOLD, (int(wheel_x), int(wheel_y)), 5)
    
    def draw_locomotive(self, screen, car_y):
        car_x = self.x
        
        # Main body
        pygame.draw.rect(screen, TRAIN_RED, (car_x, car_y, self.width, self.height), border_radius=10)
        pygame.draw.rect(screen, TRAIN_DARK_RED, (car_x, car_y, self.width, self.height), 3, border_radius=10)
        
        # Chimney
        pygame.draw.rect(screen, TRAIN_BLACK, (car_x + self.width - 30, car_y - 20, 20, 25))
        pygame.draw.rect(screen, TRAIN_BLACK, (car_x + self.width - 35, car_y - 25, 30, 8))
        
        # Windows
        pygame.draw.circle(screen, WINDOW_BLUE, (car_x + 30, car_y + 30), 18)
        pygame.draw.circle(screen, TRAIN_GOLD, (car_x + 30, car_y + 30), 18, 3)
        
        # Headlight
        pygame.draw.circle(screen, TRAIN_GOLD, (car_x + 10, car_y + 60), 12)
        pygame.draw.circle(screen, (255, 255, 200), (car_x + 8, car_y + 58), 6)
        
        # Gold trim
        pygame.draw.rect(screen, TRAIN_GOLD, (car_x, car_y, self.width, 5))
        pygame.draw.rect(screen, TRAIN_GOLD, (car_x, car_y + self.height - 5, self.width, 5))
        
        # Number
        font = pygame.font.Font(None, 36)
        text = font.render("GIT-1", True, TRAIN_GOLD)
        screen.blit(text, (car_x + self.width // 2 - 20, car_y + 40))
        
        self.draw_wheels(screen, car_x, car_y, 6)
    
    def draw_commit_car(self, screen, car_y):
        car_x = self.x
        
        # Determine color based on commit type
        if self.commit_info:
            commit_msg = self.commit_info.get('message', '')
            
            # Color based on commit characteristics
            if any(word in commit_msg.lower() for word in ['fix', 'bug']):
                body_color = COMMIT_RED
            elif any(word in commit_msg.lower() for word in ['add', 'new', 'feature']):
                body_color = COMMIT_GREEN
            elif any(word in commit_msg.lower() for word in ['update', 'improve']):
                body_color = COMMIT_BLUE
            elif any(word in commit_msg.lower() for word in ['merge', 'pull']):
                body_color = COMMIT_PURPLE
            else:
                body_color = COMMIT_ORANGE
        else:
            body_color = COMMIT_ORANGE
        
        # Main body
        pygame.draw.rect(screen, body_color, (car_x, car_y, self.width, self.height), border_radius=10)
        pygame.draw.rect(screen, TRAIN_BLACK, (car_x, car_y, self.width, self.height), 3, border_radius=10)
        
        # Roof
        pygame.draw.rect(screen, TRAIN_BLACK, (car_x + 10, car_y - 5, self.width - 20, 10), border_radius=5)
        
        # Connections
        pygame.draw.rect(screen, TRAIN_BLACK, (car_x - 15, car_y + self.height // 2 - 8, 15, 16))
        pygame.draw.rect(screen, TRAIN_BLACK, (car_x + self.width, car_y + self.height // 2 - 8, 15, 16))
        
        # Commit info display
        if self.commit_info:
            font_small = pygame.font.Font(None, 20)
            font_tiny = pygame.font.Font(None, 16)
            
            # Hash
            hash_short = self.commit_info.get('hash', '')[:7]
            hash_text = font_small.render(hash_short, True, TRAIN_GOLD)
            screen.blit(hash_text, (car_x + 15, car_y + 15))
            
            # Message (truncated)
            msg = self.commit_info.get('message', '')
            if len(msg) > 20:
                msg = msg[:17] + "..."
            
            # Split message into multiple lines if needed
            words = msg.split()
            lines = []
            current_line = ""
            for word in words:
                if len(current_line + " " + word) <= 15:
                    current_line += (" " if current_line else "") + word
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            # Use white text for better visibility on colored backgrounds
            for i, line in enumerate(lines[:2]):
                msg_text = font_tiny.render(line, True, TRAIN_WHITE)
                screen.blit(msg_text, (car_x + 15, car_y + 40 + i * 18))
            
            # Author
            author = self.commit_info.get('author', '')
            if len(author) > 15:
                author = author[:12] + "..."
            author_text = font_tiny.render(author, True, (200, 200, 200))
            screen.blit(author_text, (car_x + 15, car_y + self.height - 25))
        
        self.draw_wheels(screen, car_x, car_y, 4)

class SmokeParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(3, 8)
        self.alpha = 255
        self.vx = random.uniform(-2, -1)  # Smoke moves backward (left) - train moving forward
        self.vy = random.uniform(-2, -1)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.alpha -= 2
        self.radius += 0.1
    
    def draw(self, screen):
        if self.alpha > 0:
            smoke_surface = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(smoke_surface, (128, 128, 128, int(self.alpha)), 
                             (int(self.radius), int(self.radius)), int(self.radius))
            screen.blit(smoke_surface, (int(self.x - self.radius), int(self.y - self.radius)))

def get_git_commits(repo_path='.', limit=10):
    """Get git commits from repository"""
    try:
        # Check if it's a git repository
        if not os.path.exists(os.path.join(repo_path, '.git')):
            print(f"Warning: {repo_path} is not a git repository")
            return generate_sample_commits()
        
        # Get git log
        cmd = ['git', 'log', f'-{limit}', '--pretty=format:%H|%an|%s|%ad', '--date=short']
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("Warning: Could not get git log, using sample data")
            return generate_sample_commits()
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('|', 3)
                if len(parts) == 4:
                    commits.append({
                        'hash': parts[0],
                        'author': parts[1],
                        'message': parts[2],
                        'date': parts[3]
                    })
        
        return commits if commits else generate_sample_commits()
    
    except Exception as e:
        print(f"Error getting commits: {e}")
        return generate_sample_commits()

def generate_sample_commits():
    """Generate sample commits for demo"""
    sample_messages = [
        "Initial commit",
        "Add core features",
        "Fix critical bug",
        "Update documentation",
        "Add new feature",
        "Improve performance",
        "Merge pull request",
        "Refactor code",
        "Add tests",
        "Update dependencies"
    ]
    
    commits = []
    for i in range(len(sample_messages)):
        commits.append({
            'hash': f"{random.randint(0, 0xfffffff):07x}",
            'author': "developer",
            'message': sample_messages[i],
            'date': "2024-01-15"
        })
    return commits

def main():
    # Setup screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Git Commit Train - Epic Visualizer")
    clock = pygame.time.Clock()
    
    # Get commits
    commits = get_git_commits(limit=8)
    
    # Create background elements
    clouds = [Cloud(random.randint(0, SCREEN_WIDTH), random.randint(50, 200), random.uniform(0.5, 1.5)) for _ in range(5)]
    # Trees positioned lower (y=480, near the tracks)
    trees = [Tree(random.randint(0, SCREEN_WIDTH), 480, random.uniform(2, 4)) for _ in range(6)]
    
    # Create train
    train_cars = []
    train_x = 100
    car_width = 150
    car_height = 100
    train_y = 390  # Slightly adjusted for better positioning
    
    # Locomotive
    locomotive = TrainCar(train_x, train_y, car_width, car_height, "locomotive")
    train_cars.append(locomotive)
    
    # Commit cars
    for i, commit in enumerate(commits):
        car_x = train_x + (i + 1) * (car_width + 20)
        commit_car = TrainCar(car_x, train_y, car_width, car_height, "commit", commit)
        train_cars.append(commit_car)
    
    # Smoke particles
    smoke_particles = []
    smoke_timer = 0
    
    # Wheel rotation
    wheel_rotation = 0
    
    # Main game loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Update - rotate wheels clockwise for forward motion
        wheel_rotation += 0.1
        
        # Update clouds (moving backward - right to left)
        for cloud in clouds:
            cloud.update()
        
        # Update trees (moving backward - right to left)
        for tree in trees:
            tree.update()
        
        # Update train cars
        for car in train_cars:
            car.update(wheel_rotation)
        
        # Generate smoke from locomotive
        smoke_timer += 1
        if smoke_timer > 8:
            smoke_timer = 0
            chimney_x = train_cars[0].x + train_cars[0].width - 25
            chimney_y = train_cars[0].y - 25
            smoke_particles.append(SmokeParticle(chimney_x, chimney_y))
        
        # Update smoke
        smoke_particles = [p for p in smoke_particles if p.alpha > 0]
        for particle in smoke_particles:
            particle.update()
        
        # Draw
        # Sky gradient
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(SKY_BLUE[0] * (1 - color_ratio) + SKY_DARKER[0] * color_ratio)
            g = int(SKY_BLUE[1] * (1 - color_ratio) + SKY_DARKER[1] * color_ratio)
            b = int(SKY_BLUE[2] * (1 - color_ratio) + SKY_DARKER[2] * color_ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Draw clouds
        for cloud in clouds:
            cloud.draw(screen)
        
        # Draw ground
        pygame.draw.rect(screen, GROUND_GREEN, (0, 460, SCREEN_WIDTH, SCREEN_HEIGHT - 460))
        
        # Draw grass details
        for i in range(0, SCREEN_WIDTH, 20):
            pygame.draw.line(screen, GROUND_DARK, (i, 465), (i + 5, 460), 2)
        
        # Draw trees (background, positioned lower)
        for tree in trees:
            tree.draw(screen)
        
        # Draw railroad tracks
        # Ballast
        pygame.draw.rect(screen, (150, 140, 130), (0, 480, SCREEN_WIDTH, 30))
        
        # Rails
        pygame.draw.rect(screen, RAIL_METAL, (0, 485, SCREEN_WIDTH, 8))
        pygame.draw.rect(screen, RAIL_METAL, (0, 500, SCREEN_WIDTH, 8))
        
        # Rail ties - moving backward (right to left) for forward train motion
        tie_spacing = 30
        for x in range(-tie_spacing, SCREEN_WIDTH + tie_spacing, tie_spacing):
            tie_offset = (wheel_rotation * 10) % tie_spacing
            pygame.draw.rect(screen, RAIL_BROWN, (x + tie_offset, 480, 20, 30))
        
        # Draw train cars
        for car in train_cars:
            car.draw(screen)
        
        # Draw smoke particles
        for particle in smoke_particles:
            particle.draw(screen)
        
        # Draw title
        font_title = pygame.font.Font(None, 48)
        font_subtitle = pygame.font.Font(None, 24)
        
        # Title with shadow
        title_shadow = font_title.render("GIT COMMIT TRAIN", True, (50, 50, 50))
        title_text = font_title.render("GIT COMMIT TRAIN", True, TRAIN_GOLD)
        screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title_text.get_width() // 2 + 3, 23))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 20))
        
        # Subtitle
        subtitle_text = font_subtitle.render(f"Showing {len(commits)} commits", True, (50, 50, 50))
        screen.blit(subtitle_text, (SCREEN_WIDTH // 2 - subtitle_text.get_width() // 2, 70))
        
        # Instructions
        font_instructions = pygame.font.Font(None, 18)
        instructions = "Press ESC to exit | Train moving forward!"
        inst_text = font_instructions.render(instructions, True, (60, 60, 60))
        screen.blit(inst_text, (10, SCREEN_HEIGHT - 25))
        
        # Update display
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()