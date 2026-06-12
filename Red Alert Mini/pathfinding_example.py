"""
Example usage of the navigation mask and pathfinding system.
Demonstrates how to integrate collision detection and pathfinding into your game.
"""

from pathfinding import initialize_pathfinder, find_path
from nav_mask import load_nav_mask, is_walkable
import os


def example_basic_usage():
    """Basic example: Initialize pathfinder and find a path."""
    print("=== Basic Pathfinding Example ===\n")
    
    # Initialize the pathfinder (loads nav_mask.pkl)
    pathfinder = initialize_pathfinder()
    
    # Example: Find path from (100, 100) to (1000, 500) in pixels
    start_pos = (100, 100)
    goal_pos = (1000, 500)
    
    print(f"Finding path from {start_pos} to {goal_pos}...")
    path = pathfinder.find_path(start_pos[0], start_pos[1], goal_pos[0], goal_pos[1])
    
    if path:
        print(f"Path found with {len(path)} waypoints!")
        print(f"First waypoint: {path[0]}")
        print(f"Last waypoint: {path[-1]}")
    else:
        print("No path found!")
    
    print()


def example_collision_check():
    """Example: Check if tiles are walkable."""
    print("=== Collision Detection Example ===\n")
    
    nav_mask = load_nav_mask("nav_mask.pkl")
    
    # Check some tile positions
    test_tiles = [
        (10, 10),
        (42, 23),
        (1, 1),
    ]
    
    for tx, ty in test_tiles:
        walkable = is_walkable(nav_mask, tx, ty)
        status = "✓ Walkable" if walkable else "✗ Blocked"
        print(f"Tile ({tx:2d}, {ty:2d}): {status}")
    
    print()


def example_unit_movement():
    """Example: Simulate unit movement along a path."""
    print("=== Unit Movement Simulation ===\n")
    
    pathfinder = initialize_pathfinder()
    
    # Unit starts at (200, 200) and needs to reach (1200, 700)
    start = (200.0, 200.0)
    goal = (1200.0, 700.0)
    
    path = pathfinder.find_path(start[0], start[1], goal[0], goal[1])
    
    if path:
        print(f"Generated path with {len(path)} waypoints")
        print(f"Total distance: ~{sum_path_distance(path):.0f} pixels")
        print(f"\nWaypoints (every 10th):")
        for i, waypoint in enumerate(path[::10]):
            print(f"  {i:2d}: ({waypoint[0]:7.1f}, {waypoint[1]:7.1f})")
    else:
        print("No valid path found!")
    
    print()


def example_nearest_walkable():
    """Example: Find nearest walkable point."""
    print("=== Finding Nearest Walkable Point ===\n")
    
    pathfinder = initialize_pathfinder()
    
    # Try to find walkable point near an obstacle
    target = (100.0, 100.0)
    nearest = pathfinder.get_nearest_walkable_point(target[0], target[1])
    
    if nearest:
        print(f"Target position: ({target[0]:.0f}, {target[1]:.0f})")
        print(f"Nearest walkable: ({nearest[0]:.0f}, {nearest[1]:.0f})")
        
        dist = ((nearest[0] - target[0])**2 + (nearest[1] - target[1])**2) ** 0.5
        print(f"Distance: {dist:.0f} pixels")
    
    print()


def sum_path_distance(path):
    """Calculate total distance of a path."""
    total = 0
    for i in range(1, len(path)):
        dx = path[i][0] - path[i-1][0]
        dy = path[i][1] - path[i-1][1]
        total += (dx*dx + dy*dy) ** 0.5
    return total


def integration_guide():
    """Print integration guide for using in main.py"""
    print("=== INTEGRATION GUIDE ===\n")
    print("""
To integrate pathfinding into your main.py:

1. At the top of main.py, add:
   from pathfinding import initialize_pathfinder, find_path, get_pathfinder
   from nav_mask import is_walkable

2. In your game initialization (before main loop):
   pathfinder = initialize_pathfinder()

3. For unit pathfinding, when you need a path:
   path = find_path(unit.x, unit.y, target.x, target.y)
   if path:
       unit.set_path(path)

4. To move units along the path each frame:
   if unit.path:
       # Move towards next waypoint
       next_wp = unit.path[unit.path_index]
       unit.move_towards(next_wp)

5. For collision avoidance with buildings:
   # Check if a tile is blocked
   blocked = get_pathfinder().is_tile_blocked(tile_x, tile_y)
   
   # Or check exact pixel location
   tx, ty = get_pathfinder().pixel_to_tile(px, py)
   if not is_walkable(nav_mask, tx, ty):
       # Can't go there

Navigation Mask Info:
- Binary array: 1 = blocked, 0 = walkable
- Tile size: 20 pixels
- Total dimensions: 85x47 tiles (1688x932 pixels)
- Blocked tiles: 83 (cliffs/obstacles)
- Walkable tiles: 3912 (green/sandy ground)
""")


if __name__ == "__main__":
    example_basic_usage()
    example_collision_check()
    example_unit_movement()
    example_nearest_walkable()
    integration_guide()
