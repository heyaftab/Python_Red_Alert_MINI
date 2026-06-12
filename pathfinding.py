"""
Pathfinding system using the navigation mask for collision detection.
Provides A* pathfinding algorithm for unit movement.
"""

import heapq
import math
from typing import List, Tuple, Optional
import os
from nav_mask import load_nav_mask, is_walkable, get_walkable_neighbors


class Pathfinder:
    """A* pathfinding using navigation mask for collision avoidance."""
    
    def __init__(self, nav_mask_path: str = "nav_mask.pkl", tile_size: int = 20):
        """
        Initialize the pathfinder.
        
        Args:
            nav_mask_path: Path to the pickled navigation mask
            tile_size: Size of each tile in pixels
        """
        self.tile_size = tile_size
        self.nav_mask = load_nav_mask(nav_mask_path)
        self.width = self.nav_mask.shape[1]
        self.height = self.nav_mask.shape[0]
        self.cache = {}  # Cache for recently computed paths
    
    def pixel_to_tile(self, px: float, py: float) -> Tuple[int, int]:
        """Convert pixel coordinates to tile coordinates."""
        tx = int(px // self.tile_size)
        ty = int(py // self.tile_size)
        return max(0, min(tx, self.width - 1)), max(0, min(ty, self.height - 1))
    
    def tile_to_pixel_center(self, tx: int, ty: int) -> Tuple[float, float]:
        """Convert tile coordinates to pixel center."""
        return (tx * self.tile_size + self.tile_size // 2,
                ty * self.tile_size + self.tile_size // 2)
    
    def heuristic(self, start: Tuple[int, int], goal: Tuple[int, int]) -> float:
        """Calculate heuristic distance (Euclidean)."""
        dx = abs(goal[0] - start[0])
        dy = abs(goal[1] - start[1])
        return math.sqrt(dx * dx + dy * dy)
    
    def find_path(self, start_px: float, start_py: float, 
                  goal_px: float, goal_py: float,
                  allow_diagonals: bool = True) -> Optional[List[Tuple[float, float]]]:
        """
        Find a path from start to goal using A* algorithm.
        
        Args:
            start_px, start_py: Starting pixel coordinates
            goal_px, goal_py: Goal pixel coordinates
            allow_diagonals: Whether to allow diagonal movement
        
        Returns:
            List of pixel coordinates representing the path, or None if no path exists
        """
        # Convert to tile coordinates
        start_tile = self.pixel_to_tile(start_px, start_py)
        goal_tile = self.pixel_to_tile(goal_px, goal_py)
        
        # Check if goal is walkable
        if not is_walkable(self.nav_mask, goal_tile[0], goal_tile[1]):
            return None
        
        # Check cache
        cache_key = (start_tile, goal_tile)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # A* algorithm
        open_set = []
        heapq.heappush(open_set, (0, start_tile))
        
        came_from = {}
        g_score = {start_tile: 0}
        f_score = {start_tile: self.heuristic(start_tile, goal_tile)}
        
        in_open = {start_tile}
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            in_open.discard(current)
            
            if current == goal_tile:
                # Reconstruct path
                path = []
                node = current
                while node in came_from:
                    path.append(self.tile_to_pixel_center(node[0], node[1]))
                    node = came_from[node]
                path.append(self.tile_to_pixel_center(start_tile[0], start_tile[1]))
                path.reverse()
                
                # Cache the result
                self.cache[cache_key] = path
                return path
            
            # Get neighbors (cardinal or with diagonals)
            if allow_diagonals:
                neighbors = self._get_all_neighbors(current[0], current[1])
            else:
                neighbors = get_walkable_neighbors(self.nav_mask, current[0], current[1], 
                                                   include_diagonals=False)
            
            for neighbor in neighbors:
                # Cost is higher for diagonals
                dx = neighbor[0] - current[0]
                dy = neighbor[1] - current[1]
                is_diagonal = dx != 0 and dy != 0
                tentative_g = g_score[current] + (math.sqrt(2) if is_diagonal else 1)
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + self.heuristic(neighbor, goal_tile)
                    f_score[neighbor] = f
                    
                    if neighbor not in in_open:
                        heapq.heappush(open_set, (f, neighbor))
                        in_open.add(neighbor)
        
        # No path found
        self.cache[cache_key] = None
        return None
    
    def _get_all_neighbors(self, tx: int, ty: int) -> List[Tuple[int, int]]:
        """Get all walkable neighbors including diagonals."""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = tx + dx, ty + dy
                if is_walkable(self.nav_mask, nx, ny):
                    # For diagonals, check that adjacent tiles are also walkable
                    if dx != 0 and dy != 0:
                        if is_walkable(self.nav_mask, tx + dx, ty) and \
                           is_walkable(self.nav_mask, tx, ty + dy):
                            neighbors.append((nx, ny))
                    else:
                        neighbors.append((nx, ny))
        return neighbors
    
    def clear_cache(self):
        """Clear the path cache."""
        self.cache.clear()
    
    def is_tile_blocked(self, tx: int, ty: int) -> bool:
        """Check if a tile is blocked."""
        return not is_walkable(self.nav_mask, tx, ty)
    
    def get_nearest_walkable_point(self, px: float, py: float, 
                                   search_radius: int = 5) -> Optional[Tuple[float, float]]:
        """
        Find the nearest walkable point to the given coordinates.
        
        Args:
            px, py: Target pixel coordinates
            search_radius: Search radius in tiles
        
        Returns:
            Nearest walkable pixel center, or None if none found
        """
        tx, ty = self.pixel_to_tile(px, py)
        
        if is_walkable(self.nav_mask, tx, ty):
            return self.tile_to_pixel_center(tx, ty)
        
        # Spiral search
        for radius in range(1, search_radius + 1):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if max(abs(dx), abs(dy)) != radius:
                        continue
                    nx, ny = tx + dx, ty + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if is_walkable(self.nav_mask, nx, ny):
                            return self.tile_to_pixel_center(nx, ny)
        
        return None


# Global pathfinder instance
_pathfinder: Optional[Pathfinder] = None


def initialize_pathfinder(nav_mask_path: str = "nav_mask.pkl", tile_size: int = 20) -> Pathfinder:
    """Initialize the global pathfinder instance."""
    global _pathfinder
    _pathfinder = Pathfinder(nav_mask_path, tile_size)
    return _pathfinder


def get_pathfinder() -> Optional[Pathfinder]:
    """Get the global pathfinder instance."""
    return _pathfinder


def find_path(start_px: float, start_py: float, 
              goal_px: float, goal_py: float) -> Optional[List[Tuple[float, float]]]:
    """Convenience function to find a path using the global pathfinder."""
    if _pathfinder is None:
        initialize_pathfinder()
    return _pathfinder.find_path(start_px, start_py, goal_px, goal_py)
