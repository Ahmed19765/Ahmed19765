#!/usr/bin/env python3
"""
Generate contribution ship GIF with Detailed Debugging Logs
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import math

# ═══════════════════════════════════════════════════════════════
# 🎨 الإعدادات
# ═══════════════════════════════════════════════════════════════

OUTPUT_FILE = "contribution-ship.gif"
SHIP_IMAGE = "ahmed-ehab-ship.png"

IMAGE_WIDTH = 1200
IMAGE_HEIGHT = 400

FRAME_COUNT = 80
FRAME_DURATION = 100
CLOUD_SPEED = 1

SHIP_WIDTH = 1150
SHIP_HEIGHT = 500
SHIP_X_POSITION = None
SHIP_Y_POSITION = 0.001
SHIP_Y_OFFSET = -40

SEA_LEVEL = 0.70
SEA_TRANSPARENCY = 180
SEA_WAVE_AMPLITUDE = 5
SEA_WAVE_FREQUENCY = 0.05

TILE_SIZE = 9.7
TILE_SPACING = 3
GRID_OFFSET_Y = 309
GRID_OFFSET_X = -36.5

SUN_X = 100
SUN_Y = 80
SUN_SIZE = 40

CLOUD_COUNT = 7
CLOUD_MIN_Y = 30
CLOUD_MAX_Y = 200
CLOUD_MIN_SIZE = 40
CLOUD_MAX_SIZE = 90
CLOUD_WHITE = (255, 255, 255, 240)
CLOUD_SHADOW = (200, 210, 225, 200)

TITLE_TEXT = "My GitHub Contributions"
TITLE_Y = 20
TITLE_SIZE = 36

GREEN_LEVELS = [
    (235, 237, 240),
    (198, 228, 139),
    (123, 201, 111),
    (35, 154, 59),
    (19, 108, 50)
]

SEA_COLORS = [
    (20, 70, 130, 180),
    (30, 90, 150, 170),
    (40, 110, 170, 160),
]

# ═══════════════════════════════════════════════════════════════

class Cloud:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = random.randint(CLOUD_MIN_SIZE, CLOUD_MAX_SIZE)
        self.puffs = []
        for _ in range(random.randint(4, 7)):
            offset_x = random.randint(-self.size//2, self.size//2)
            offset_y = random.randint(-self.size//4, self.size//4)
            radius = random.randint(self.size//4, self.size//2)
            self.puffs.append((offset_x, offset_y, radius))
    
    def update(self):
        self.x += self.speed
        if self.x > IMAGE_WIDTH + self.size:
            self.x = -self.size * 2
            self.y = random.randint(CLOUD_MIN_Y, CLOUD_MAX_Y)
            self.size = random.randint(CLOUD_MIN_SIZE, CLOUD_MAX_SIZE)
            self.puffs = []
            for _ in range(random.randint(4, 7)):
                offset_x = random.randint(-self.size//2, self.size//2)
                offset_y = random.randint(-self.size//4, self.size//4)
                radius = random.randint(self.size//4, self.size//2)
                self.puffs.append((offset_x, offset_y, radius))
    
    def draw(self, draw):
        for offset_x, offset_y, radius in self.puffs:
            draw.ellipse(
                [self.x + offset_x - radius + 2, 
                 self.y + offset_y - radius + 5,
                 self.x + offset_x + radius - 2, 
                 self.y + offset_y + radius + 5],
                fill=CLOUD_SHADOW
            )
            draw.ellipse(
                [self.x + offset_x - radius, 
                 self.y + offset_y - radius,
                 self.x + offset_x + radius, 
                 self.y + offset_y + radius],
                fill=CLOUD_WHITE
            )

def create_scattered_clouds():
    clouds = []
    section_width = IMAGE_WIDTH / CLOUD_COUNT
    for i in range(CLOUD_COUNT):
        base_x = section_width * i
        x = base_x + random.uniform(0, section_width * 0.8)
        y = random.randint(CLOUD_MIN_Y, CLOUD_MAX_Y)
        speed = random.uniform(CLOUD_SPEED * 0.4, CLOUD_SPEED * 1.2)
        clouds.append(Cloud(x, y, speed))
    return clouds

def fetch_github_contributions_recent(username, token):
    """جلب مساهمات آخر 365 يوم مع إصلاح استعلام GraphQL"""
    url = 'https://api.github.com/graphql'
    
    to_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    from_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%S')
    
    print(f"🔍 DEBUG: Target Username: '{username}'")
    print(f"🔍 DEBUG: Has Token? -> {bool(token)}")
    if token:
        print(f"🔍 DEBUG: Token Length -> {len(token)} chars")

    # 🔧 تم تصحيح مكان totalContributions ليكون داخل contributionCalendar
    query = """
    query($username: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $username) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
                color
              }
            }
          }
        }
      }
    }
    """
    
    headers = {'User-Agent': 'Python-Script'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    variables = {'username': username, 'from': from_date, 'to': to_date}
    
    try:
        response = requests.post(url, json={'query': query, 'variables': variables}, 
                                headers=headers, timeout=15)
        
        print(f"📡 DEBUG: GitHub API Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"❌ DEBUG API Error Payload: {json.dumps(data['errors'])}")
                return None, 0
            
            user_data = data.get('data', {}).get('user')
            if not user_data:
                print(f"❌ DEBUG: User '{username}' not found or returned null in API response.")
                return None, 0

            calendar = user_data['contributionsCollection']['contributionCalendar']
            total = calendar['totalContributions']
            weeks = calendar['weeks']
            print(f"✅ SUCCESS: Fetched {total} REAL contributions for '{username}'")
            
            grid = []
            for week in weeks:
                for day in week['contributionDays']:
                    count = day['contributionCount']
                    level = 0 if count == 0 else 1 if count <= 3 else 2 if count <= 6 else 3 if count <= 9 else 4
                    grid.append(level)
            
            rows = 7
            cols = len(grid) // rows
            formatted = []
            for row in range(rows):
                row_data = []
                for col in range(cols):
                    idx = col * rows + row
                    if idx < len(grid):
                        row_data.append(grid[idx])
                formatted.append(row_data)
            
            return formatted, total
        else:
            print(f"❌ DEBUG Response Text: {response.text}")
    except Exception as e:
        print(f"❌ DEBUG Exception: {e}")
    
    return None, 0

def generate_random_grid():
    grid = []
    for row in range(7):
        row_data = []
        for col in range(52):
            r = random.random()
            level = 0 if r < 0.35 else 1 if r < 0.60 else 2 if r < 0.80 else 3 if r < 0.93 else 4
            row_data.append(level)
        grid.append(row_data)
    return grid

def draw_sea_layer(draw, frame_num):
    sea_y = int(IMAGE_HEIGHT * SEA_LEVEL)
    for y in range(sea_y, IMAGE_HEIGHT):
        ratio = (y - sea_y) / (IMAGE_HEIGHT - sea_y)
        color_idx = min(int(ratio * len(SEA_COLORS)), len(SEA_COLORS) - 1)
        base_color = SEA_COLORS[color_idx]
        wave_offset = math.sin(y * SEA_WAVE_FREQUENCY + frame_num * 0.1) * SEA_WAVE_AMPLITUDE
        r = base_color[0] + int(wave_offset)
        g = base_color[1] + int(wave_offset * 0.5)
        b = base_color[2] + int(wave_offset * 0.3)
        draw.line([(0, y), (IMAGE_WIDTH, y)], fill=(r, g, b, SEA_TRANSPARENCY))
    
    horizon_y = sea_y + int(math.sin(frame_num * 0.05) * 3)
    draw.line([(0, horizon_y), (IMAGE_WIDTH, horizon_y)], fill=(200, 230, 250, 150), width=2)
    for x in range(0, IMAGE_WIDTH, 20):
        wave_y = horizon_y + int(math.sin(x * 0.05 + frame_num * 0.1) * 4)
        draw.ellipse([x, wave_y-2, x+15, wave_y+2], fill=(255, 255, 255, 100))

def create_frame(draw, ship_img, ship_x, ship_y, clouds, grid, total, frame_num):
    for y in range(IMAGE_HEIGHT):
        ratio = y / IMAGE_HEIGHT
        r = int(30 * (1 - ratio) + 110 * ratio)
        g = int(60 * (1 - ratio) + 180 * ratio)
        b = int(120 * (1 - ratio) + 240 * ratio)
        draw.line([(0, y), (IMAGE_WIDTH, y)], fill=(r, g, b, 255))
    
    draw.ellipse([SUN_X-SUN_SIZE, SUN_Y-SUN_SIZE, SUN_X+SUN_SIZE, SUN_Y+SUN_SIZE], fill=(255, 220, 100, 255))
    draw.ellipse([SUN_X-SUN_SIZE-10, SUN_Y-SUN_SIZE-10, SUN_X+SUN_SIZE+10, SUN_Y+SUN_SIZE+10], outline=(255, 200, 80, 100), width=5)
    
    for cloud in clouds:
        cloud.draw(draw)
        cloud.update()
    
    if ship_img:
        draw._image.paste(ship_img, (ship_x, ship_y), ship_img)
    
    grid_width = len(grid[0]) * (TILE_SIZE + TILE_SPACING)
    grid_height = len(grid) * (TILE_SIZE + TILE_SPACING)
    start_x = (IMAGE_WIDTH - grid_width) // 2 + GRID_OFFSET_X
    start_y = ship_y - grid_height + GRID_OFFSET_Y
    
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            level = grid[row][col]
            color = GREEN_LEVELS[level]
            x = start_x + col * (TILE_SIZE + TILE_SPACING)
            y = start_y + row * (TILE_SIZE + TILE_SPACING)
            draw.rectangle([x, y, x+TILE_SIZE, y+TILE_SIZE], fill=color)
            border_color = (200, 200, 200, 255) if level == 0 else (150, 150, 150, 255)
            draw.rectangle([x, y, x+TILE_SIZE, y+TILE_SIZE], outline=border_color, width=1)
    
    draw_sea_layer(draw, frame_num)
    
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", TITLE_SIZE)
    except:
        font_large = ImageFont.load_default()
    
    title = f"{TITLE_TEXT}: {total}"
    title_bbox = draw.textbbox((0, 0), title, font=font_large)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((IMAGE_WIDTH - title_width) // 2, TITLE_Y), title, 
              fill=(255, 255, 255, 255), font=font_large)

def main():
    print("=" * 60)
    print("🚢 Generating Contribution Ship...")
    print("=" * 60)
    
    username = os.environ.get('GITHUB_USERNAME', 'Ahmed19765')
    token = os.environ.get('GITHUB_TOKEN', None)
    
    grid, total = fetch_github_contributions_recent(username, token)
    
    if grid is None:
        print("⚠️ Failed to fetch real data. Fallback to random data...")
        grid = generate_random_grid()
        total = 0
    
    ship_img = None
    if os.path.exists(SHIP_IMAGE):
        try:
            ship_img = Image.open(SHIP_IMAGE).convert('RGBA')
            ship_height = SHIP_HEIGHT or int(ship_img.height * SHIP_WIDTH / ship_img.width)
            ship_img = ship_img.resize((SHIP_WIDTH, ship_height), Image.Resampling.LANCZOS)
            print(f"✅ Ship: {SHIP_WIDTH}x{ship_height}")
        except Exception as e:
            print(f"❌ {e}")
    
    ship_x = (IMAGE_WIDTH - SHIP_WIDTH) // 2 if SHIP_X_POSITION is None else SHIP_X_POSITION
    ship_y = int(IMAGE_HEIGHT * SHIP_Y_POSITION) + SHIP_Y_OFFSET - 40
    
    clouds = create_scattered_clouds()
    
    print(f"📊 Final Rendered Total: {total}")
    print(f"🎬 Creating {FRAME_COUNT} frames...")
    
    frames = []
    for frame_num in range(FRAME_COUNT):
        img = Image.new('RGBA', (IMAGE_WIDTH, IMAGE_HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        create_frame(draw, ship_img, ship_x, ship_y, clouds, grid, total, frame_num)
        frames.append(img.convert('RGB'))
        if (frame_num + 1) % 20 == 0:
            print(f"   ⏳ {frame_num + 1}/{FRAME_COUNT}")
    
    frames[0].save(OUTPUT_FILE, save_all=True, append_images=frames[1:],
                   duration=FRAME_DURATION, loop=0, optimize=True)
    
    print(f"✅ Saved: {OUTPUT_FILE}")
    print(f"📐 Size: {frames[0].size}")
    print(f"💾 File: {os.path.getsize(OUTPUT_FILE)/1024:.1f} KB")
    print("=" * 60)

if __name__ == "__main__":
    main()
