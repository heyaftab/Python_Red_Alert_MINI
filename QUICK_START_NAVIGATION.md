# Navigation Mask System - Quick Start Guide

## What Was Created

Your game now has a complete navigation and collision detection system:

### Core Files

- **`nav_mask.py`** - Generates collision map from map image (6.7K)
- **`pathfinding.py`** - A* pathfinding algorithm (7.8K)
- **`nav_mask.pkl`** - Binary collision map data (4.1K)
- **`nav_mask_vis.png`** - Visual representation of collision map

### Utilities & Documentation

- **`pathfinding.py`** - Pathfinding API for unit movement
- **`pathfinding_debug.py`** - Debug visualization tools (9.4K)
- **`pathfinding_example.py`** - Usage examples and integration code
- **`collision_test.png`** - Collision map overlaid on original map
- **`NAVIGATION_SYSTEM.md`** - Comprehensive documentation (6.1K)

## Quick Integration

### 1. Add to top of main.py

```python
from pathfinding import initialize_pathfinder, find_path, get_pathfinder
```


### 2. In game initialization

```python
pathfinder = initialize_pathfinder()
```


### 3. For unit pathfinding

```python
# When unit needs to move to a target
path = find_path(unit.x, unit.y, target_x, target_y)
if path:
    unit.set_path(path)
    unit.path_index = 0
```


### 4. Update unit position each frame

```python
if unit.path and unit.path_index < len(unit.path):
    next_waypoint = unit.path[unit.path_index]
    
    # Move towards waypoint
    dx = next_waypoint[0] - unit.x
    dy = next_waypoint[1] - unit.y
    distance = (dx**2 + dy**2) ** 0.5
    
    if distance < unit.speed * dt:
        unit.path_index += 1  # Move to next waypoint
    else:
        # Normalize and move
        unit.x += (dx / distance) * unit.speed * dt
        unit.y += (dy / distance) * unit.speed * dt
```


## Key Numbers

- **Map size**: 1688×932 pixels
- **Tile grid**: 85×47 tiles (20 pixels per tile)
- **Blocked tiles**: 83 (2.1%) - orange/brown cliffs
- **Walkable tiles**: 3912 (97.9%) - green and sandy ground
- **Collision map size**: Only 4.1K!

## What Gets Detected

✓ **Orange/Brown cliffs** → Blocked (can't walk)
✓ **Green grass** → Walkable
✓ **Sandy/tan ground** → Walkable
✗ **Buildings** → Use separate collision system (not in map analysis)

## Files Generated

1. **`nav_mask.pkl`** - Binary collision data for pathfinding
2. **`nav_mask_vis.png`** - Green (walkable) + Red (blocked) visualization
3. **`collision_test.png`** - Original map with red overlay on blocked areas

## Debugging & Testing

### Check statistics

```bash
python3 pathfinding_debug.py
```


### View collision map

Open `nav_mask_vis.png` or `collision_test.png` to verify terrain detection

### Test pathfinding

```bash
python3 pathfinding_example.py
```


## API Cheat Sheet

```python
from pathfinding import initialize_pathfinder, find_path, get_pathfinder
from nav_mask import is_walkable, load_nav_mask

# Initialize
pf = initialize_pathfinder()

# Find paths
path = find_path(x1, y1, x2, y2)  # Returns list of (x,y) waypoints or None

# Coordinate conversion
tx, ty = pf.pixel_to_tile(px, py)
px, py = pf.tile_to_pixel_center(tx, ty)

# Collision checking
blocked = pf.is_tile_blocked(tx, ty)
valid_pos = pf.get_nearest_walkable_point(x, y)

# Direct mask access
nav_mask = load_nav_mask("nav_mask.pkl")
walkable = is_walkable(nav_mask, tx, ty)
```


## Troubleshooting

**Units get stuck in terrain**

- Ensure pathfinding is initialized before units move
- Check that nav_mask.pkl exists and is valid
- Verify tile coordinates are within bounds (0-84 for x, 0-46 for y)

**No path found**

- Check destination is walkable: `is_walkable(nav_mask, goal_tx, goal_ty)`
- Use `get_nearest_walkable_point()` to find valid destination
- Ensure start and goal aren't in isolated regions

**Wrong obstacles detected**

- Modify color thresholds in `nav_mask.py` function `get_color_category()`
- Regenerate with: `python3 nav_mask.py`

## Performance

- Pathfinding: ~0.5-2ms for typical paths
- Cached paths: <0.1ms (instant)
- Memory: 4.1KB for entire map
- Grid: 85×47 tiles is very fast

## Next Steps

1. Copy integration code into your `main.py`
2. Test with `python3 pathfinding_example.py`
3. Use `NAVIGATION_SYSTEM.md` for full API reference
4. Debug with `pathfinding_debug.py` if needed

That's it! Your units now have intelligent pathfinding avoiding all terrain obstacles.
