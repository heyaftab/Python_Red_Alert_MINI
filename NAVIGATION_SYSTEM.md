# Navigation Mask & Pathfinding System

## Overview

This system provides automatic collision detection and A* pathfinding for your game. It analyzes the map image to detect obstacles (orange/brown cliffs) and generates a binary collision map for efficient pathfinding.

## Files

- **`nav_mask.py`** - Navigation mask generator (analyzes map image)
- **`pathfinding.py`** - A* pathfinding algorithm with collision detection
- **`pathfinding_example.py`** - Usage examples and integration guide
- **`nav_mask.pkl`** - Generated binary collision map (pickled)
- **`nav_mask_vis.png`** - Visual representation of the collision map

## How It Works

### 1. Map Analysis (`nav_mask.py`)

The script analyzes `assets/Map.png` and classifies pixels:

- **Orange/Brown Pixels** → Blocked terrain (cliffs, walls)
- **Green Pixels** → Walkable ground
- **Sandy/Tan Pixels** → Walkable ground
- **Other Colors** → Unknown (treated conservatively)

### 2. Collision Map Generation

The map is divided into 20×20 pixel tiles. Each tile is marked as:
- **1** = Blocked (>30% obstacle pixels)
- **0** = Walkable (>70% open ground)

**Map Statistics:**
- Map size: 1688×932 pixels
- Tile grid: 85×47 tiles (20px per tile)
- Blocked tiles: 83
- Walkable tiles: 3912

### 3. Pathfinding Algorithm

The `Pathfinder` class implements **A* pathfinding**:
- Finds optimal paths avoiding obstacles
- Supports diagonal movement (with validation)
- Caches recently computed paths for performance
- Handles unreachable destinations gracefully

## Integration into main.py

### Basic Setup

```python
from pathfinding import initialize_pathfinder, find_path
from nav_mask import is_walkable

# In game initialization:
pathfinder = initialize_pathfinder()
```

### Finding Paths for Units

```python
# When a unit needs to move:
path = find_path(unit.x, unit.y, target_x, target_y)

if path:
    unit.set_path(path)  # Path is list of (x, y) tuples
    unit.path_index = 0
else:
    print("No path available!")
```

### Moving Units Along Path

```python
def update_unit(unit, dt):
    if unit.path and unit.path_index < len(unit.path):
        waypoint = unit.path[unit.path_index]
        
        # Move towards waypoint
        dx = waypoint[0] - unit.x
        dy = waypoint[1] - unit.y
        dist = (dx**2 + dy**2) ** 0.5
        
        if dist < unit.speed * dt:
            # Reached waypoint, move to next
            unit.path_index += 1
        else:
            # Move towards waypoint
            unit.x += (dx / dist) * unit.speed * dt
            unit.y += (dy / dist) * unit.speed * dt
```

### Collision Checking

```python
from pathfinding import get_pathfinder

pathfinder = get_pathfinder()

# Check if a tile is blocked
if pathfinder.is_tile_blocked(tile_x, tile_y):
    print("Can't build here!")

# Find nearest valid position
valid_pos = pathfinder.get_nearest_walkable_point(x, y)
if valid_pos:
    print(f"Move to: {valid_pos}")
```

## API Reference

### Pathfinder Class

```python
pathfinder = Pathfinder(nav_mask_path="nav_mask.pkl", tile_size=20)

# Find a path
path = pathfinder.find_path(start_x, start_y, goal_x, goal_y, allow_diagonals=True)

# Convert between pixel and tile coordinates
tile_x, tile_y = pathfinder.pixel_to_tile(pixel_x, pixel_y)
pixel_x, pixel_y = pathfinder.tile_to_pixel_center(tile_x, tile_y)

# Check walkability
if not pathfinder.is_tile_blocked(tile_x, tile_y):
    print("Walkable!")

# Find nearest walkable point (useful for invalid destinations)
valid_pos = pathfinder.get_nearest_walkable_point(x, y, search_radius=5)

# Clear cached paths
pathfinder.clear_cache()
```

### Convenience Functions

```python
from pathfinding import initialize_pathfinder, find_path, get_pathfinder

# Initialize global pathfinder
pathfinder = initialize_pathfinder()

# Use global pathfinder
path = find_path(start_x, start_y, goal_x, goal_y)

# Get the global instance
pf = get_pathfinder()
```

### Navigation Mask Functions

```python
from nav_mask import load_nav_mask, is_walkable, get_walkable_neighbors, save_nav_mask

# Load the collision map
nav_mask = load_nav_mask("nav_mask.pkl")

# Check if a tile is walkable
if is_walkable(nav_mask, tile_x, tile_y):
    print("Can walk here")

# Get adjacent walkable tiles
neighbors = get_walkable_neighbors(nav_mask, tile_x, tile_y, include_diagonals=True)
```

## Color Detection Thresholds

The system detects terrain types using RGB color thresholds:

- **Orange/Brown (Obstacles)**
  - R > 150, G < 150, B < 100
  - R > G and R > B

- **Green (Walkable)**
  - G > 100, R < 150, B < 120
  - G > R and G > B

- **Sandy/Tan (Walkable)**
  - R > 150, G > 120, B < 100
  - Adjusted R-G difference and G > B

To adjust detection, modify the `get_color_category()` function in `nav_mask.py` and regenerate the mask.

## Performance Considerations

- **Path caching**: Recently computed paths are cached to avoid recomputation
- **Tile size**: Larger tiles = faster pathfinding but less precision (currently 20px)
- **Grid size**: 85×47 tiles is reasonable for typical queries
- **Memory**: Navigation mask is ~4KB (47×85 bytes)

## Troubleshooting

### No path found

- Verify the destination is walkable: `is_walkable(nav_mask, goal_tx, goal_ty)`
- Try `get_nearest_walkable_point()` to find a valid destination
- Check if start and goal are on different isolated regions

### Units stuck in obstacles

- Ensure buildings are added to the collision map or handled separately
- Verify pathfinding initialization: `pathfinder = initialize_pathfinder()`
- Check tile coordinates are within bounds: `0 ≤ tx < 85`, `0 ≤ ty < 47`

### Performance issues

- Clear cache periodically: `pathfinder.clear_cache()`
- Consider pre-computing paths during idle time
- Use shorter search paths or waypoint networks for large distances

## Regenerating the Navigation Mask

If you modify the map image, regenerate the collision map:

```bash
python3 nav_mask.py
```

This will create:
- `nav_mask.pkl` - Updated collision map
- `nav_mask_vis.png` - Updated visualization

## Visualization

The `nav_mask_vis.png` file shows:
- **Green areas** = Walkable terrain (open ground)
- **Red areas** = Blocked terrain (cliffs/obstacles)

Use this to verify the collision detection is working correctly.
