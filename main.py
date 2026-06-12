import math
import os
import random
import sys
import heapq
from dataclasses import dataclass, field

import pygame

try:
    import nav_mask
    _HAS_NAV_MASK = True
except ImportError:
    _HAS_NAV_MASK = False


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")
SOUND_DIR = os.path.join(BASE_DIR, "Sounds")

SCREEN_W = 1280
SCREEN_H = 760
TOP_H = 46
BOTTOM_H = 32
SIDEBAR_W = 258
VIEW_W = SCREEN_W - SIDEBAR_W
VIEW_H = SCREEN_H - TOP_H - BOTTOM_H

WORLD_W = 1688
WORLD_H = 932
TILE = 20
NAV_TILE = TILE
BUILD_RADIUS = 220
MINIMAP_W = 214
MINIMAP_H = 118

TEAM_RED = "soviet"
TEAM_BLUE = "allied"

DIFFICULTIES = {
    "easy": {
        "label": "Easy",
        "enemy_hp": 0.7,
        "enemy_atk": 0.6,
        "wave_interval": 90,
        "max_wave_count": 12,
        "start_credits": 5000,
        "enemy_count_base": 2,
        "enemy_count_per_wave": 1,
    },
    "medium": {
        "label": "Medium",
        "enemy_hp": 1.0,
        "enemy_atk": 1.0,
        "wave_interval": 60,
        "max_wave_count": 16,
        "start_credits": 2000,
        "enemy_count_base": 3,
        "enemy_count_per_wave": 2,
    },
    "hard": {
        "label": "Hard",
        "enemy_hp": 1.4,
        "enemy_atk": 1.3,
        "wave_interval": 40,
        "max_wave_count": 99,
        "start_credits": 1000,
        "enemy_count_base": 4,
        "enemy_count_per_wave": 3,
    },
}

UNIT_DEFS = {
    "conscript": {
        "name": "Conscript",
        "hp": 80,
        "spd": 60,
        "atk": 15,
        "range": 80,
        "atk_spd": 1.2,
        "sight": 120,
        "size": 10,
        "cost": 100,
        "color": (205, 45, 30),
        "category": "infantry",
    },
    "dog": {
        "name": "War Dog",
        "hp": 60,
        "spd": 100,
        "atk": 25,
        "range": 40,
        "atk_spd": 1.5,
        "sight": 100,
        "size": 8,
        "cost": 200,
        "color": (150, 75, 36),
        "category": "infantry",
    },
    "tesla_trooper": {
        "name": "Tesla Trooper",
        "hp": 100,
        "spd": 55,
        "atk": 45,
        "range": 70,
        "atk_spd": 1.0,
        "sight": 120,
        "size": 10,
        "cost": 500,
        "color": (40, 150, 255),
        "category": "infantry",
    },
    "rhino": {
        "name": "Rhino Tank",
        "hp": 300,
        "spd": 70,
        "atk": 60,
        "range": 120,
        "atk_spd": 1.8,
        "sight": 160,
        "size": 16,
        "cost": 900,
        "color": (140, 70, 36),
        "category": "vehicle",
    },
    "v3": {
        "name": "V3 Rocket",
        "hp": 150,
        "spd": 60,
        "atk": 100,
        "range": 200,
        "atk_spd": 3.0,
        "sight": 180,
        "size": 18,
        "cost": 1200,
        "color": (110, 70, 26),
        "category": "vehicle",
    },
    "apocalypse": {
        "name": "Apocalypse",
        "hp": 600,
        "spd": 45,
        "atk": 120,
        "range": 140,
        "atk_spd": 2.0,
        "sight": 180,
        "size": 20,
        "cost": 2000,
        "color": (105, 28, 20),
        "category": "vehicle",
    },
    "gi": {
        "name": "GI",
        "hp": 70,
        "spd": 55,
        "atk": 12,
        "range": 80,
        "atk_spd": 1.2,
        "sight": 110,
        "size": 10,
        "cost": 0,
        "color": (45, 100, 220),
        "category": "infantry",
    },
    "grizzly": {
        "name": "Grizzly Tank",
        "hp": 250,
        "spd": 75,
        "atk": 50,
        "range": 120,
        "atk_spd": 1.8,
        "sight": 150,
        "size": 15,
        "cost": 0,
        "color": (45, 80, 170),
        "category": "vehicle",
    },
    "prism": {
        "name": "Prism Tank",
        "hp": 180,
        "spd": 65,
        "atk": 80,
        "range": 180,
        "atk_spd": 2.5,
        "sight": 200,
        "size": 14,
        "cost": 0,
        "color": (80, 125, 235),
        "category": "vehicle",
    },
}

STRUCT_DEFS = {
    "conyard": {
        "name": "Construction Yard",
        "hp": 1000,
        "pw": 0,
        "size": 6,
        "cost": 0,
        "color": (174, 65, 40),
    },
    "barracks": {
        "name": "Barracks",
        "hp": 500,
        "pw": -5,
        "size": 4,
        "cost": 300,
        "color": (198, 75, 48),
    },
    "warfactory": {
        "name": "War Factory",
        "hp": 800,
        "pw": -10,
        "size": 6,
        "cost": 2000,
        "color": (184, 80, 48),
    },
    "refinery": {
        "name": "Ore Refinery",
        "hp": 700,
        "pw": -8,
        "size": 4,
        "w_tiles": 6,
        "h_tiles": 4,
        "cost": 2000,
        "color": (198, 132, 58),
    },
    "turret": {
        "name": "Tesla Turret",
        "hp": 400,
        "pw": -5,
        "size": 2,
        "cost": 600,
        "atk": 70,
        "range": 160,
        "atk_spd": 2.0,
        "color": (150, 55, 55),
    },
    "tesla": {
        "name": "Tesla Coil",
        "hp": 500,
        "pw": -15,
        "size": 4,
        "cost": 1500,
        "atk": 120,
        "range": 200,
        "atk_spd": 2.5,
        "color": (95, 65, 175),
    },
    "wall": {
        "name": "Wall",
        "hp": 250,
        "pw": 0,
        "size": 1,
        "cost": 100,
        "color": (92, 86, 76),
    },
    "radar": {
        "name": "Radar Dome",
        "hp": 400,
        "pw": -8,
        "size": 4,
        "cost": 1000,
        "color": (92, 112, 62),
    },
    "powerplant": {
        "name": "Power Plant",
        "hp": 400,
        "pw": 20,
        "size": 4,
        "cost": 500,
        "color": (132, 90, 54),
    },
}

BUILD_KEYS = {
    pygame.K_1: "powerplant",
    pygame.K_KP_1: "powerplant",
    pygame.K_2: "barracks",
    pygame.K_KP_2: "barracks",
    pygame.K_3: "warfactory",
    pygame.K_KP_3: "warfactory",
    pygame.K_4: "refinery",
    pygame.K_KP_4: "refinery",
    pygame.K_5: "turret",
    pygame.K_KP_5: "turret",
    pygame.K_6: "tesla",
    pygame.K_KP_6: "tesla",
    pygame.K_7: "radar",
    pygame.K_KP_7: "radar",
    pygame.K_8: "wall",
    pygame.K_KP_8: "wall",
}

TRAIN_KEYS = {
    pygame.K_q: "conscript",
    pygame.K_w: "dog",
    pygame.K_e: "tesla_trooper",
    pygame.K_a: "rhino",
    pygame.K_s: "v3",
    pygame.K_d: "apocalypse",
}


@dataclass
class Camera:
    x: float = 360
    y: float = 620
    zoom: float = 1.0


@dataclass
class Entity:
    id: int
    kind: str
    type: str
    team: str
    x: float
    y: float
    w: float = 0
    h: float = 0
    hp: float = 1
    max_hp: float = 1
    atk: float = 0
    atk_spd: float = 99
    atk_timer: float = 0
    range: float = 0
    sight: float = 100
    spd: float = 0
    size: float = 10
    color: tuple = (220, 60, 40)
    pw: int = 0
    tx: float = 0
    ty: float = 0
    target_id: int | None = None
    selected: bool = False
    attack_move: bool = False
    state: str = "idle"
    facing: float = 0
    rally_x: float = 0
    rally_y: float = 0
    path: list[tuple[float, float]] = field(default_factory=list)
    path_goal: tuple[float, float] | None = None

    def center(self):
        return self.x + self.w / 2, self.y + self.h / 2

    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), round(self.w), round(self.h))


@dataclass
class Ore:
    x: float
    y: float
    available: bool = True
    respawn: float = 0


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    ttl: float
    color: tuple
    size: float = 3
    text: str | None = None


@dataclass
class Button:
    rect: pygame.Rect
    label: str
    action: str
    kind: str


class NavigationGrid:
    def __init__(self, world_w, world_h, tile_size):
        self.world_w = world_w
        self.world_h = world_h
        self.tile_size = tile_size
        self.cols = math.ceil(world_w / tile_size)
        self.rows = math.ceil(world_h / tile_size)
        self.static_blocked = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.building_occupied = [[False for _ in range(self.cols)] for _ in range(self.rows)]

    def reset_building_occupancy(self):
        self.building_occupied = [[False for _ in range(self.cols)] for _ in range(self.rows)]

    def is_blocked_pixel(self, r, g, b):
        if r > 170 and g > 80 and g < 140 and b < 140 and (r - b) > 70 and (g - b) > 20:
            return True
        if r > 145 and g > 50 and g < 130 and b < 60 and (r - g) > 35:
            return True
        if r < 30 and g < 30 and b < 20:
            return True
        return False

    def generate_from_map(self, map_surface):
        stride = max(1, self.tile_size // 2)
        for gy in range(self.rows):
            for gx in range(self.cols):
                px = gx * self.tile_size
                py = gy * self.tile_size
                blocked_count = 0
                total = 0
                for dy in range(0, self.tile_size, stride):
                    for dx in range(0, self.tile_size, stride):
                        wx = px + dx
                        wy = py + dy
                        if wx >= self.world_w or wy >= self.world_h:
                            continue
                        c = map_surface.get_at((wx, wy))
                        if c.a < 128:
                            continue
                        total += 1
                        if self.is_blocked_pixel(c.r, c.g, c.b):
                            blocked_count += 1
                if total > 0 and blocked_count / total > 0.50:
                    self.static_blocked[gy][gx] = True

    def rebuild_building_occupancy(self, entities):
        self.reset_building_occupancy()
        for entity in entities:
            if entity.kind == "structure" and entity.hp > 0:
                self.occupy_rect(entity.rect().inflate(8, 8))

    def occupy_rect(self, rect):
        start_gx = max(0, rect.left // self.tile_size)
        end_gx = min(self.cols - 1, (rect.right - 1) // self.tile_size)
        start_gy = max(0, rect.top // self.tile_size)
        end_gy = min(self.rows - 1, (rect.bottom - 1) // self.tile_size)
        for gy in range(start_gy, end_gy + 1):
            for gx in range(start_gx, end_gx + 1):
                self.building_occupied[gy][gx] = True

    def cell(self, wx, wy):
        return int(wx // self.tile_size), int(wy // self.tile_size)

    def cell_center(self, gx, gy):
        return (
            gx * self.tile_size + self.tile_size / 2,
            gy * self.tile_size + self.tile_size / 2,
        )

    def in_bounds(self, gx, gy):
        return 0 <= gx < self.cols and 0 <= gy < self.rows

    def is_static_walkable(self, gx, gy):
        return self.in_bounds(gx, gy) and not self.static_blocked[gy][gx]

    def is_walkable_cell(self, gx, gy, ignore_buildings=False):
        if not self.is_static_walkable(gx, gy):
            return False
        return ignore_buildings or not self.building_occupied[gy][gx]

    def is_walkable_world(self, wx, wy, ignore_buildings=False):
        if wx < 0 or wy < 0 or wx >= self.world_w or wy >= self.world_h:
            return False
        return self.is_walkable_cell(*self.cell(wx, wy), ignore_buildings)

    def rect_walkable_for_building(self, rect):
        start_gx = max(0, rect.left // self.tile_size)
        end_gx = min(self.cols - 1, (rect.right - 1) // self.tile_size)
        start_gy = max(0, rect.top // self.tile_size)
        end_gy = min(self.rows - 1, (rect.bottom - 1) // self.tile_size)
        for gy in range(start_gy, end_gy + 1):
            for gx in range(start_gx, end_gx + 1):
                if not self.is_walkable_cell(gx, gy):
                    return False
        return True

    def nearest_walkable_cell(self, gx, gy, max_radius=18):
        if self.is_walkable_cell(gx, gy):
            return gx, gy
        for radius in range(1, max_radius + 1):
            candidates = []
            for x in range(gx - radius, gx + radius + 1):
                candidates.append((x, gy - radius))
                candidates.append((x, gy + radius))
            for y in range(gy - radius + 1, gy + radius):
                candidates.append((gx - radius, y))
                candidates.append((gx + radius, y))
            for cx, cy in candidates:
                if self.is_walkable_cell(cx, cy):
                    return cx, cy
        return None

    def find_path(self, start_world, goal_world):
        start = self.nearest_walkable_cell(*self.cell(*start_world))
        goal = self.nearest_walkable_cell(*self.cell(*goal_world))
        if not start or not goal:
            return []
        if start == goal:
            return [self.cell_center(*goal)]

        open_heap = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        closed = set()

        while open_heap:
            _, current = heapq.heappop(open_heap)
            if current in closed:
                continue
            if current == goal:
                return self.reconstruct_path(came_from, current)
            closed.add(current)
            for neighbor, step_cost in self.neighbors(current):
                if neighbor in closed:
                    continue
                score = g_score[current] + step_cost
                if score < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = score
                    priority = score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_heap, (priority, neighbor))
        return []

    def neighbors(self, cell):
        gx, gy = cell
        for dx, dy, cost in [
            (1, 0, 1),
            (-1, 0, 1),
            (0, 1, 1),
            (0, -1, 1),
            (1, 1, 1.414),
            (1, -1, 1.414),
            (-1, 1, 1.414),
            (-1, -1, 1.414),
        ]:
            nx, ny = gx + dx, gy + dy
            if not self.is_walkable_cell(nx, ny):
                continue
            if dx and dy:
                if not self.is_walkable_cell(gx + dx, gy) or not self.is_walkable_cell(gx, gy + dy):
                    continue
            yield (nx, ny), cost

    def reconstruct_path(self, came_from, current):
        cells = [current]
        while current in came_from:
            current = came_from[current]
            cells.append(current)
        cells.reverse()
        return [self.cell_center(gx, gy) for gx, gy in cells[1:]]

    def heuristic(self, a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])


@dataclass
class Game:
    screen: pygame.Surface
    clock: pygame.time.Clock
    font: pygame.font.Font
    small: pygame.font.Font
    big: pygame.font.Font
    assets: dict = field(default_factory=dict)
    sounds: dict = field(default_factory=dict)
    entities: list[Entity] = field(default_factory=list)
    ore: list[Ore] = field(default_factory=list)
    particles: list[Particle] = field(default_factory=list)
    buttons: list[Button] = field(default_factory=list)
    selected_ids: list[int] = field(default_factory=list)
    training_queue: list[str] = field(default_factory=list)
    camera: Camera = field(default_factory=Camera)
    next_id: int = 1
    credits: int = 2000
    power: int = 10
    wave: int = 1
    wave_timer: float = 0
    refinery_timer: float = 0
    training_timer: float = 0
    radar_timer: float = 0
    difficulty: str | None = None
    paused: bool = False
    game_over: bool = False
    winner: str | None = None
    placing: str | None = None
    message: str = "Select a difficulty."
    message_timer: float = 0
    drag_start: tuple | None = None
    drag_pos: tuple | None = None
    panning: bool = False
    pan_start: tuple = (0, 0)
    pan_cam: tuple = (0, 0)
    map_surface: pygame.Surface | None = None
    nav_grid: NavigationGrid = field(default_factory=lambda: NavigationGrid(WORLD_W, WORLD_H, NAV_TILE))
    debug_nav: bool = False
    music_mode: str | None = None
    music_channel: pygame.mixer.Channel | None = None
    command_voice_timer: float = 0
    base_warning_timer: float = 0
    active_tab: str = "bldg"
    paused_buttons: list[Button] = field(default_factory=list)
    muted: bool = False
    sfx_volume: float = 1.0
    cheat_buffer: str = ""
    menu_hover_key: str | None = None
    nav_vis_surface: pygame.Surface | None = None
    show_nav_vis: bool = False
    _menu_was_pressed: bool = False

    def uid(self):
        value = self.next_id
        self.next_id += 1
        return value

    def load_assets(self):
        names = {
            "map": "Map.png",
            "red_conyard": "Red_Motherhall.png",
            "blue_conyard": "Blue_Motherhall.png",
            "red_powerplant": "Red_Power_Plant.png",
            "blue_powerplant": "Blue_Power_Plant.png",
            "red_refinery": "Red_Refinery.png",
            "blue_refinery": "Blue_Refinery.png",
            "red_barracks": "Red_Infantry.png",
            "blue_barracks": "Blue_Infantry.png",
            "red_warfactory": "Red_Barrack.png",
            "blue_warfactory": "Blue_Barrack.png",
            "red_radar": "Red_Radar.png",
            "blue_radar": "Blue_Radar.png",
            "red_tesla": "Red_Tesla_Coil.png",
            "blue_tesla": "Blue_Tesla_Coil.png",
            "red_turret": "Red_Turret.png",
            "blue_turret": "Blue_Turret.png",
            "red_apocalypse": "Red_Apocalypse.png",
            "red_v3": "Red_V3.png",
            "red_dog": "Red_War_Dog.png",
            "red_tesla_trooper": "Red_Tesla_Trooper.png",
            "red_troop": "red_troop_logo.png",
            "blue_troop": "blue_troop_logo.png",
            "red_rhino": "Red_Rhino.png",
            "blue_apocalypse": "Blue_Apocalypse.png",
        }
        for i in range(8):
            names[f"red_rhino_{i}"] = f"Rhino_Red_{i}.png"
            names[f"blue_rhino_{i}"] = f"Rhino_Blue_{i}.png"
        for key, filename in names.items():
            path = os.path.join(ASSET_DIR, filename)
            if os.path.exists(path):
                try:
                    self.assets[key] = pygame.image.load(path).convert_alpha()
                except pygame.error:
                    pass
        if "map" in self.assets:
            self.map_surface = pygame.transform.smoothscale(
                self.assets["map"], (WORLD_W, WORLD_H)
            )
        else:
            self.map_surface = self.create_fallback_map()

    def load_sounds(self):
        if not pygame.mixer.get_init():
            return
        pygame.mixer.set_reserved(1)
        self.music_channel = pygame.mixer.Channel(0)
        names = {
            "click": "Clicking_Sound.mp3",
            "menu_music": "Landing_Page_Song.mp3",
            "theme": "Theme_Song.mp3",
            "build_start": "building.mp3",
            "construction_done": "construction-completed.mp3",
            "new_options": "new-construction-options.mp3",
            "insufficient": "insufficient-balance.mp3",
            "unit_ready": "unit-ready.mp3",
            "move": "moving-out.mp3",
            "affirmative": "affirmative.mp3",
            "yes_commander": "yes-commander.mp3",
            "yes_sir": "yes-sir.mp3",
            "absolutely": "absolutely.mp3",
            "cancel": "cancel.mp3",
            "hold": "on-hold.mp3",
            "base_danger": "our-base-is-in-danger.mp3",
            "dog": "dog_sound.mp3",
            "victory": "congratulations.mp3",
            "defeat": "Loosing_Sound.mp3",
        }
        for key, filename in names.items():
            path = os.path.join(SOUND_DIR, filename)
            if os.path.exists(path):
                try:
                    self.sounds[key] = pygame.mixer.Sound(path)
                except pygame.error:
                    pass
        for key, sound in self.sounds.items():
            sound.set_volume(0.28 if key in ("menu_music", "theme") else 0.45)

    def play(self, key):
        if self.muted or not pygame.mixer.get_init():
            return
        sound = self.sounds.get(key)
        if sound:
            try:
                vol = 0.28 if key in ("menu_music", "theme") else 0.45
                sound.set_volume(vol * self.sfx_volume)
                sound.play()
            except Exception:
                pass

    def music(self, key):
        try:
            if self.music_mode == key or key not in self.sounds:
                return
            if not pygame.mixer.get_init():
                return
            if not self.music_channel:
                self.music_channel = pygame.mixer.Channel(0)
            self.music_channel.stop()
            
            # Set music channel volume
            vol = 0.28 if key in ("menu_music", "theme") else 0.45
            if self.muted:
                self.music_channel.set_volume(0)
            else:
                self.music_channel.set_volume(vol * self.sfx_volume)
                
            self.music_channel.play(self.sounds[key], loops=-1)
            self.music_mode = key
        except Exception:
            pass

    def update_music_volume(self):
        if not pygame.mixer.get_init() or not self.music_channel:
            return
        if self.muted:
            self.music_channel.set_volume(0)
        else:
            vol = 0.28 if self.music_mode in ("menu_music", "theme") else 0.45
            self.music_channel.set_volume(vol * self.sfx_volume)

    def update_volumes(self):
        # Update sound volumes
        for key, sound in self.sounds.items():
            if self.muted:
                sound.set_volume(0)
            else:
                vol = 0.28 if key in ("menu_music", "theme") else 0.45
                sound.set_volume(vol * self.sfx_volume)
        # Update active music channel
        self.update_music_volume()

    def create_fallback_map(self):
        """Generate a clean, minimal background map"""
        surface = pygame.Surface((WORLD_W, WORLD_H))
        
        # Simple solid background
        surface.fill((35, 45, 32))
        
        # Optional: Add very subtle grid for tactical feel (remove if you want it completely blank)
        grid_color = (28, 36, 25)
        for x in range(0, WORLD_W, TILE * 8):
            pygame.draw.line(surface, grid_color, (x, 0), (x, WORLD_H), 1)
        for y in range(0, WORLD_H, TILE * 8):
            pygame.draw.line(surface, grid_color, (0, y), (WORLD_W, y), 1)
        
        return surface

    def start(self, difficulty):
        self.difficulty = difficulty
        self.entities.clear()
        self.ore.clear()
        self.particles.clear()
        self.selected_ids.clear()
        self.training_queue.clear()
        self.next_id = 1
        self.credits = DIFFICULTIES[difficulty]["start_credits"]
        self.wave = 1
        self.wave_timer = 0
        self.refinery_timer = 0
        self.training_timer = 0
        self.radar_timer = 0
        self.paused = False
        self.game_over = False
        self.winner = None
        self.placing = None
        self.camera = Camera(360, 620, 1.0)
        self.message = "Awaiting orders, Commander."
        self.message_timer = 4
        self.command_voice_timer = 0
        self.base_warning_timer = 0
        self.active_tab = "bldg"
        try:
            self.music("theme")
            self.play("yes_commander")
        except Exception:
            pass

        nav_mask_path = os.path.join(BASE_DIR, "nav_mask.pkl")
        if _HAS_NAV_MASK and os.path.exists(nav_mask_path):
            try:
                loaded = nav_mask.load_nav_mask(nav_mask_path)
                for gy in range(min(loaded.shape[0], self.nav_grid.rows)):
                    for gx in range(min(loaded.shape[1], self.nav_grid.cols)):
                        self.nav_grid.static_blocked[gy][gx] = bool(loaded[gy, gx])
            except Exception:
                self.nav_grid.generate_from_map(self.map_surface)
        else:
            self.nav_grid.generate_from_map(self.map_surface)
        for data in [
            ("conyard", 6, 34, TEAM_RED),
            ("barracks", 14, 34, TEAM_RED),
            ("refinery", 6, 40, TEAM_RED),
            ("turret", 22, 34, TEAM_RED),
            ("turret", 22, 40, TEAM_RED),
            ("conyard", 66, 4, TEAM_BLUE),
            ("barracks", 74, 4, TEAM_BLUE),
            ("refinery", 66, 10, TEAM_BLUE),
            ("turret", 58, 4, TEAM_BLUE),
            ("turret", 58, 10, TEAM_BLUE),
        ]:
            self.entities.append(self.spawn_structure(*data))
        self.refresh_navigation()

        for i in range(5):
            self.entities.append(self.spawn_unit("conscript", 200 + i * 25, 600 + (i % 2) * 30, TEAM_RED))
            self.entities.append(self.spawn_unit("gi", 1300 - i * 25, 120 + (i % 2) * 30, TEAM_BLUE))
        self.entities.append(self.spawn_unit("rhino", 300, 650, TEAM_RED))
        self.entities.append(self.spawn_unit("grizzly", 1400, 250, TEAM_BLUE))
        self.create_ore(7)
        self.recalc_power()

    def refresh_navigation(self):
        self.nav_grid.rebuild_building_occupancy(self.entities)

    def set_unit_destination(self, unit, wx, wy):
        unit.tx = clamp(wx, 0, WORLD_W - 1)
        unit.ty = clamp(wy, 0, WORLD_H - 1)
        unit.path_goal = (unit.tx, unit.ty)
        unit.path = self.nav_grid.find_path((unit.x, unit.y), unit.path_goal)
        if unit.path:
            unit.tx, unit.ty = unit.path[-1]
            unit.path_goal = (unit.tx, unit.ty)
        if not unit.path and self.nav_grid.is_walkable_world(unit.tx, unit.ty):
            unit.path = [(unit.tx, unit.ty)]

    def spawn_unit(self, unit_type, x, y, team):
        data = UNIT_DEFS[unit_type]
        hp_mult = DIFFICULTIES[self.difficulty]["enemy_hp"] if team == TEAM_BLUE and self.difficulty else 1
        atk_mult = DIFFICULTIES[self.difficulty]["enemy_atk"] if team == TEAM_BLUE and self.difficulty else 1
        hp = data["hp"] * hp_mult
        return Entity(
            id=self.uid(),
            kind="unit",
            type=unit_type,
            team=team,
            x=x,
            y=y,
            hp=hp,
            max_hp=hp,
            atk=data["atk"] * atk_mult,
            atk_spd=data["atk_spd"],
            range=data["range"],
            sight=data["sight"],
            spd=data["spd"],
            size=data["size"],
            color=data["color"],
            tx=x,
            ty=y,
            w=data["size"] * 2,
            h=data["size"] * 2,
        )

    def spawn_structure(self, struct_type, gx, gy, team):
        data = STRUCT_DEFS[struct_type]
        wt = data.get("w_tiles", data["size"])
        ht = data.get("h_tiles", data["size"])
        w = wt * TILE
        h = ht * TILE
        x = gx * TILE
        y = gy * TILE
        return Entity(
            id=self.uid(),
            kind="structure",
            type=struct_type,
            team=team,
            x=x,
            y=y,
            w=w,
            h=h,
            hp=data["hp"],
            max_hp=data["hp"],
            atk=data.get("atk", 0),
            atk_spd=data.get("atk_spd", 99),
            range=data.get("range", 0),
            sight=max(160, data.get("range", 0) * 1.5),
            color=data["color"] if team == TEAM_RED else (55, 90, 185),
            pw=data["pw"],
            rally_x=x + w / 2 + 40,
            rally_y=y + h + 20,
        )

    def create_ore(self, count):
        for _ in range(count):
            self.ore.append(self.random_ore())

    def random_ore(self):
        for _ in range(200):
            x = random.randint(80, WORLD_W - 80)
            y = random.randint(80, WORLD_H - 80)
            if all(distance_xy(x, y, *e.center()) > 120 for e in self.entities):
                if all(distance_xy(x, y, o.x, o.y) > 120 for o in self.ore):
                    return Ore(x, y)
        return Ore(random.randint(80, WORLD_W - 80), random.randint(80, WORLD_H - 80))

    def entity_by_id(self, entity_id):
        for entity in self.entities:
            if entity.id == entity_id:
                return entity
        return None

    def selected(self):
        return [e for e in self.entities if e.id in self.selected_ids]

    def alert(self, message, seconds=3):
        self.message = message
        self.message_timer = seconds

    def update(self, dt):
        if not self.difficulty or self.paused or self.game_over:
            if not self.difficulty:
                self.music("menu_music")
                pressed = pygame.mouse.get_pressed()
                any_down = pressed[0] or pressed[1] or pressed[2]
                if any_down and not self._menu_was_pressed:
                    mx, my = pygame.mouse.get_pos()
                    for key, rect in self.menu_cards():
                        if rect.collidepoint(mx, my):
                            self.start(key)
                            break
                self._menu_was_pressed = any_down
            self.update_particles(dt)
            return

        self.handle_camera_keys(dt)
        self.command_voice_timer = max(0, self.command_voice_timer - dt)
        self.base_warning_timer = max(0, self.base_warning_timer - dt)
        self.refinery_timer += dt
        if self.refinery_timer >= 5:
            self.refinery_timer = 0
            refineries = [e for e in self.entities if e.kind == "structure" and e.team == TEAM_RED and e.type == "refinery"]
            if refineries:
                self.credits = min(99999, self.credits + 200 * len(refineries))
                self.alert(f"+${200 * len(refineries)} credits")

        self.wave_timer += dt
        interval = DIFFICULTIES[self.difficulty]["wave_interval"]
        if self.wave_timer >= interval:
            self.wave_timer = 0
            self.spawn_wave()
            self.wave += 1

        self.update_training(dt)
        self.update_ore(dt)
        self.update_radar_heal(dt)
        for entity in list(self.entities):
            self.update_combat(entity, dt)
            if entity.kind == "unit":
                self.update_movement(entity, dt)
        self.remove_dead()
        self.recalc_power()
        self.update_particles(dt)
        if self.message_timer > 0:
            self.message_timer -= dt

    def handle_camera_keys(self, dt):
        keys = pygame.key.get_pressed()
        speed = 520 / self.camera.zoom
        
        # Keyboard panning (Arrow keys or IJKL keys)
        if keys[pygame.K_LEFT] or keys[pygame.K_j]:
            self.camera.x -= speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_l]:
            self.camera.x += speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_i]:
            self.camera.y -= speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_k]:
            self.camera.y += speed * dt
            
        # Mouse edge scrolling
        if pygame.mouse.get_focused():
            mx, my = pygame.mouse.get_pos()
            margin = 20
            if mx < margin:
                self.camera.x -= speed * dt
            elif mx > SCREEN_W - margin:
                self.camera.x += speed * dt
            if my < margin:
                self.camera.y -= speed * dt
            elif my > SCREEN_H - margin:
                self.camera.y += speed * dt
                
        self.clamp_camera()

    def update_training(self, dt):
        if not self.training_queue:
            return
        unit_type = self.training_queue[0]
        train_time = max(3, UNIT_DEFS[unit_type]["cost"] / 200)
        self.training_timer += dt
        if self.training_timer >= train_time:
            self.training_timer = 0
            self.training_queue.pop(0)
            producer = "warfactory" if unit_type in ("rhino", "v3", "apocalypse") else "barracks"
            src = next((e for e in self.entities if e.team == TEAM_RED and e.type == producer), None)
            if not src:
                src = next((e for e in self.entities if e.team == TEAM_RED and e.type in ("barracks", "warfactory")), None)
            sx, sy = (300, 650) if not src else (src.x + src.w / 2, src.y + src.h + 20)
            unit = self.spawn_unit(unit_type, sx + random.uniform(-24, 24), sy + random.uniform(0, 30), TEAM_RED)
            self.entities.append(unit)
            self.alert(f"{UNIT_DEFS[unit_type]['name']} ready")
            self.play("unit_ready")

    def update_ore(self, dt):
        for ore in self.ore:
            if not ore.available:
                ore.respawn -= dt
                if ore.respawn <= 0:
                    new_ore = self.random_ore()
                    ore.x = new_ore.x
                    ore.y = new_ore.y
                    ore.available = True
                continue
            for entity in self.entities:
                if entity.kind == "unit" and distance_xy(entity.x, entity.y, ore.x, ore.y) < 26:
                    if entity.team == TEAM_RED:
                        self.credits = min(99999, self.credits + 200)
                        self.alert("+$200 ore collected")
                    ore.available = False
                    ore.respawn = 40
                    break

    def update_radar_heal(self, dt):
        self.radar_timer += dt
        if self.radar_timer < 0.5:
            return
        self.radar_timer = 0
        radars = [e for e in self.entities if e.kind == "structure" and e.team == TEAM_RED and e.type == "radar"]
        if not radars:
            return
        for entity in self.entities:
            if entity.team == TEAM_RED and entity.hp < entity.max_hp:
                if any(entity_distance(entity, radar) < 300 for radar in radars):
                    entity.hp = min(entity.max_hp, entity.hp + 3)

    def update_combat(self, entity, dt):
        if entity.atk <= 0:
            return
        entity.atk_timer = max(0, entity.atk_timer - dt)
        target = self.entity_by_id(entity.target_id) if entity.target_id else None
        if entity.kind == "unit" and entity.state == "move" and not entity.attack_move and not target:
            return
        if not target or target.hp <= 0:
            target = self.find_target(entity)
            entity.target_id = target.id if target else None
        if not target:
            return
        d = entity_distance(entity, target)
        if d <= entity.range:
            if entity.kind == "unit":
                entity.tx = entity.x
                entity.ty = entity.y
                entity.path.clear()
                entity.path_goal = None
            if entity.atk_timer <= 0:
                dmg = entity.atk * (1.3 if self.has_radar_buff(entity) else 1)
                target.hp -= dmg
                if target.team == TEAM_RED and target.kind == "structure" and self.base_warning_timer <= 0:
                    self.play("base_danger")
                    self.base_warning_timer = 12
                entity.atk_timer = entity.atk_spd
                tx, ty = target.center()
                self.add_burst(tx, ty, (255, 190, 80), 5)
                self.particles.append(Particle(tx, ty - 12, 0, -20, 0.7, (255, 230, 150), 1, str(round(dmg))))
                if target.kind == "unit" and target.team == TEAM_RED and not target.target_id:
                    target.target_id = entity.id
                    target.state = "attack"
        elif entity.kind == "unit" and (entity.attack_move or entity.state == "attack"):
            goal = target.center()
            if not entity.path_goal or distance_xy(entity.path_goal[0], entity.path_goal[1], *goal) > NAV_TILE * 2:
                self.set_unit_destination(entity, *goal)

    def find_target(self, entity):
        enemies = [e for e in self.entities if e.team != entity.team and e.hp > 0]
        if entity.team == TEAM_BLUE and entity.state == "attack":
            return min(enemies, key=lambda e: entity_distance(entity, e) * (0.85 if e.kind == "structure" else 1), default=None)
        sight = entity.sight * (1.5 if self.has_radar_buff(entity) else 1)
        nearby = [e for e in enemies if entity_distance(entity, e) <= sight]
        return min(nearby, key=lambda e: entity_distance(entity, e), default=None)

    def has_radar_buff(self, entity):
        if entity.team != TEAM_RED:
            return False
        return any(e.team == TEAM_RED and e.type == "radar" and entity_distance(entity, e) < 300 for e in self.entities)

    def update_movement(self, unit, dt):
        if not unit.path and unit.path_goal and distance_xy(unit.x, unit.y, *unit.path_goal) > NAV_TILE:
            unit.path = self.nav_grid.find_path((unit.x, unit.y), unit.path_goal)
        wx, wy = unit.path[0] if unit.path else (unit.tx, unit.ty)
        dx = wx - unit.x
        dy = wy - unit.y
        d = math.hypot(dx, dy)
        if d < 2:
            unit.x = wx
            unit.y = wy
            if unit.path:
                unit.path.pop(0)
            if not unit.path and distance_xy(unit.x, unit.y, unit.tx, unit.ty) <= NAV_TILE:
                unit.path_goal = None
                unit.state = "idle"
            return
        unit.facing = math.atan2(dy, dx)
        step = min(d, unit.spd * dt)
        nx = unit.x + dx / d * step
        ny = unit.y + dy / d * step
        if self.walkable(nx, ny, unit):
            unit.x = nx
            unit.y = ny
        else:
            unit.path = self.nav_grid.find_path((unit.x, unit.y), (unit.tx, unit.ty))
            if not unit.path:
                unit.tx = unit.x
                unit.ty = unit.y
                unit.path_goal = None
                unit.state = "idle"
        unit.x = clamp(unit.x, 0, WORLD_W)
        unit.y = clamp(unit.y, 0, WORLD_H)

    def walkable(self, x, y, unit=None):
        return self.nav_grid.is_walkable_world(x, y)

    def remove_dead(self):
        dead = [e for e in self.entities if e.hp <= 0]
        for entity in dead:
            x, y = entity.center()
            self.add_burst(x, y, (255, 75, 30), 18)
            if entity.team == TEAM_BLUE and entity.kind == "unit":
                self.credits = min(99999, self.credits + 50)
        self.entities = [e for e in self.entities if e.hp > 0]
        if any(e.kind == "structure" for e in dead):
            self.refresh_navigation()
        live_ids = {e.id for e in self.entities}
        self.selected_ids = [entity_id for entity_id in self.selected_ids if entity_id in live_ids]
        soviet_cy = any(e.team == TEAM_RED and e.type == "conyard" for e in self.entities)
        allied_cy = any(e.team == TEAM_BLUE and e.type == "conyard" for e in self.entities)
        if not soviet_cy:
            self.end_game(TEAM_BLUE)
        elif not allied_cy:
            self.end_game(TEAM_RED)

    def end_game(self, winner):
        if self.game_over:
            return
        self.winner = winner
        self.game_over = True
        if self.music_channel:
            self.music_channel.stop()
        self.music_mode = None
        for sound in self.sounds.values():
            try:
                sound.stop()
            except Exception:
                pass
        self.play("victory" if winner == TEAM_RED else "defeat")
        self.alert("Victory! The Allied base has fallen." if winner == TEAM_RED else "Defeat! Construction Yard destroyed.", 99)

    def spawn_wave(self):
        diff = DIFFICULTIES[self.difficulty]
        count = min(diff["enemy_count_base"] + self.wave * diff["enemy_count_per_wave"], diff["max_wave_count"])
        types = self.wave_types()
        for _ in range(count):
            unit_type = random.choice(types)
            unit = self.spawn_unit(unit_type, WORLD_W - 210 + random.uniform(-100, 100), 120 + random.uniform(-50, 180), TEAM_BLUE)
            unit.state = "attack"
            unit.attack_move = True
            self.set_unit_destination(unit, 150 + random.uniform(-40, 360), 690 + random.uniform(-40, 140))
            self.entities.append(unit)
        self.alert(f"Enemy attack! Wave {self.wave}", 4)
        self.play("base_danger")

    def wave_types(self):
        if self.wave <= 2:
            return ["gi"]
        if self.wave <= 4:
            return ["gi", "gi", "grizzly"]
        if self.wave <= 6:
            return ["gi", "grizzly", "grizzly"]
        if self.wave <= 8:
            return ["grizzly", "prism", "gi"]
        return ["grizzly", "prism", "apocalypse", "v3"]

    def recalc_power(self):
        self.power = 10 + sum(e.pw for e in self.entities if e.kind == "structure" and e.team == TEAM_RED)

    def add_burst(self, x, y, color, count):
        for _ in range(count):
            angle = random.random() * math.tau
            speed = random.uniform(20, 90)
            self.particles.append(Particle(x, y, math.cos(angle) * speed, math.sin(angle) * speed, random.uniform(0.25, 0.75), color, random.uniform(2, 5)))

    def update_particles(self, dt):
        for particle in self.particles:
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            particle.ttl -= dt
        self.particles = [p for p in self.particles if p.ttl > 0]

    def try_build(self, struct_type):
        if not self.difficulty or self.game_over:
            return
        data = STRUCT_DEFS[struct_type]
        if self.credits < data["cost"]:
            self.alert("Insufficient credits")
            self.play("insufficient")
            return
        self.placing = struct_type
        self.alert(f"Place {data['name']} with left click")
        self.play("new_options")

    def place_structure(self, wx, wy):
        if not self.placing:
            return
        data = STRUCT_DEFS[self.placing]
        gx = int(wx // TILE)
        gy = int(wy // TILE)
        wt = data.get("w_tiles", data["size"])
        ht = data.get("h_tiles", data["size"])
        rect = pygame.Rect(gx * TILE, gy * TILE, wt * TILE, ht * TILE)
        if rect.left < 0 or rect.top < 0 or rect.right > WORLD_W or rect.bottom > WORLD_H:
            self.alert("Cannot build here")
            self.play("cancel")
            return
        if not self.nav_grid.rect_walkable_for_building(rect):
            self.alert("Terrain blocked")
            self.play("cancel")
            return
        for entity in self.entities:
            if entity.kind == "structure" and rect.colliderect(entity.rect()):
                self.alert("Space occupied")
                self.play("cancel")
                return
        cx, cy = rect.center
        if not any(e.kind == "structure" and e.team == TEAM_RED and distance_xy(cx, cy, *e.center()) < BUILD_RADIUS for e in self.entities):
            self.alert("Build near your base")
            self.play("cancel")
            return
        self.credits -= data["cost"]
        self.entities.append(self.spawn_structure(self.placing, gx, gy, TEAM_RED))
        self.refresh_navigation()
        self.alert(f"{data['name']} constructed")
        self.play("construction_done")
        self.placing = None

    def train_unit(self, unit_type):
        if not self.difficulty or self.game_over:
            return
        data = UNIT_DEFS[unit_type]
        if unit_type in ("conscript", "dog", "tesla_trooper"):
            if not any(e.team == TEAM_RED and e.type == "barracks" for e in self.entities):
                self.alert("Need Barracks")
                self.play("cancel")
                return
        if unit_type in ("rhino", "v3", "apocalypse"):
            if not any(e.team == TEAM_RED and e.type == "warfactory" for e in self.entities):
                self.alert("Need War Factory")
                self.play("cancel")
                return
        if self.credits < data["cost"]:
            self.alert("Insufficient credits")
            self.play("insufficient")
            return
        self.credits -= data["cost"]
        self.training_queue.append(unit_type)
        self.alert(f"Training {data['name']}")
        self.play("build_start")

    def screen_to_world(self, sx, sy):
        vx = sx
        vy = sy - TOP_H
        wx = (vx - VIEW_W / 2) / self.camera.zoom + self.camera.x
        wy = (vy - VIEW_H / 2) / self.camera.zoom + self.camera.y
        return wx, wy

    def world_to_screen(self, wx, wy):
        sx = (wx - self.camera.x) * self.camera.zoom + VIEW_W / 2
        sy = (wy - self.camera.y) * self.camera.zoom + VIEW_H / 2 + TOP_H
        return sx, sy

    def clamp_camera(self):
        half_w = VIEW_W / 2 / self.camera.zoom
        half_h = VIEW_H / 2 / self.camera.zoom
        min_x, max_x = half_w, WORLD_W - half_w
        min_y, max_y = half_h, WORLD_H - half_h
        if min_x < max_x:
            self.camera.x = clamp(self.camera.x, min_x, max_x)
        if min_y < max_y:
            self.camera.y = clamp(self.camera.y, min_y, max_y)

    def event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            self.keydown(event.key)

        # 1. Handle clicks when game is paused (left-click only — block everything else)
        if self.paused and self.difficulty:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Top-bar pause button toggles resume
                pause_rect = pygame.Rect(SCREEN_W - 38, 10, 26, 26)
                if pause_rect.collidepoint(event.pos):
                    self.play("click")
                    self.paused = False
                    self.play("affirmative")
                    return
                self.paused_click(event.pos)
            # Swallow all other mouse events (right/middle/wheel/motion) so the
            # world underneath the overlay cannot receive them.
            return

        if not self.difficulty:
            if event.type in (pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
                print(f"[MENU] Button {event.button} {event.type} at {event.pos}", file=sys.stderr)
                if event.button in (1, 2, 3):
                    mx, my = event.pos
                    for key, rect in self.menu_cards():
                        if rect.collidepoint(mx, my):
                            self.start(key)
                            try:
                                self.play("click")
                            except Exception:
                                pass
                            break
                return
            self.menu_event(event)
            return

        # 2. Check if top-bar pause button is clicked
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pause_rect = pygame.Rect(SCREEN_W - 38, 10, 26, 26)
            if pause_rect.collidepoint(event.pos):
                self.play("click")
                self.paused = True
                self.play("hold")
                return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_down(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_up(event)
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_motion(event)

    def paused_click(self, pos):
        for btn in self.paused_buttons:
            if btn.rect.collidepoint(pos):
                self.play("click")
                if btn.action == "resume":
                    self.paused = False
                    self.play("affirmative")
                elif btn.action == "mute":
                    self.muted = not self.muted
                    self.update_volumes()
                elif btn.action == "vol_down":
                    self.sfx_volume = clamp(self.sfx_volume - 0.1, 0.0, 1.0)
                    self.muted = False  # changing volume implies the user wants sound
                    self.update_volumes()
                elif btn.action == "vol_up":
                    self.sfx_volume = clamp(self.sfx_volume + 0.1, 0.0, 1.0)
                    self.muted = False
                    self.update_volumes()
                elif btn.action == "quit":
                    self.paused = False
                    self.difficulty = None
                    self.music("menu_music")
                return

    def keydown(self, key):
        if not self.difficulty:
            if key == pygame.K_1:
                self.start("easy")
            elif key == pygame.K_2:
                self.start("medium")
            elif key == pygame.K_3:
                self.start("hard")
            return
        if key == pygame.K_ESCAPE:
            self.placing = None
            self.paused = False
            self.play("cancel")
            return
        elif key == pygame.K_p:
            self.paused = not self.paused
            self.play("hold" if self.paused else "affirmative")
            return
        elif key == pygame.K_g:
            self.debug_nav = not self.debug_nav
            self.alert("Navigation grid shown" if self.debug_nav else "Navigation grid hidden")
            return
        elif key == pygame.K_v:
            self.show_nav_vis = not self.show_nav_vis
            if self.show_nav_vis and self.nav_vis_surface is None and _HAS_NAV_MASK:
                vis_path = os.path.join(BASE_DIR, "nav_mask_vis.png")
                if os.path.exists(vis_path):
                    try:
                        self.nav_vis_surface = pygame.image.load(vis_path).convert()
                    except pygame.error:
                        pass
            self.alert("Nav mask vis shown" if self.show_nav_vis else "Nav mask vis hidden")
            return
        elif key == pygame.K_r and self.game_over:
            self.difficulty = None
            self.game_over = False
            self.music("menu_music")
            return
        elif key == pygame.K_DELETE:
            self.sell_selected()
            return
        elif key == pygame.K_EQUALS or key == pygame.K_PLUS:
            self.camera.zoom = min(1.8, self.camera.zoom + 0.1)
            self.clamp_camera()
            return
        elif key == pygame.K_MINUS:
            self.camera.zoom = max(0.55, self.camera.zoom - 0.1)
            self.clamp_camera()
            return

        if pygame.K_a <= key <= pygame.K_z:
            self.cheat_buffer += pygame.key.name(key)
            if len(self.cheat_buffer) > 20:
                self.cheat_buffer = self.cheat_buffer[-20:]
            if self.cheat_buffer.endswith("win"):
                self.cheat_buffer = ""
                for e in list(self.entities):
                    if e.team == TEAM_BLUE and e.kind == "structure":
                        e.hp = 0
                self.alert("Cheat activated: Victory")
                return
            elif self.cheat_buffer.endswith("los"):
                self.cheat_buffer = ""
                for e in list(self.entities):
                    if e.team == TEAM_RED and e.kind == "structure":
                        e.hp = 0
                self.alert("Cheat activated: Defeat")
                return
            elif self.cheat_buffer.endswith("money"):
                self.cheat_buffer = ""
                self.credits += 100000
                self.alert("Cheat activated: +100000 credits")
                return
        else:
            self.cheat_buffer = ""

        if key in BUILD_KEYS:
            self.try_build(BUILD_KEYS[key])
        elif key in TRAIN_KEYS:
            self.train_unit(TRAIN_KEYS[key])

    def sell_selected(self):
        selected = self.selected()
        if not selected:
            return
        refund = 0
        for entity in selected:
            if entity.team == TEAM_RED:
                if entity.kind == "structure":
                    refund += int(STRUCT_DEFS[entity.type]["cost"] * 0.5)
                entity.hp = 0
        self.credits = min(99999, self.credits + refund)
        self.alert(f"Sold for ${refund}")
        self.play("construction_done" if refund else "cancel")

    def menu_event(self, event):
        try:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.start("easy")
                elif event.key in (pygame.K_1, pygame.K_KP_1):
                    self.start("easy")
                elif event.key in (pygame.K_2, pygame.K_KP_2):
                    self.start("medium")
                elif event.key in (pygame.K_3, pygame.K_KP_3):
                    self.start("hard")
                return
            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                self.menu_hover_key = None
                for key, rect in self.menu_cards():
                    if rect.collidepoint(mx, my):
                        self.menu_hover_key = key
                        break
                return
            if event.type in (pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN) and event.button in (1, 2, 3):
                mx, my = event.pos
                for key, rect in self.menu_cards():
                    if rect.collidepoint(mx, my):
                        self.start(key)
                        try:
                            self.play("click")
                        except Exception:
                            pass
                        break
        except Exception as e:
            import traceback
            traceback.print_exc()

    def mouse_down(self, event):
        mx, my = event.pos
        if event.button == 4:
            self.camera.zoom = min(1.8, self.camera.zoom + 0.08)
            self.clamp_camera()
            return
        if event.button == 5:
            self.camera.zoom = max(0.55, self.camera.zoom - 0.08)
            self.clamp_camera()
            return
        if mx >= VIEW_W:
            self.sidebar_click(mx, my)
            return
        if my < TOP_H or my > TOP_H + VIEW_H:
            return
        if event.button == 2:
            self.panning = True
            self.pan_start = event.pos
            self.pan_cam = (self.camera.x, self.camera.y)
        elif event.button == 3:
            self.select_ids([])
            return
        elif event.button == 1:
            self.play("click")
            if self.placing:
                self.place_structure(*self.screen_to_world(mx, my))
                return
            self.drag_start = event.pos
            self.drag_pos = event.pos

    def mouse_motion(self, event):
        if self.panning:
            dx = event.pos[0] - self.pan_start[0]
            dy = event.pos[1] - self.pan_start[1]
            self.camera.x = self.pan_cam[0] - dx / self.camera.zoom
            self.camera.y = self.pan_cam[1] - dy / self.camera.zoom
            self.clamp_camera()
        elif self.drag_start:
            self.drag_pos = event.pos

    def mouse_up(self, event):
        if event.button == 2:
            self.panning = False
            return
        if event.button != 1 or not self.drag_start:
            return
        sx, sy = self.drag_start
        ex, ey = event.pos
        self.drag_start = None
        self.drag_pos = None
        if abs(ex - sx) > 8 or abs(ey - sy) > 8:
            rect = pygame.Rect(min(sx, ex), min(sy, ey), abs(ex - sx), abs(ey - sy))
            selected = []
            for entity in self.entities:
                if entity.team == TEAM_RED and entity.kind == "unit":
                    px, py = self.world_to_screen(entity.x, entity.y)
                    if rect.collidepoint(px, py):
                        selected.append(entity.id)
            self.select_ids(selected, add=pygame.key.get_mods() & pygame.KMOD_SHIFT)
        else:
            wx, wy = self.screen_to_world(ex, ey)
            hit = self.hit_entity(wx, wy, TEAM_RED)
            if hit:
                self.select_ids([hit.id], add=pygame.key.get_mods() & pygame.KMOD_SHIFT)
            elif not pygame.key.get_mods() & pygame.KMOD_SHIFT:
                if any(e.kind == "unit" for e in self.selected()):
                    self.command_selected(ex, ey)
                else:
                    self.select_ids([])

    def sidebar_click(self, mx, my):
        mini_rect = pygame.Rect(VIEW_W + 22, TOP_H + 80, MINIMAP_W, MINIMAP_H)
        if mini_rect.collidepoint(mx, my):
            self.play("click")
            rel_x = (mx - mini_rect.x) / mini_rect.w
            rel_y = (my - mini_rect.y) / mini_rect.h
            self.camera.x = rel_x * WORLD_W
            self.camera.y = rel_y * WORLD_H
            self.clamp_camera()
            return
        for button in self.buttons:
            if button.rect.collidepoint(mx, my):
                self.play("click")
                if button.kind == "tab":
                    self.active_tab = button.action
                elif button.kind == "build":
                    self.try_build(button.action)
                elif button.kind == "train":
                    self.train_unit(button.action)
                return

    def command_selected(self, mx, my):
        wx, wy = self.screen_to_world(mx, my)
        target = self.hit_entity(wx, wy, TEAM_BLUE)
        units = [e for e in self.selected() if e.kind == "unit"]
        if not units:
            return
        for i, unit in enumerate(units):
            row = i // 4
            col = i % 4
            spread = 28 if len(units) > 1 else 0
            self.set_unit_destination(unit, wx + (col - 1.5) * spread, wy + row * spread)
            unit.target_id = target.id if target else None
            unit.attack_move = bool(target)
            unit.state = "attack" if target else "move"
        self.alert("Attack order confirmed" if target else "Moving out")
        if self.command_voice_timer <= 0:
            self.play("affirmative" if target else "move")
            self.command_voice_timer = 1.2

    def hit_entity(self, wx, wy, team=None):
        for entity in reversed(self.entities):
            if team and entity.team != team:
                continue
            if entity.kind == "structure":
                if entity.rect().collidepoint(wx, wy):
                    return entity
            elif distance_xy(wx, wy, entity.x, entity.y) <= self.unit_hit_radius(entity):
                return entity
        return None

    def unit_hit_radius(self, entity):
        radius = entity.size * 1.8
        if entity.type == "v3":
            radius = max(radius, 44)
        return radius

    def select_ids(self, ids, add=False):
        if add:
            existing = set(self.selected_ids)
            for entity_id in ids:
                if entity_id in existing:
                    existing.remove(entity_id)
                else:
                    existing.add(entity_id)
            self.selected_ids = list(existing)
        else:
            self.selected_ids = ids
        for entity in self.entities:
            entity.selected = entity.id in self.selected_ids
        if ids and not add:
            selected = self.selected()
            if any(e.type == "dog" for e in selected):
                self.play("dog")
            elif self.command_voice_timer <= 0:
                self.play(random.choice(["yes_commander", "yes_sir", "absolutely"]))
                self.command_voice_timer = 1.0

    def draw(self):
        if not self.difficulty:
            self.draw_menu()
            return
        self.screen.fill((8, 8, 8))
        self.draw_world()
        self.draw_topbar()
        self.draw_sidebar()
        self.draw_bottombar()
        if self.paused:
            self.draw_pause_overlay()
        if self.game_over:
            text = "VICTORY" if self.winner == TEAM_RED else "DEFEAT"
            self.draw_center_banner(text, "Press R for menu")
        self.draw_nav_vis_overlay()

    def draw_menu(self):
        # Ultra dark background for contrast
        self.screen.fill((8, 3, 1))
        
        # Draw animated fire field at bottom (inspired by fire.html)
        self.draw_fire_background()
        
        # Add atmospheric glow and particles
        self.draw_atmospheric_effects()
        
        # Draw title with intense glow
        self.draw_menu_title()
        
        # Draw difficulty buttons with fire effect
        self.draw_difficulty_buttons()
        
        # Hint text
        hint = self.small.render("Click a difficulty or press 1(Easy) / 2(Medium) / 3(Hard)", True, (200, 140, 90))
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_W // 2, SCREEN_H - 40)))

    def draw_fire_background(self):
        """Draw animated fire particles at bottom of screen"""
        if not hasattr(self, 'menu_fire_particles'):
            self.menu_fire_particles = []
            self.menu_embers = []
            self.menu_smoke = []
            for _ in range(150):
                self.menu_fire_particles.append({
                    'x': random.random() * SCREEN_W,
                    'y': SCREEN_H + random.random() * 100,
                    'vx': (random.random() - 0.5) * 2,
                    'vy': -(2 + random.random() * 3),
                    'life': 1.0,
                    'max_life': 1.0 + random.random() * 0.5,
                    'size': random.randint(20, 60),
                    'hue': random.randint(0, 60),
                })
            for _ in range(60):
                self.menu_embers.append({
                    'x': random.random() * SCREEN_W,
                    'y': SCREEN_H,
                    'vx': (random.random() - 0.5) * 3,
                    'vy': -(3 + random.random() * 5),
                    'life': 1.0,
                    'size': random.randint(2, 5),
                })
            for _ in range(40):
                self.menu_smoke.append({
                    'x': random.random() * SCREEN_W,
                    'y': SCREEN_H - 200,
                    'vx': (random.random() - 0.5) * 0.5,
                    'vy': -0.5,
                    'life': 1.0,
                    'size': random.randint(40, 100),
                    'opacity': 0.1,
                })
        
        # Update and draw smoke particles (background layer)
        for p in self.menu_smoke:
            p['y'] += p['vy']
            p['life'] -= 0.008
            if p['life'] > 0:
                color = (60, 40, 20)
                pygame.draw.circle(self.screen, color, (int(p['x']), int(p['y'])), max(2, int(p['size'] * (1 - p['life']) * 0.5)))
        
        # Update and draw fire particles
        alive = []
        for p in self.menu_fire_particles:
            p['y'] += p['vy']
            p['vx'] += (random.random() - 0.5) * 0.3
            p['life'] -= 0.015
            p['size'] *= 0.98
            
            if p['life'] > 0:
                alive.append(p)
                # Gradient color based on life (bright yellow -> orange -> red -> dark)
                if p['life'] > 0.7:
                    color = (255, 200 + int(55 * p['life']), 0)
                elif p['life'] > 0.4:
                    color = (255, int(180 * (p['life'] - 0.4) / 0.3), 0)
                elif p['life'] > 0.2:
                    color = (220, int(80 * (p['life'] - 0.2) / 0.2), 0)
                else:
                    color = (180, 30, 0)
                
                try:
                    pygame.draw.circle(self.screen, color, (int(p['x']), int(p['y'])), max(1, int(p['size'] * p['life'])))
                except:
                    pass
            else:
                # Respawn at bottom
                p['y'] = SCREEN_H + random.random() * 50
                p['x'] = random.random() * SCREEN_W
                p['life'] = 1.0
                p['size'] = random.randint(20, 60)
                alive.append(p)
        
        self.menu_fire_particles = alive
        
        # Update and draw embers (bright fast particles)
        alive_embers = []
        for e in self.menu_embers:
            e['y'] += e['vy']
            e['vx'] *= 0.99
            e['vy'] *= 0.98
            e['life'] -= 0.02
            
            if e['life'] > 0:
                alive_embers.append(e)
                ember_color = (255, 255, int(100 * e['life']))
                pygame.draw.circle(self.screen, ember_color, (int(e['x']), int(e['y'])), max(1, int(e['size'] * e['life'])))
            else:
                e['y'] = SCREEN_H
                e['x'] = random.random() * SCREEN_W
                e['life'] = 1.0
                alive_embers.append(e)
        
        self.menu_embers = alive_embers

    def draw_atmospheric_effects(self):
        """Draw glowing particles and light effects"""
        if not hasattr(self, 'menu_glow_time'):
            self.menu_glow_time = 0
            self.menu_sparks = []
        
        self.menu_glow_time += 0.016
        
        # Flickering base glow at bottom (stronger effect)
        flicker = 0.6 + 0.4 * math.sin(self.menu_glow_time * 3) + random.random() * 0.2
        glow_height = 500
        for i in range(glow_height):
            alpha = int((1 - i / glow_height) ** 1.5 * 120 * flicker)
            intensity = int(60 * (1 - i / glow_height))
            color = (min(220 + intensity, 255), min(80 + intensity, 255), 10)
            try:
                glow_line = pygame.Surface((SCREEN_W, 1), pygame.SRCALPHA)
                glow_line.fill((color[0], color[1], color[2], alpha // 4))
                self.screen.blit(glow_line, (0, SCREEN_H - i))
            except:
                pass
        
        # Random bright sparks
        for _ in range(20):
            x = random.randint(0, SCREEN_W)
            y = random.randint(SCREEN_H - 350, SCREEN_H - 100)
            colors = [(255, 255, 200), (255, 200, 0), (255, 100, 0), (255, 150, 50)]
            color = random.choice(colors)
            size = random.randint(1, 4)
            pygame.draw.circle(self.screen, color, (x, y), size)

    def draw_menu_title(self):
        """Draw the main title with intense neon glow"""
        title_text = "RED ALERT MINI"
        subtitle_text = "- BLOOD, STEEL & FIRE -"
        title_y = 120
        
        # Draw subtle glow layers (less intense)
        for offset in range(6, 1, -1):
            color_intensity = 1 - offset / 6
            glow_color = (int(200 * color_intensity), int(80 * color_intensity), 0)
            glow_title = self.big.render(title_text, True, glow_color)
            glow_rect = glow_title.get_rect(center=(SCREEN_W // 2 + offset // 2, title_y + offset // 2))
            self.screen.blit(glow_title, glow_rect)
        
        # Main title (only once)
        title = self.big.render(title_text, True, (255, 160, 50))
        self.screen.blit(title, title.get_rect(center=(SCREEN_W // 2, title_y)))
        
        # Subtitle
        sub = self.font.render(subtitle_text, True, (255, 140, 80))
        self.screen.blit(sub, sub.get_rect(center=(SCREEN_W // 2, 210)))

    def draw_difficulty_buttons(self):
        """Draw enhanced difficulty selection buttons"""
        for key, rect in self.menu_cards():
            hovered = key == self.menu_hover_key
            # Glow effect behind button
            glow_rect = rect.inflate(20, 20)
            glow_surf = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
            glow_alpha = 80 if hovered else 40
            pygame.draw.rect(glow_surf, (255, 100, 0, glow_alpha), (0, 0, glow_rect.w, glow_rect.h), border_radius=10)
            self.screen.blit(glow_surf, glow_rect)
            
            # Button frame with fire colors
            border_color = (255, 200, 100) if hovered else (255, 120, 40)
            pygame.draw.rect(self.screen, border_color, rect, 4, border_radius=8)
            pygame.draw.rect(self.screen, (255, 80, 20), pygame.Rect(rect.x + 2, rect.y + 2, rect.w - 4, rect.h - 4), 2, border_radius=7)
            
            # Button background with transparency
            btn_bg = pygame.Surface((rect.w - 4, rect.h - 4), pygame.SRCALPHA)
            bg_alpha = 240 if hovered else 200
            bg_color = (60, 25, 10, bg_alpha) if hovered else (40, 15, 5, bg_alpha)
            btn_bg.fill(bg_color)
            self.screen.blit(btn_bg, (rect.x + 2, rect.y + 2))
            
            label = DIFFICULTIES[key]["label"]
            num_label = {"easy": "1", "medium": "2", "hard": "3"}[key]
            
            # Draw number indicator
            num_font = pygame.font.Font(None, 48)
            num_text = num_font.render(num_label, True, (255, 180, 80))
            self.screen.blit(num_text, (rect.x + 20, rect.y + 25))
            
            # Difficulty icon
            icon_x = rect.centerx
            icon_y = rect.y + 40
            icon_color = (255, 200, 100)
            
            if key == "easy":
                pygame.draw.line(self.screen, icon_color, (icon_x - 12, icon_y), (icon_x + 12, icon_y), 4)
                pygame.draw.line(self.screen, icon_color, (icon_x, icon_y - 12), (icon_x, icon_y + 12), 4)
            elif key == "medium":
                for offset in [-6, 0, 6]:
                    pygame.draw.line(self.screen, icon_color, (icon_x - 15, icon_y + offset), (icon_x + 15, icon_y + offset), 3)
            else:
                star_size = 12
                points = []
                for i in range(10):
                    angle = i * math.pi / 5 - math.pi / 2
                    radius = star_size if i % 2 == 0 else star_size * 0.4
                    points.append((icon_x + radius * math.cos(angle), icon_y + radius * math.sin(angle)))
                pygame.draw.polygon(self.screen, icon_color, points)
                pygame.draw.polygon(self.screen, (255, 220, 120), points, 2)
            
            # Label text
            txt = self.font.render(label.upper(), True, (255, 240, 180))
            self.screen.blit(txt, (rect.centerx - 30, rect.y + 60))
            
            # Description
            descriptions = {
                "easy": "Softer Opposition",
                "medium": "Balanced Conflict",
                "hard": "Extreme Pressure"
            }
            desc = self.small.render(descriptions[key], True, (210, 160, 100))
            self.screen.blit(desc, (rect.centerx - 40, rect.y + 80))

    def menu_cards(self):
        w = 240
        h = 108
        y = 320
        gap = 28
        start_x = SCREEN_W // 2 - (w * 3 + gap * 2) // 2
        return [
            ("easy", pygame.Rect(start_x, y, w, h)),
            ("medium", pygame.Rect(start_x + w + gap, y, w, h)),
            ("hard", pygame.Rect(start_x + (w + gap) * 2, y, w, h)),
        ]

    def draw_nav_vis_overlay(self):
        if not self.show_nav_vis or self.nav_vis_surface is None:
            return
        scale = 3
        w = self.nav_vis_surface.get_width() * scale
        h = self.nav_vis_surface.get_height() * scale
        scaled = pygame.transform.scale(self.nav_vis_surface, (w, h))
        overlay = scaled.convert()
        overlay.set_alpha(180)
        self.screen.blit(overlay, (SCREEN_W - w - 10, TOP_H + 10))

    def draw_world(self):
        viewport = pygame.Rect(0, TOP_H, VIEW_W, VIEW_H)
        pygame.draw.rect(self.screen, (20, 22, 18), viewport)
        half_w = VIEW_W / 2 / self.camera.zoom
        half_h = VIEW_H / 2 / self.camera.zoom
        vx = int(max(0, self.camera.x - half_w))
        vy = int(max(0, self.camera.y - half_h))
        vw = int(min(WORLD_W - vx, half_w * 2))
        vh = int(min(WORLD_H - vy, half_h * 2))
        view = pygame.Rect(vx, vy, vw, vh)
        if vw <= 0 or vh <= 0:
            return
        try:
            world_part = self.map_surface.subsurface(view).copy()
            scaled = pygame.transform.smoothscale(world_part, (max(1, round(view.w * self.camera.zoom)), max(1, round(view.h * self.camera.zoom))))
            sx, sy = self.world_to_screen(view.x, view.y)
            self.screen.blit(scaled, (sx, sy))
        except Exception:
            return
        self.draw_grid()
        if self.debug_nav:
            self.draw_nav_debug()
        for ore in self.ore:
            if ore.available:
                self.draw_ore(ore)
        for entity in sorted(self.entities, key=lambda e: (e.y, e.kind == "unit")):
            self.draw_entity(entity)
        for particle in self.particles:
            self.draw_particle(particle)
        if self.placing:
            self.draw_placement_preview()
        if self.drag_start and self.drag_pos:
            rect = pygame.Rect(
                min(self.drag_start[0], self.drag_pos[0]),
                min(self.drag_start[1], self.drag_pos[1]),
                abs(self.drag_pos[0] - self.drag_start[0]),
                abs(self.drag_pos[1] - self.drag_start[1]),
            )
            pygame.draw.rect(self.screen, (240, 210, 80), rect, 1)
            fill = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            fill.fill((240, 210, 80, 32))
            self.screen.blit(fill, rect)

    def draw_grid(self):
        if self.camera.zoom < 0.9:
            return
        left, top = self.screen_to_world(0, TOP_H)
        right, bottom = self.screen_to_world(VIEW_W, TOP_H + VIEW_H)
        start_x = int(left // TILE) * TILE
        start_y = int(top // TILE) * TILE
        color = (0, 0, 0, 38)
        grid = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
        for x in range(start_x, int(right) + TILE, TILE):
            sx, _ = self.world_to_screen(x, 0)
            pygame.draw.line(grid, color, (sx, 0), (sx, VIEW_H))
        for y in range(start_y, int(bottom) + TILE, TILE):
            _, sy = self.world_to_screen(0, y)
            pygame.draw.line(grid, color, (0, sy - TOP_H), (VIEW_W, sy - TOP_H))
        self.screen.blit(grid, (0, TOP_H))

    def draw_nav_debug(self):
        left, top = self.screen_to_world(0, TOP_H)
        right, bottom = self.screen_to_world(VIEW_W, TOP_H + VIEW_H)
        start_gx = max(0, int(left // NAV_TILE))
        end_gx = min(self.nav_grid.cols - 1, int(right // NAV_TILE) + 1)
        start_gy = max(0, int(top // NAV_TILE))
        end_gy = min(self.nav_grid.rows - 1, int(bottom // NAV_TILE) + 1)
        overlay = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
        for gy in range(start_gy, end_gy + 1):
            for gx in range(start_gx, end_gx + 1):
                wx = gx * NAV_TILE
                wy = gy * NAV_TILE
                sx, sy = self.world_to_screen(wx, wy)
                rect = pygame.Rect(
                    round(sx),
                    round(sy - TOP_H),
                    max(1, round(NAV_TILE * self.camera.zoom)),
                    max(1, round(NAV_TILE * self.camera.zoom)),
                )
                if self.nav_grid.static_blocked[gy][gx]:
                    color = (220, 35, 35, 105)
                elif self.nav_grid.building_occupied[gy][gx]:
                    color = (255, 160, 40, 115)
                else:
                    color = (40, 210, 90, 38)
                pygame.draw.rect(overlay, color, rect)
                if self.camera.zoom >= 0.9:
                    pygame.draw.rect(overlay, (0, 0, 0, 40), rect, 1)
        self.screen.blit(overlay, (0, TOP_H))

        for unit in self.selected():
            if unit.kind != "unit" or not unit.path:
                continue
            points = [self.world_to_screen(unit.x, unit.y)] + [self.world_to_screen(x, y) for x, y in unit.path]
            if len(points) > 1:
                pygame.draw.lines(self.screen, (90, 210, 255), False, [(round(x), round(y)) for x, y in points], 2)

    def draw_ore(self, ore):
        sx, sy = self.world_to_screen(ore.x, ore.y)
        if not self.on_view(sx, sy, 44):
            return
        zoom = self.camera.zoom
        tick = pygame.time.get_ticks() / 1000
        pulse = 0.5 + 0.5 * math.sin(tick * 4.4 + ore.x * 0.03 + ore.y * 0.02)
        shimmer = 0.5 + 0.5 * math.sin(tick * 7.0 + ore.x * 0.01)
        cx, cy = round(sx), round(sy)

        glow_r = max(10, round((16 + 5 * pulse) * zoom))
        glow = pygame.Surface((glow_r * 2 + 4, glow_r * 2 + 4), pygame.SRCALPHA)
        gc = glow_r + 2
        for layer in range(4):
            radius = max(1, glow_r - layer * max(2, round(3 * zoom)))
            alpha = max(0, round((42 + 28 * pulse) * (1 - layer / 4)))
            pygame.draw.circle(glow, (255, 216, 70, alpha), (gc, gc), radius)
        self.screen.blit(glow, (cx - gc, cy - gc))

        shadow_w = max(6, round(14 * zoom))
        shadow_h = max(3, round(5 * zoom))
        pygame.draw.ellipse(
            self.screen,
            (45, 28, 8),
            pygame.Rect(cx - shadow_w // 2, cy + round(7 * zoom), shadow_w, shadow_h),
        )

        def draw_diamond(dx, dy, size, fill, edge):
            px = cx + round(dx * zoom)
            py = cy + round(dy * zoom)
            r = max(3, round(size * zoom * (0.88 + pulse * 0.1)))
            points = [(px, py - r), (px + r, py), (px, py + r), (px - r, py)]
            pygame.draw.polygon(self.screen, edge, points)
            inner = max(2, r - max(1, round(2 * zoom)))
            inner_points = [(px, py - inner), (px + inner, py), (px, py + inner), (px - inner, py)]
            pygame.draw.polygon(self.screen, fill, inner_points)
            glint = max(1, round(r * 0.35))
            pygame.draw.line(self.screen, (255, 255, 210), (px - glint, py - glint), (px, py - r + 1), max(1, round(zoom)))

        draw_diamond(0, 0, 7, (255, 220, 72), (122, 77, 18))
        draw_diamond(-7, 5, 4.2, (245, 183, 45), (104, 64, 14))
        draw_diamond(7, 4, 3.8, (255, 239, 126), (119, 75, 17))

        if shimmer > 0.72:
            sparkle_r = max(2, round(4 * zoom * shimmer))
            sparkle_x = cx + round(10 * zoom)
            sparkle_y = cy - round(10 * zoom)
            pygame.draw.line(self.screen, (255, 250, 180), (sparkle_x - sparkle_r, sparkle_y), (sparkle_x + sparkle_r, sparkle_y), 1)
            pygame.draw.line(self.screen, (255, 250, 180), (sparkle_x, sparkle_y - sparkle_r), (sparkle_x, sparkle_y + sparkle_r), 1)

    def draw_entity(self, entity):
        if entity.kind == "structure":
            self.draw_structure(entity)
        else:
            self.draw_unit(entity)

    def draw_structure(self, entity):
        sx, sy = self.world_to_screen(entity.x, entity.y)
        w = max(2, entity.w * self.camera.zoom)
        h = max(2, entity.h * self.camera.zoom)
        if not self.on_view(sx + w / 2, sy + h / 2, max(w, h)):
            return
        rect = pygame.Rect(round(sx), round(sy), round(w), round(h))
        asset = self.structure_asset(entity)
        if asset:
            self.blit_fit(asset, rect, 1.08)
        else:
            pygame.draw.rect(self.screen, entity.color, rect)
            pygame.draw.rect(self.screen, (45, 25, 18), rect, 2)
        if entity.selected:
            pygame.draw.rect(self.screen, (255, 225, 40), rect, 2)
            if entity.atk > 0:
                cx, cy = self.world_to_screen(*entity.center())
                pygame.draw.circle(self.screen, (255, 55, 35), (round(cx), round(cy)), round(entity.range * self.camera.zoom), 1)
            if entity.type == "radar":
                cx, cy = self.world_to_screen(*entity.center())
                pygame.draw.circle(self.screen, (240, 200, 60), (round(cx), round(cy)), round(300 * self.camera.zoom), 1)
        self.draw_health(entity, rect)

    def draw_unit(self, entity):
        sx, sy = self.world_to_screen(entity.x, entity.y)
        r = max(4, entity.size * self.camera.zoom)
        if not self.on_view(sx, sy, r + 20):
            return
        pygame.draw.ellipse(self.screen, (0, 0, 0, 110), (sx - r, sy + r * 0.35, r * 2.2, r * 0.8))
        asset = self.unit_asset(entity)
        if asset:
            rect = pygame.Rect(0, 0, round(r * 3.0), round(r * 3.0))
            rect.center = (round(sx), round(sy))
            self.blit_fit(asset, rect, 1)
        else:
            pygame.draw.circle(self.screen, entity.color, (round(sx), round(sy)), round(r))
            cannon_x = sx + math.cos(entity.facing) * r * 1.25
            cannon_y = sy + math.sin(entity.facing) * r * 1.25
            pygame.draw.line(self.screen, (35, 24, 18), (sx, sy), (cannon_x, cannon_y), max(2, round(r * 0.25)))
        if entity.selected:
            pygame.draw.circle(self.screen, (255, 230, 40), (round(sx), round(sy)), round(r + 5), 2)
        bar = pygame.Rect(round(sx - r), round(sy - r - 10), round(r * 2), 4)
        self.draw_health(entity, bar, force=entity.selected or entity.hp < entity.max_hp)

    def structure_asset(self, entity):
        prefix = "red" if entity.team == TEAM_RED else "blue"
        key = f"{prefix}_{entity.type}"
        if entity.type == "conyard":
            key = f"{prefix}_conyard"
        return self.assets.get(key)

    def unit_asset(self, entity):
        if entity.type in ("rhino", "grizzly"):
            prefix = "red" if entity.team == TEAM_RED else "blue"
            return self.assets.get(f"{prefix}_rhino_{self.facing_frame(entity)}") or self.assets.get(f"{prefix}_rhino_0") or self.assets.get("red_rhino")
        if entity.team == TEAM_BLUE:
            if entity.type == "gi":
                return self.assets.get("blue_troop")
            if entity.type in ("apocalypse", "prism"):
                return self.assets.get("blue_apocalypse")
            if entity.type == "v3":
                return self.assets.get("blue_rhino_0")
            return self.assets.get("blue_troop")
        return {
            "conscript": self.assets.get("red_troop"),
            "dog": self.assets.get("red_dog"),
            "tesla_trooper": self.assets.get("red_tesla_trooper") or self.assets.get("red_troop"),
            "v3": self.assets.get("red_v3"),
            "apocalypse": self.assets.get("red_apocalypse"),
        }.get(entity.type)

    def facing_frame(self, entity):
        # Asset frames are north-first and then clockwise: 0 up, 2 right, 4 down, 6 left.
        angle = (entity.facing + math.pi / 2 + math.tau) % math.tau
        return int(((angle + math.tau / 16) % math.tau) / (math.tau / 8))

    def blit_fit(self, image, rect, scale=1.0):
        iw, ih = image.get_size()
        if iw == 0 or ih == 0:
            return
        ratio = ih / iw
        fit_w = rect.w * scale
        fit_h = fit_w * ratio
        if fit_h > rect.h * scale:
            fit_h = rect.h * scale
            fit_w = fit_h / ratio
        scaled = pygame.transform.smoothscale(image, (max(1, round(fit_w)), max(1, round(fit_h))))
        out = scaled.get_rect(center=rect.center)
        self.screen.blit(scaled, out)

    def draw_health(self, entity, rect, force=True):
        if not force:
            return
        pct = clamp(entity.hp / entity.max_hp, 0, 1)
        back = pygame.Rect(rect.x, rect.y - 8, rect.w, 5)
        pygame.draw.rect(self.screen, (12, 12, 12), back)
        color = (45, 210, 75) if pct > 0.55 else (220, 170, 20) if pct > 0.25 else (220, 45, 30)
        pygame.draw.rect(self.screen, color, (back.x, back.y, round(back.w * pct), back.h))

    def draw_particle(self, particle):
        sx, sy = self.world_to_screen(particle.x, particle.y)
        if particle.text:
            surf = self.small.render(particle.text, True, particle.color)
            self.screen.blit(surf, surf.get_rect(center=(sx, sy)))
        else:
            pygame.draw.circle(self.screen, particle.color, (round(sx), round(sy)), max(1, round(particle.size)))

    def draw_placement_preview(self):
        mx, my = pygame.mouse.get_pos()
        if mx >= VIEW_W or my < TOP_H or my > TOP_H + VIEW_H:
            return
        wx, wy = self.screen_to_world(mx, my)
        data = STRUCT_DEFS[self.placing]
        gx = int(wx // TILE)
        gy = int(wy // TILE)
        wt = data.get("w_tiles", data["size"])
        ht = data.get("h_tiles", data["size"])
        sx, sy = self.world_to_screen(gx * TILE, gy * TILE)
        rect = pygame.Rect(round(sx), round(sy), round(wt * TILE * self.camera.zoom), round(ht * TILE * self.camera.zoom))
        valid = self.valid_placement(gx, gy, wt, ht)
        color = (40, 220, 80, 90) if valid else (240, 40, 30, 90)
        fill = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        fill.fill(color)
        self.screen.blit(fill, rect)
        pygame.draw.rect(self.screen, color[:3], rect, 2)

    def valid_placement(self, gx, gy, wt, ht):
        rect = pygame.Rect(gx * TILE, gy * TILE, wt * TILE, ht * TILE)
        if rect.left < 0 or rect.top < 0 or rect.right > WORLD_W or rect.bottom > WORLD_H:
            return False
        if any(e.kind == "structure" and rect.colliderect(e.rect()) for e in self.entities):
            return False
        if not self.nav_grid.rect_walkable_for_building(rect):
            return False
        return any(e.kind == "structure" and e.team == TEAM_RED and distance_xy(rect.centerx, rect.centery, *e.center()) < BUILD_RADIUS for e in self.entities)

    def draw_topbar(self):
        pygame.draw.rect(self.screen, (18, 16, 14), (0, 0, SCREEN_W, TOP_H))
        pygame.draw.line(self.screen, (160, 40, 28), (0, TOP_H - 1), (SCREEN_W, TOP_H - 1), 2)
        logo = self.font.render("RED ALERT MINI", True, (245, 55, 35))
        self.screen.blit(logo, (18, 12))
        diff = DIFFICULTIES[self.difficulty]["label"].upper()
        stat = self.small.render(f"{diff}   WAVE {self.wave}   POWER {self.power}", True, (240, 205, 140))
        self.screen.blit(stat, (260, 15))
        msg_color = (255, 205, 70) if self.message_timer > 0 else (150, 135, 115)
        msg = self.small.render(self.message, True, msg_color)
        self.screen.blit(msg, (690, 15))
        interval = DIFFICULTIES[self.difficulty]["wave_interval"]
        pct = clamp(self.wave_timer / interval, 0, 1)
        pygame.draw.rect(self.screen, (50, 30, 20), (SCREEN_W - 190, 16, 150, 12))
        pygame.draw.rect(self.screen, (210, 40, 28), (SCREEN_W - 190, 16, round(150 * pct), 12))
        self.draw_pause_button()

    def draw_pause_button(self):
        """Draw the pause/resume toggle button in the top-right corner."""
        pause_rect = pygame.Rect(SCREEN_W - 38, 10, 26, 26)
        mouse_pos = pygame.mouse.get_pos()
        hovered = pause_rect.collidepoint(mouse_pos) and not self.paused
        # Background (brighter when hovered)
        bg = (70, 32, 22) if hovered else (40, 20, 14)
        border = (245, 95, 50) if hovered else (160, 40, 28)
        pygame.draw.rect(self.screen, bg, pause_rect, border_radius=4)
        pygame.draw.rect(self.screen, border, pause_rect, 2, border_radius=4)
        # Icon: two bars when running, triangle when paused
        cx, cy = pause_rect.center
        if self.paused:
            # Play triangle
            tri = [
                (cx - 5, cy - 7),
                (cx - 5, cy + 7),
                (cx + 7, cy),
            ]
            pygame.draw.polygon(self.screen, (255, 210, 90), tri)
        else:
            # Pause bars
            bar_w, bar_h, gap = 4, 12, 4
            pygame.draw.rect(self.screen, (255, 210, 90),
                             (cx - gap - bar_w, cy - bar_h // 2, bar_w, bar_h), border_radius=1)
            pygame.draw.rect(self.screen, (255, 210, 90),
                             (cx + gap, cy - bar_h // 2, bar_w, bar_h), border_radius=1)
        # Tooltip-style hint
        if hovered:
            tip = self.small.render("Pause (P)", True, (240, 200, 140))
            self.screen.blit(tip, tip.get_rect(midright=(pause_rect.x - 6, pause_rect.centery)))

    def draw_pause_overlay(self):
        """Black out the world, freeze simulation visuals, and draw the pause menu."""
        # 1. Solid black wash over the whole screen
        blackout = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        blackout.fill((0, 0, 0, 215))
        self.screen.blit(blackout, (0, 0))

        # 2. Centered panel
        panel_w, panel_h = 360, 360
        panel = pygame.Rect(0, 0, panel_w, panel_h)
        panel.center = (SCREEN_W // 2, SCREEN_H // 2)
        # Outer gold + inner purple borders for a Yuri feel
        pygame.draw.rect(self.screen, (14, 8, 8), panel.inflate(8, 8), border_radius=10)
        pygame.draw.rect(self.screen, (200, 55, 35), panel.inflate(4, 4), border_radius=8)
        pygame.draw.rect(self.screen, (22, 8, 28), panel, border_radius=6)
        pygame.draw.rect(self.screen, (120, 45, 175), panel, 2, border_radius=6)

        # 3. Title
        title = self.big.render("PAUSED", True, (255, 90, 55))
        self.screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 38)))
        sub = self.font.render("COMMAND HALTED", True, (230, 190, 135))
        self.screen.blit(sub, sub.get_rect(center=(panel.centerx, panel.y + 76)))

        # 4. Buttons (Resume, Mute, Vol-, Vol+, Quit)
        self.paused_buttons = []
        btn_w, btn_h = 280, 40
        gap = 10
        first_y = panel.y + 110
        mouse_pos = pygame.mouse.get_pos()
        for idx, (label, action, sub_label) in enumerate([
            ("RESUME GAME", "resume", "P"),
            ("MUTE / UNMUTE", "mute", "M"),
            ("SFX VOLUME -", "vol_down", "-"),
            ("SFX VOLUME +", "vol_up", "+"),
            ("QUIT TO MENU", "quit", "ESC"),
        ]):
            bx = panel.centerx - btn_w // 2
            by = first_y + idx * (btn_h + gap)
            rect = pygame.Rect(bx, by, btn_w, btn_h)
            hovered = rect.collidepoint(mouse_pos)

            # Active state for mute
            active = (action == "mute" and self.muted)
            if active:
                bg = (140, 35, 35)
                border = (255, 120, 80)
            elif hovered:
                bg = (60, 25, 80)
                border = (245, 185, 45)
            else:
                bg = (34, 14, 50)
                border = (90, 50, 115)
            pygame.draw.rect(self.screen, bg, rect, border_radius=5)
            pygame.draw.rect(self.screen, border, rect, 2, border_radius=5)

            # Label
            if action == "mute":
                text_color = (255, 230, 200) if self.muted else (210, 200, 230)
                label_text = "MUTED — CLICK TO UNMUTE" if self.muted else "SOUND ON — CLICK TO MUTE"
            else:
                text_color = (255, 230, 200) if hovered else (220, 200, 230)
                label_text = label
            lbl_surf = self.font.render(label_text, True, text_color)
            self.screen.blit(lbl_surf, lbl_surf.get_rect(center=(rect.centerx, rect.centery - 4)))

            # Sub-line: hotkey or volume level
            if action in ("vol_down", "vol_up"):
                vol_pct = round(self.sfx_volume * 100)
                bar_w = 120
                bar_x = rect.centerx - bar_w // 2
                bar_y = rect.bottom - 14
                pygame.draw.rect(self.screen, (15, 8, 25), (bar_x, bar_y, bar_w, 6), border_radius=2)
                pygame.draw.rect(self.screen, (245, 185, 45),
                                 (bar_x, bar_y, round(bar_w * self.sfx_volume), 6), border_radius=2)
                vtxt = self.small.render(f"{vol_pct}%", True, (255, 220, 110))
                self.screen.blit(vtxt, vtxt.get_rect(midright=(bar_x - 6, bar_y + 3)))
                vtxt2 = self.small.render(f"{vol_pct}%", True, (255, 220, 110))
                self.screen.blit(vtxt2, vtxt2.get_rect(midleft=(bar_x + bar_w + 6, bar_y + 3)))
            else:
                hint = self.small.render(f"[{sub_label}]", True, (150, 200, 240))
                self.screen.blit(hint, hint.get_rect(midright=(rect.right - 8, rect.centery - 4)))

            self.paused_buttons.append(Button(rect, label, action, "pause"))

        # 5. Footer hint
        footer = self.small.render("Press P or click RESUME to continue", True, (190, 160, 130))
        self.screen.blit(footer, footer.get_rect(center=(panel.centerx, panel.bottom - 16)))

    def draw_sidebar(self):
        x = VIEW_W
        # Deep dark purple background with metallic borders
        pygame.draw.rect(self.screen, (22, 10, 30), (x, TOP_H, SIDEBAR_W, VIEW_H))
        pygame.draw.line(self.screen, (120, 40, 175), (x, TOP_H), (x, TOP_H + VIEW_H), 3) # vertical divider
        
        # Add a retro grid background pattern to the sidebar to make it look premium
        for py in range(TOP_H + 10, TOP_H + VIEW_H, 40):
            pygame.draw.line(self.screen, (32, 15, 45), (x, py), (x + SIDEBAR_W, py), 1)

        # Title at the top
        title = self.font.render("YURI'S COMMAND", True, (245, 185, 45))
        self.screen.blit(title, (x + 22, TOP_H + 12))
        
        # Credits display at top of sidebar
        credit_label = self.small.render("CREDITS", True, (185, 145, 85))
        self.screen.blit(credit_label, (x + 22, TOP_H + 36))
        credit_val = self.font.render(f"${self.credits}", True, (255, 220, 90))
        self.screen.blit(credit_val, (x + 22, TOP_H + 52))
        
        # Draw Minimap
        self.draw_minimap(x + 22, TOP_H + 80)
        
        # Clear buttons list
        self.buttons = []
        
        # Draw Category Tabs below minimap
        tabs = [
            ("bldg", "BLDG"),
            ("defn", "DEFN"),
            ("inf", "INF"),
            ("veh", "VEH")
        ]
        tab_w = 50
        tab_h = 24
        tab_gap = 6
        start_tx = x + 22
        tab_y = TOP_H + 206
        for idx, (tab_id, label_str) in enumerate(tabs):
            tx = start_tx + idx * (tab_w + tab_gap)
            rect = pygame.Rect(tx, tab_y, tab_w, tab_h)
            is_active = (self.active_tab == tab_id)
            
            # Tab Styling
            bg_color = (130, 45, 185) if is_active else (35, 15, 50)
            border_color = (245, 185, 45) if is_active else (85, 45, 115)
            text_color = (255, 255, 255) if is_active else (155, 120, 175)
            
            # Double border on active tab for luxury feel
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=4)
            pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=4)
            if is_active:
                pygame.draw.rect(self.screen, (255, 220, 110), rect.inflate(-4, -4), 1, border_radius=2)
                
            tab_lbl = self.small.render(label_str, True, text_color)
            self.screen.blit(tab_lbl, tab_lbl.get_rect(center=rect.center))
            
            # Store tab button for clicks
            self.buttons.append(Button(rect, label_str, tab_id, "tab"))

        # Draw segmented Yuri-style Power Bar on the left
        power_y = TOP_H + 238
        power_h = 320
        power_w = 10
        power_x = x + 8
        # Outer bezel
        pygame.draw.rect(self.screen, (12, 5, 20), (power_x - 2, power_y - 2, power_w + 4, power_h + 4), border_radius=3)
        pygame.draw.rect(self.screen, (75, 30, 105), (power_x - 2, power_y - 2, power_w + 4, power_h + 4), 1, border_radius=3)
        
        # Calculate Power Levels
        produced = 10 + sum(e.pw for e in self.entities if e.kind == "structure" and e.team == TEAM_RED and e.pw > 0)
        consumed = sum(abs(e.pw) for e in self.entities if e.kind == "structure" and e.team == TEAM_RED and e.pw < 0)
        
        # Segmented colors
        segments = 32
        seg_h = power_h / segments
        for s in range(segments):
            sy = power_y + power_h - (s + 1) * seg_h
            # Map segments bottom-to-top: first 30% red, next 20% yellow, top 50% green
            ratio = s / segments
            if ratio < 0.3:
                color = (205, 35, 20)
            elif ratio < 0.5:
                color = (235, 185, 35)
            else:
                color = (35, 195, 40)
            # Draw segment (slightly smaller than full seg_h to show gaps)
            pygame.draw.rect(self.screen, color, (power_x, sy + 1, power_w, seg_h - 2))
            
        # Draw pointer showing consumption vs production
        if produced > 0:
            ptr_ratio = clamp(consumed / produced, 0.05, 0.95)
            ptr_y = power_y + power_h - ptr_ratio * power_h
        else:
            ptr_y = power_y + power_h - 10
        # Pointer shapes (gold pointer pointing to the level)
        pygame.draw.polygon(self.screen, (245, 185, 45), [
            (power_x - 7, ptr_y - 5),
            (power_x - 1, ptr_y),
            (power_x - 7, ptr_y + 5)
        ])
        pygame.draw.line(self.screen, (245, 185, 45), (power_x - 2, ptr_y), (power_x + power_w + 2, ptr_y), 2)

        # Draw 2-Column Construction Card Grid (right of power bar)
        # Select active tab items
        if self.active_tab == "bldg":
            active_items = [
                ("powerplant", "1", "Build"),
                ("barracks", "2", "Build"),
                ("warfactory", "3", "Build"),
                ("refinery", "4", "Build"),
                ("radar", "7", "Build")
            ]
        elif self.active_tab == "defn":
            active_items = [
                ("turret", "5", "Build"),
                ("tesla", "6", "Build"),
                ("wall", "8", "Build")
            ]
        elif self.active_tab == "inf":
            active_items = [
                ("conscript", "Q", "Train"),
                ("dog", "W", "Train"),
                ("tesla_trooper", "E", "Train")
            ]
        else: # veh
            active_items = [
                ("rhino", "A", "Train"),
                ("v3", "S", "Train"),
                ("apocalypse", "D", "Train")
            ]
            
        grid_start_x = x + 24
        grid_start_y = TOP_H + 238
        card_w = 104
        card_h = 74
        gap_x = 8
        gap_y = 8
        
        for idx, (item_id, hotkey, item_kind) in enumerate(active_items):
            col = idx % 2
            row = idx // 2
            cx = grid_start_x + col * (card_w + gap_x)
            cy = grid_start_y + row * (card_h + gap_y)
            card_rect = pygame.Rect(cx, cy, card_w, card_h)
            
            # 1. Tech requirements check
            locked = False
            lock_reason = ""
            if item_kind == "Train":
                if item_id in ("conscript", "dog", "tesla_trooper"):
                    if not any(e.team == TEAM_RED and e.type == "barracks" for e in self.entities):
                        locked = True
                        lock_reason = "REQ: BARRACKS"
                if item_id in ("rhino", "v3", "apocalypse"):
                    if not any(e.team == TEAM_RED and e.type == "warfactory" for e in self.entities):
                        locked = True
                        lock_reason = "REQ: FACTORY"
                        
            data = STRUCT_DEFS[item_id] if item_kind == "Build" else UNIT_DEFS[item_id]
            cost = data["cost"]
            
            # Hover / selected highlight
            mouse_pos = pygame.mouse.get_pos()
            hovered = card_rect.collidepoint(mouse_pos)
            
            # Highlight gold if placing or active
            is_active_placing = (self.placing == item_id)
            
            # Card border and bg colors
            bg_color = (25, 12, 38)
            if locked:
                bg_color = (15, 8, 22)
            border_color = (90, 50, 115)
            if hovered and not locked:
                border_color = (165, 80, 220)
            if is_active_placing:
                border_color = (245, 185, 45)
                
            # Draw Card Background and border
            pygame.draw.rect(self.screen, bg_color, card_rect, border_radius=4)
            pygame.draw.rect(self.screen, border_color, card_rect, 2, border_radius=4)
            
            # 2. Draw Sprite Icon (with fallbacks)
            icon_key = f"red_{item_id}"
            if item_id == "conscript":
                icon_key = "red_troop"
            elif item_id == "tesla_trooper":
                icon_key = "red_tesla_trooper"
            icon_rect = pygame.Rect(cx + 12, cy + 6, card_w - 24, 46)
            
            asset = self.assets.get(icon_key)
            if asset:
                self.blit_fit(asset, icon_rect, 1.0)
            else:
                # Color block representing item
                color = data.get("color", (120, 60, 160))
                pygame.draw.rect(self.screen, color, icon_rect.inflate(-4, -4), border_radius=2)
                
            # Gray scale shade if locked or player has insufficient credits
            if locked or self.credits < cost:
                shade = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                shade.fill((0, 0, 0, 120) if locked else (200, 30, 20, 60))
                self.screen.blit(shade, (cx, cy))
                
            # 3. Text indicators
            # Hotkey in top-left
            hk_lbl = self.small.render(f"[{hotkey}]", True, (80, 200, 240))
            self.screen.blit(hk_lbl, (cx + 6, cy + 4))
            
            # Name at bottom-left
            name_str = data["name"].upper().split()[0] # first word
            name_lbl = self.small.render(name_str, True, (255, 255, 255))
            self.screen.blit(name_lbl, (cx + 6, cy + 54))
            
            # Cost at bottom-right
            cost_lbl = self.small.render(f"${cost}", True, (245, 185, 45))
            self.screen.blit(cost_lbl, (cx + card_w - cost_lbl.get_width() - 6, cy + 54))
            
            # 4. Status overlay text (Locked, Ready, Training Progress)
            if locked:
                lock_lbl = self.small.render("LOCKED", True, (255, 50, 50))
                # Draw black label background
                pygame.draw.rect(self.screen, (10, 5, 15), (cx + 6, cy + 24, card_w - 12, 18), border_radius=2)
                self.screen.blit(lock_lbl, lock_lbl.get_rect(center=(cx + card_w // 2, cy + 33)))
            elif is_active_placing:
                # Flashing READY text for buildings
                if int(pygame.time.get_ticks() / 300) % 2 == 0:
                    pygame.draw.rect(self.screen, (12, 5, 20), (cx + 12, cy + 24, card_w - 24, 18), border_radius=2)
                    ready_lbl = self.small.render("READY", True, (245, 185, 45))
                    self.screen.blit(ready_lbl, ready_lbl.get_rect(center=(cx + card_w // 2, cy + 33)))
            elif item_kind == "Train" and self.training_queue:
                # Check queue count
                queue_count = sum(1 for q in self.training_queue if q == item_id)
                if queue_count > 0:
                    # Draw training progress shade for the active one
                    if self.training_queue[0] == item_id:
                        train_time = max(3, data["cost"] / 200)
                        pct = clamp(self.training_timer / train_time, 0, 1)
                        # Vertical wipe shade
                        wipe_h = round(card_h * (1.0 - pct))
                        if wipe_h > 0:
                            wipe_surf = pygame.Surface((card_w, wipe_h), pygame.SRCALPHA)
                            wipe_surf.fill((0, 0, 0, 150))
                            self.screen.blit(wipe_surf, (cx, cy))
                        # Display percentage
                        pct_lbl = self.small.render(f"{round(pct * 100)}%", True, (255, 255, 255))
                        pygame.draw.rect(self.screen, (12, 5, 20), (cx + card_w - 36, cy + 4, 30, 15), border_radius=2)
                        self.screen.blit(pct_lbl, pct_lbl.get_rect(center=(cx + card_w - 21, cy + 11)))
                    else:
                        # Draw HOLD queue indicator
                        hold_lbl = self.small.render(f"Q: {queue_count}", True, (215, 175, 120))
                        pygame.draw.rect(self.screen, (12, 5, 20), (cx + card_w - 36, cy + 4, 30, 15), border_radius=2)
                        self.screen.blit(hold_lbl, hold_lbl.get_rect(center=(cx + card_w - 21, cy + 11)))
                        
            # Store button for clicks
            self.buttons.append(Button(card_rect, data["name"], item_id, "build" if item_kind == "Build" else "train"))
            
        # Draw selected units info console (Yuri vector display)
        info_y = TOP_H + VIEW_H - 104
        pygame.draw.rect(self.screen, (12, 6, 20), (x + 16, info_y, SIDEBAR_W - 32, 82), border_radius=5)
        pygame.draw.rect(self.screen, (120, 45, 175), (x + 16, info_y, SIDEBAR_W - 32, 82), 1, border_radius=5)
        # Vector screen grid line highlights
        pygame.draw.line(self.screen, (40, 18, 55), (x + 16, info_y + 24), (x + SIDEBAR_W - 16, info_y + 24), 1)
        
        selected = self.selected()
        if selected:
            first = selected[0]
            name = STRUCT_DEFS[first.type]["name"] if first.kind == "structure" else UNIT_DEFS[first.type]["name"]
            lines = [
                f">> COMMAND: {name.upper()}",
                f">> INTEGRITY: {round(first.hp)} / {round(first.max_hp)} HP",
                f">> SECTOR CODES: LOCKED ({len(selected)} UNIT)"
            ]
        else:
            lines = [
                ">> COMMUNICATIONS ACTIVE",
                ">> AWAITING FIELD SELECTION",
                ">> USSR TACTICAL GRID LINKED"
            ]
        for i, line in enumerate(lines):
            surf = self.small.render(line, True, (245, 160, 40) if selected else (145, 210, 80)) # Amber if active, Green/Greenish if idle
            self.screen.blit(surf, (x + 24, info_y + 10 + i * 22))

    def draw_minimap(self, x, y):
        rect = pygame.Rect(x, y, MINIMAP_W, MINIMAP_H)
        pygame.draw.rect(self.screen, (8, 18, 16), rect)
        
        # Double gold & purple frames
        pygame.draw.rect(self.screen, (245, 185, 45), rect.inflate(4, 4), 2, border_radius=4)
        pygame.draw.rect(self.screen, (120, 45, 175), rect.inflate(8, 8), 2, border_radius=6)
        
        if self.map_surface:
            mini = pygame.transform.smoothscale(self.map_surface, (MINIMAP_W, MINIMAP_H))
            mini.set_alpha(125)
            self.screen.blit(mini, rect)
        for ore in self.ore:
            if ore.available:
                px = x + ore.x / WORLD_W * MINIMAP_W
                py = y + ore.y / WORLD_H * MINIMAP_H
                pygame.draw.circle(self.screen, (245, 195, 45), (round(px), round(py)), 2)
        for entity in self.entities:
            px = x + entity.center()[0] / WORLD_W * MINIMAP_W
            py = y + entity.center()[1] / WORLD_H * MINIMAP_H
            color = (245, 40, 35) if entity.team == TEAM_RED else (50, 130, 245)
            pygame.draw.circle(self.screen, color, (round(px), round(py)), 2 if entity.kind == "unit" else 3)
        half_w = VIEW_W / 2 / self.camera.zoom / WORLD_W * MINIMAP_W
        half_h = VIEW_H / 2 / self.camera.zoom / WORLD_H * MINIMAP_H
        cx = x + self.camera.x / WORLD_W * MINIMAP_W
        cy = y + self.camera.y / WORLD_H * MINIMAP_H
        pygame.draw.rect(self.screen, (245, 215, 90), (cx - half_w, cy - half_h, half_w * 2, half_h * 2), 1)

    def draw_bottombar(self):
        y = SCREEN_H - BOTTOM_H
        pygame.draw.rect(self.screen, (18, 16, 14), (0, y, SCREEN_W, BOTTOM_H))
        text = "Left drag: select   Right click: move/attack   Mouse wheel: zoom   Middle drag/arrows: pan   G: nav grid   Delete: sell"
        surf = self.small.render(text, True, (190, 170, 140))
        self.screen.blit(surf, (18, y + 9))
        queue = ", ".join(self.training_queue[:5]) if self.training_queue else "empty"
        qsurf = self.small.render(f"Queue: {queue}", True, (220, 180, 110))
        self.screen.blit(qsurf, (SCREEN_W - 360, y + 9))

    def draw_center_banner(self, title, subtitle):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 115))
        self.screen.blit(overlay, (0, 0))
        rect = pygame.Rect(0, 0, 430, 140)
        rect.center = (SCREEN_W // 2, SCREEN_H // 2)
        pygame.draw.rect(self.screen, (25, 18, 14), rect, border_radius=6)
        pygame.draw.rect(self.screen, (210, 55, 35), rect, 2, border_radius=6)
        title_s = self.big.render(title, True, (250, 70, 45))
        sub_s = self.font.render(subtitle, True, (230, 190, 135))
        self.screen.blit(title_s, title_s.get_rect(center=(rect.centerx, rect.y + 48)))
        self.screen.blit(sub_s, sub_s.get_rect(center=(rect.centerx, rect.y + 96)))

    def on_view(self, sx, sy, pad=0):
        return -pad <= sx <= VIEW_W + pad and TOP_H - pad <= sy <= TOP_H + VIEW_H + pad


def distance_xy(ax, ay, bx, by):
    return math.hypot(ax - bx, ay - by)


def entity_distance(a, b):
    ax, ay = a.center()
    bx, by = b.center()
    return distance_xy(ax, ay, bx, by)


def clamp(value, low, high):
    return max(low, min(high, value))


def main():
    pygame.init()
    pygame.display.set_caption("Red Alert Mini - Pygame")
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 18, bold=True)
    small = pygame.font.SysFont("arial", 14)
    big = pygame.font.SysFont("arial", 42, bold=True)
    game = Game(screen, clock, font, small, big)
    try:
        game.load_assets()
    except Exception as e:
        import traceback
        traceback.print_exc()
    try:
        game.load_sounds()
    except Exception as e:
        import traceback
        traceback.print_exc()

    while True:
        try:
            dt = clock.tick(60) / 1000
            for event in pygame.event.get():
                game.event(event)
            game.update(min(dt, 0.05))
            game.draw()
            pygame.display.flip()
        except Exception as e:
            import traceback
            traceback.print_exc()
            pygame.display.flip()


if __name__ == "__main__":
    main()
