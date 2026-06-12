"""
Navigation mask generator for collision detection and pathfinding.
Analyzes the map image to create a binary collision map where:
- 1 = blocked (obstacles/cliffs)
- 0 = walkable (open ground)

The classification rules match main.py's is_blocked_pixel() exactly.
"""

import os
import numpy as np
from PIL import Image
import pickle


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")


def is_blocked_pixel(r, g, b):
    """Same 3 rules as main.py NavigationGrid.is_blocked_pixel()."""
    if r > 170 and g > 80 and g < 140 and b < 140 and (r - b) > 70 and (g - b) > 20:
        return True
    if r > 145 and g > 50 and g < 130 and b < 60 and (r - g) > 35:
        return True
    if r < 30 and g < 30 and b < 20:
        return True
    return False


def generate_nav_mask(map_image_path, tile_size=20):
    """
    Generate a binary navigation mask from the map image.

    Args:
        map_image_path: Path to the map image file
        tile_size: Size of tiles to group pixels into (for performance)

    Returns:
        nav_mask: 2D numpy array where 1=blocked, 0=walkable
        dimensions: (height, width) of the mask in tiles
    """

    if not os.path.exists(map_image_path):
        raise FileNotFoundError(f"Map image not found: {map_image_path}")

    img = Image.open(map_image_path).convert('RGBA')
    img_array = np.array(img)

    print(f"Map image loaded: {img.size} pixels")

    height, width = img_array.shape[0], img_array.shape[1]

    # Calculate mask dimensions (in tiles)
    mask_height = (height + tile_size - 1) // tile_size
    mask_width = (width + tile_size - 1) // tile_size

    print(f"Generating navigation mask: {mask_width}x{mask_height} tiles ({tile_size}px per tile)")

    # Create navigation mask
    nav_mask = np.zeros((mask_height, mask_width), dtype=np.uint8)

    # Process each tile using stride sampling (match main.py)
    stride = max(1, tile_size // 2)
    for ty in range(mask_height):
        for tx in range(mask_width):
            y_start = ty * tile_size
            x_start = tx * tile_size
            blocked_count = 0
            total = 0
            for dy in range(0, tile_size, stride):
                for dx in range(0, tile_size, stride):
                    wy = y_start + dy
                    wx = x_start + dx
                    if wx >= width or wy >= height:
                        continue
                    r, g, b, a = img_array[wy, wx]
                    if a < 128:
                        continue
                    total += 1
                    if is_blocked_pixel(int(r), int(g), int(b)):
                        blocked_count += 1
            if total > 0 and blocked_count / total > 0.50:
                nav_mask[ty, tx] = 1

    return nav_mask, (height, width)


def save_nav_mask(nav_mask, output_path):
    """Save the navigation mask to a pickle file."""
    with open(output_path, 'wb') as f:
        pickle.dump(nav_mask, f)
    print(f"Navigation mask saved to: {output_path}")


def load_nav_mask(input_path):
    """Load a saved navigation mask."""
    with open(input_path, 'rb') as f:
        nav_mask = pickle.load(f)
    return nav_mask


def is_walkable(nav_mask, tx, ty):
    """Check if a tile position is walkable."""
    if ty < 0 or ty >= nav_mask.shape[0] or tx < 0 or tx >= nav_mask.shape[1]:
        return False
    return nav_mask[ty, tx] == 0


def get_walkable_neighbors(nav_mask, tx, ty, include_diagonals=True):
    """Get all walkable neighboring tiles."""
    neighbors = []
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = tx + dx, ty + dy
        if is_walkable(nav_mask, nx, ny):
            neighbors.append((nx, ny))
    if include_diagonals:
        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = tx + dx, ty + dy
            if is_walkable(nav_mask, nx, ny):
                neighbors.append((nx, ny))
    return neighbors


def visualize_nav_mask(nav_mask, output_path=None):
    """Create a green/red visualization of the navigation mask."""
    vis_array = np.zeros((nav_mask.shape[0], nav_mask.shape[1], 3), dtype=np.uint8)
    vis_array[nav_mask == 0] = [0, 200, 0]
    vis_array[nav_mask == 1] = [200, 0, 0]
    vis_img = Image.fromarray(vis_array)
    if output_path:
        vis_img.save(output_path)
        print(f"Navigation mask visualization saved to: {output_path}")
    return vis_img


if __name__ == "__main__":
    map_path = os.path.join(ASSET_DIR, "Map.png")
    nav_mask_path = os.path.join(BASE_DIR, "nav_mask.pkl")
    vis_path = os.path.join(BASE_DIR, "nav_mask_vis.png")

    nav_mask, dimensions = generate_nav_mask(map_path, tile_size=20)

    print(f"Navigation mask dimensions: {nav_mask.shape}")
    print(f"Blocked tiles: {np.sum(nav_mask)}")
    print(f"Walkable tiles: {np.sum(nav_mask == 0)}")

    save_nav_mask(nav_mask, nav_mask_path)
    visualize_nav_mask(nav_mask, vis_path)

    print("\nNavigation mask generation complete!")
