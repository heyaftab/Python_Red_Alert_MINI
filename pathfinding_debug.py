"""
Debugging and visualization utilities for the navigation system.
Useful for visualizing pathfinding results and collision detection during development.
"""

import pygame
import numpy as np
from pathfinding import get_pathfinder
from nav_mask import load_nav_mask
from typing import Optional, List, Tuple


class PathfindingDebugger:
    """Visualize pathfinding and collision detection in pygame."""
    
    def __init__(self, screen_width: int, screen_height: int, 
                 nav_mask_path: str = "nav_mask.pkl", tile_size: int = 20):
        """
        Initialize the debugger.
        
        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            nav_mask_path: Path to navigation mask
            tile_size: Tile size in pixels
        """
        self.tile_size = tile_size
        self.nav_mask = load_nav_mask(nav_mask_path)
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Visualization states
        self.show_grid = False
        self.show_blocked_tiles = False
        self.show_current_path = False
        self.current_path: Optional[List[Tuple[float, float]]] = None
        self.path_start: Optional[Tuple[float, float]] = None
        self.path_goal: Optional[Tuple[float, float]] = None
    
    def toggle_grid(self):
        """Toggle grid visibility."""
        self.show_grid = not self.show_grid
    
    def toggle_blocked_tiles(self):
        """Toggle blocked tiles visibility."""
        self.show_blocked_tiles = not self.show_blocked_tiles
    
    def set_path(self, start: Tuple[float, float], goal: Tuple[float, float]):
        """
        Compute and set path for visualization.
        
        Args:
            start: Starting position (x, y)
            goal: Goal position (x, y)
        """
        pathfinder = get_pathfinder()
        if pathfinder:
            self.current_path = pathfinder.find_path(start[0], start[1], goal[0], goal[1])
            self.path_start = start
            self.path_goal = goal
            self.show_current_path = True
    
    def draw_debug_overlay(self, surface: pygame.Surface, 
                          camera_x: float = 0, camera_y: float = 0):
        """
        Draw debug overlay on the surface.
        
        Args:
            surface: Pygame surface to draw on
            camera_x, camera_y: Camera offset (for viewport translation)
        """
        if self.show_grid:
            self._draw_grid(surface, camera_x, camera_y)
        
        if self.show_blocked_tiles:
            self._draw_blocked_tiles(surface, camera_x, camera_y)
        
        if self.show_current_path and self.current_path:
            self._draw_path(surface, self.current_path, camera_x, camera_y)
        
        # Draw path start and goal markers
        if self.path_start:
            self._draw_marker(surface, self.path_start, (0, 255, 0), 
                            camera_x, camera_y, label="Start")
        if self.path_goal:
            self._draw_marker(surface, self.path_goal, (255, 0, 0), 
                            camera_x, camera_y, label="Goal")
    
    def _draw_grid(self, surface: pygame.Surface, camera_x: float, camera_y: float):
        """Draw collision grid overlay."""
        color = (100, 100, 100, 50)  # Semi-transparent gray
        
        # Draw vertical lines
        for tx in range(self.nav_mask.shape[1] + 1):
            x = tx * self.tile_size - camera_x
            if -10 < x < self.screen_width + 10:
                pygame.draw.line(surface, color, (x, 0), (x, self.screen_height), 1)
        
        # Draw horizontal lines
        for ty in range(self.nav_mask.shape[0] + 1):
            y = ty * self.tile_size - camera_y
            if -10 < y < self.screen_height + 10:
                pygame.draw.line(surface, color, (0, y), (self.screen_width, y), 1)
    
    def _draw_blocked_tiles(self, surface: pygame.Surface, 
                           camera_x: float, camera_y: float):
        """Draw blocked tiles as semi-transparent red rectangles."""
        color = (255, 0, 0, 100)  # Semi-transparent red
        
        for ty in range(self.nav_mask.shape[0]):
            for tx in range(self.nav_mask.shape[1]):
                if self.nav_mask[ty, tx] == 1:  # Blocked
                    x = tx * self.tile_size - camera_x
                    y = ty * self.tile_size - camera_y
                    
                    # Only draw if visible on screen
                    if -self.tile_size < x < self.screen_width + self.tile_size and \
                       -self.tile_size < y < self.screen_height + self.tile_size:
                        pygame.draw.rect(surface, color, 
                                        (x, y, self.tile_size, self.tile_size))
    
    def _draw_path(self, surface: pygame.Surface, path: List[Tuple[float, float]],
                   camera_x: float, camera_y: float):
        """Draw the computed path as connected line."""
        if len(path) < 2:
            return
        
        # Convert path points to screen coordinates
        screen_points = []
        for px, py in path:
            sx = px - camera_x
            sy = py - camera_y
            if -50 < sx < self.screen_width + 50 and \
               -50 < sy < self.screen_height + 50:
                screen_points.append((sx, sy))
        
        # Draw path as line
        if len(screen_points) > 1:
            pygame.draw.lines(surface, (0, 255, 255), screen_points, 2)
        
        # Draw waypoint markers
        for i, (sx, sy) in enumerate(screen_points):
            color = (100, 255, 100) if i % 2 == 0 else (100, 200, 255)
            pygame.draw.circle(surface, color, (int(sx), int(sy)), 3)
    
    def _draw_marker(self, surface: pygame.Surface, pos: Tuple[float, float],
                    color: Tuple[int, int, int], camera_x: float, camera_y: float,
                    label: str = ""):
        """Draw a position marker."""
        sx = int(pos[0] - camera_x)
        sy = int(pos[1] - camera_y)
        
        if -20 < sx < self.screen_width + 20 and \
           -20 < sy < self.screen_height + 20:
            # Draw circle
            pygame.draw.circle(surface, color, (sx, sy), 8, 2)
            # Draw cross
            pygame.draw.line(surface, color, (sx - 5, sy), (sx + 5, sy), 2)
            pygame.draw.line(surface, color, (sx, sy - 5), (sx, sy + 5), 2)
    
    def get_debug_info(self) -> str:
        """Get debug information string."""
        info = []
        info.append("=== Navigation Debug Info ===")
        info.append(f"Grid: {self.show_grid and 'ON' or 'OFF'}")
        info.append(f"Blocked Tiles: {self.show_blocked_tiles and 'ON' or 'OFF'}")
        info.append(f"Path Display: {self.show_current_path and 'ON' or 'OFF'}")
        
        if self.current_path:
            info.append(f"Current Path: {len(self.current_path)} waypoints")
            
            if self.path_start and self.path_goal:
                dist = sum(
                    ((self.current_path[i][0] - self.current_path[i-1][0])**2 +
                     (self.current_path[i][1] - self.current_path[i-1][1])**2)**0.5
                    for i in range(1, len(self.current_path))
                )
                info.append(f"Path Length: {dist:.0f} pixels")
        
        return "\n".join(info)


def print_navigation_stats():
    """Print statistics about the navigation mask."""
    nav_mask = load_nav_mask("nav_mask.pkl")
    
    total_tiles = nav_mask.shape[0] * nav_mask.shape[1]
    blocked_tiles = np.sum(nav_mask)
    walkable_tiles = total_tiles - blocked_tiles
    
    print("=== Navigation Mask Statistics ===")
    print(f"Grid dimensions: {nav_mask.shape[1]} x {nav_mask.shape[0]} tiles")
    print(f"Total tiles: {total_tiles}")
    print(f"Blocked tiles: {blocked_tiles} ({100 * blocked_tiles / total_tiles:.1f}%)")
    print(f"Walkable tiles: {walkable_tiles} ({100 * walkable_tiles / total_tiles:.1f}%)")
    print(f"Tile size: 20 pixels")
    print(f"Total map: 1688 x 932 pixels")


def create_collision_test_image(output_path: str = "collision_test.png"):
    """
    Create a test image showing the collision map overlaid on the original.
    Useful for verifying collision detection accuracy.
    """
    from PIL import Image
    
    # Load original map
    orig_img = Image.open("assets/Map.png").convert('RGB')
    orig_array = np.array(orig_img)
    
    # Load navigation mask
    nav_mask = load_nav_mask("nav_mask.pkl")
    
    # Create overlay
    overlay = orig_array.copy()
    
    # Color blocked tiles with red overlay
    for ty in range(nav_mask.shape[0]):
        for tx in range(nav_mask.shape[1]):
            if nav_mask[ty, tx] == 1:  # Blocked
                # Map tile coordinates to pixel range
                y_start = ty * 20
                y_end = min((ty + 1) * 20, overlay.shape[0])
                x_start = tx * 20
                x_end = min((tx + 1) * 20, overlay.shape[1])
                
                # Apply red tint
                overlay[y_start:y_end, x_start:x_end] = np.clip(
                    overlay[y_start:y_end, x_start:x_end].astype(np.float32) * 0.5 +
                    np.array([200, 0, 0]) * 0.5,
                    0, 255
                ).astype(np.uint8)
    
    # Save result
    result_img = Image.fromarray(overlay)
    result_img.save(output_path)
    print(f"Collision test image saved to: {output_path}")


if __name__ == "__main__":
    print_navigation_stats()
    print("\nGenerating collision test image...")
    create_collision_test_image()
