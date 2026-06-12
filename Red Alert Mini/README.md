# Command & Conquer: Pygame Edition 🎮⚡

Welcome to **Command & Conquer: Pygame Edition**, a retro real-time strategy (RTS) game built using Python and Pygame. It recreates the gameplay, atmosphere, and mechanics of the classic Command & Conquer: Red Alert series, complete with base building, resource harvesting, unit production, combat, and nostalgic audio cues.

---

## 🚀 Purpose of the Game

The purpose of the game is to lead the **Soviet Faction (Team Red)** to victory against the **Allied Forces (Team Blue)**. As the Commander, you are responsible for:
1. **Establishing a Base**: Place critical structures such as [Power Plants](file:///Users/aftabuddinahmad/Desktop/pygame/main.py#L260), [Barracks](file:///Users/aftabuddinahmad/Desktop/pygame/main.py#L196), [War Factories](file:///Users/aftabuddinahmad/Desktop/pygame/main.py#L204), and defense grids like [Tesla Coils](file:///Users/aftabuddinahmad/Desktop/pygame/main.py#L233) or [Tesla Turrets](file:///Users/aftabuddinahmad/Desktop/pygame/main.py#L222).
2. **Managing Faction Resources & Energy**:
   - Deploy harvesters to mine gold ore fields and refinery nodes to earn **credits**.
   - Build sufficient [Power Plants](file:///Users/aftabuddinahmad/Desktop/pygame/main.py#L260) to maintain grid stability. Low power slows down base operations.
3. **Training & Mobilizing Armies**: Train infantry ([Conscripts](file:///Users/aftabuddinahmad/Desktop/pygame/main.py#L68), [War Dogs](file:///Users/aftabuddinahmad/Desktop/pygame/main.py#L81), [Tesla Troopers](file:///Users/aftabuddinahmad/Desktop/pygame/main.py#L94)) and armored divisions ([Rhino Tanks](file:///Users/aftabuddinahmad/Desktop/pygame/main.py#L107), [V3 Rockets](file:///Users/aftabuddinahmad/Desktop/pygame/main.py#L120), [Apocalypse Tanks](file:///Users/aftabuddinahmad/Desktop/pygame/main.py#L133)).
4. **Defeating the Enemy**: Fend off increasingly difficult waves of Allied invaders (such as [GIs](file:///Users/aftabuddinahmad/Desktop/pygame/main.py#L146), [Grizzly Tanks](file:///Users/aftabuddinahmad/Desktop/pygame/main.py#L159), and [Prism Tanks](file:///Users/aftabuddinahmad/Desktop/pygame/main.py#L172)) and eliminate their Construction Yard.

---

## ⚡ Why it is Better

This implementation stands out due to several high-performance features and nostalgic details:

1. **Intelligent Hybrid Pathfinding (A* & Navigation Mask)**
   - The game employs a pixel-color classification pipeline in [nav_mask.py](file:///Users/aftabuddinahmad/Desktop/pygame/nav_mask.py) using `Pillow` and `NumPy` to map walkability. It distinguishes green/sandy ground from orange/brown cliff walls.
   - It compiles high-resolution map assets (1688×932) into a highly compact **4KB binary collision grid** ([nav_mask.pkl](file:///Users/aftabuddinahmad/Desktop/pygame/nav_mask.pkl)).
   - The custom [Pathfinder](file:///Users/aftabuddinahmad/Desktop/pygame/pathfinding.py#L13) class implements the **A* pathfinding algorithm** with diagonal checks and a path cache, guaranteeing smooth paths under 2ms.
2. **Dynamic Obstacle Registration**
   - Obstacles aren't just static cliffs. When you or the AI place structures on the battlefield, the pathfinder dynamically updates the tile walkability matrix. Units will intelligently detour around buildings in real-time.
3. **Immersive Retro Sound Design & Voice Acting**
   - The game features authentic Command & Conquer voice feedback, including selections like *"Yes, Commander"*, *"Moving out"*, *"Affirmative"*, and warning prompts such as *"Our base is in danger"*.
   - Includes a looping retro synth soundtrack for the menus and battlefields.
4. **Advanced RTS UI**
   - **Tactical Viewport Controls**: Zoom in/out (mouse wheel or `+`/`-`) and pan manually (middle mouse drag or Arrow/IJKL keys).
   - **Edge Scrolling**: Drag your mouse cursor to the borders or corners of the window to automatically scroll the map in that direction.
   - **Yuri's Revenge themed Sidebar**:
     - **Category Tabs**: Switch between Buildings (`BLDG`), Defenses (`DEFN`), Infantry (`INF`), and Vehicles (`VEH`).
     - **Segmented Power Bar**: Segmented vertical power indicator showing current power output vs consumption ratio in red/yellow/green.
     - **Interactive Minimap**: Beveled gold-framed radar map displaying units, buildings, camera viewports, and ore fields.
     - **Graphic Cards Grid**: 2-column cards showing item sprites, hotkey indexes, costs, queued counts, and vertical training sweeps.
     - **Amber Vector Console**: Futuristic screen displaying HP, selection quantities, and grid connectivity status.
   - **Classic Selection**: Left-click drag selection box and Shift-click grouping.
5. **Robust Simulation Depth**
   - Full implementation of unit attributes (HP, Range, Attack Speed, Fire Rate, Sight Range, Base Costs).
   - Tesla Coils and Tesla Turrets automatically target and blast enemies that breach their range.
   - Dynamic fire particle effects and damage labels float above combat sites.

---

## 🛠️ Required Dependencies

To run the game, you need **Python 3.8+** installed along with these libraries:

* **`pygame`** - Core engine for screen rendering, event/input loops, audio channels, and game loops.
* **`numpy`** - Fast multi-dimensional array operations used for processing collision maps.
* **`pillow` (PIL)** - Image reading, thresholding, and generating obstacle masks.

### Installation Command
Run the following in your terminal:
```bash
pip install pygame numpy pillow
```

---

## 🎮 How to Run

Follow these instructions to start the game:

### 1. (Optional) Regenerate the Navigation Map
If you change the map graphics (`assets/Map.png`), you can rebuild the collision grid using:
```bash
python3 nav_mask.py
```
This updates the binary collision file ([nav_mask.pkl](file:///Users/aftabuddinahmad/Desktop/pygame/nav_mask.pkl)) and creates a green/red walkability layout ([nav_mask_vis.png](file:///Users/aftabuddinahmad/Desktop/pygame/nav_mask_vis.png)).

### 2. Start the Main Game
Run the game using the main entry script:
```bash
python3 main.py
```

### 3. Run Pathfinding Diagnostics & Demos
To check pathfinding statistics, run the debug utilities:
- **Pathfinding Example**: `python3 pathfinding_example.py` (simulates pathing conversions, caching efficiency, and coordinates)
- **Pathfinding Debug**: `python3 pathfinding_debug.py` (benchmarks A* performance and maps terrain walkability statistics)

---

## ⌨️ Tactical Controls Reference

### 🖥️ Main Menu Controls
* **`1`** — Start Game (Easy Difficulty)
* **`2`** — Start Game (Medium Difficulty)
* **`3`** — Start Game (Hard Difficulty)

### 🖱️ Mouse Controls
* **Left-Click & Drag** — Selection box for grouping multiple units.
* **Shift + Left-Click** — Add or remove units to/from the current selection.
* **Left-Click (with Structure Active)** — Place selected building on the map.
* **Right-Click** — Command selected units to move to a destination, harvest ore, or attack an enemy unit/structure.
* **Middle-Click & Drag** — Pan the camera manually.
* **Scroll Wheel Up / Down** — Zoom the camera in and out.
* **Edge Hover** — Hover cursor within 20px of any window edge to scroll the map in that direction.

### ⌨️ Hotkeys & Shortcuts
* **`Escape`** — Cancel structure placement / Deselect / Unpause.
* **`P`** — Pause / Resume the game.
* **`G`** — Toggle the pathfinding navigation grid overlay (Debug).
* **`Delete`** — Sell selected units or structures (50% refund on buildings).
* **`+` or `=`** — Zoom In.
* **`-`** — Zoom Out.
* **`R`** — Return to the Main Menu (available on the Game Over / Victory screen).

### 🏗️ Base Construction Keys (Build Grid)
* **`1`** — **Power Plant** ($500) — Generates energy.
* **`2`** — **Barracks** ($300) — Allows training infantry.
* **`3`** — **War Factory** ($2000) — Allows manufacturing vehicles.
* **`4`** — **Ore Refinery** ($2000) — Enables harvesters to gather credits.
* **`5`** — **Tesla Turret** ($600) — Standard base defense.
* **`6`** — **Tesla Coil** ($1500) — Advanced high-damage base defense.
* **`7`** — **Radar Dome** ($1000) — Displays minimap features.
* **`8`** — **Wall** ($100) — Blockades enemy units.

### 💂 Unit Production Keys (Train Grid)
* **`Q`** — **Conscript** ($100) — Cheap basic infantry.
* **`W`** — **War Dog** ($200) — Fast scout infantry, excellent against other infantry.
* **`E`** — **Tesla Trooper** ($500) — Heavy shock trooper.
* **`A`** — **Rhino Tank** ($900) — Standard battle tank.
* **`S`** — **V3 Rocket Launcher** ($1200) — Long-range artillery vehicle.
* **`D`** — **Apocalypse Tank** ($2000) — Heavy-duty dual-cannon armored vehicle.

---

## 📂 Codebase File Layout

* 📄 [main.py](file:///Users/aftabuddinahmad/Desktop/pygame/main.py) — Core game logic, faction settings, entity managers, rendering pipeline, inputs, and UI.
* 📄 [nav_mask.py](file:///Users/aftabuddinahmad/Desktop/pygame/nav_mask.py) — Parses RGB values from the battlefield image to determine where units can walk.
* 📄 [pathfinding.py](file:///Users/aftabuddinahmad/Desktop/pygame/pathfinding.py) — Custom A* path solver incorporating pixel-to-tile translations and path caching.
* 📄 [NAVIGATION_SYSTEM.md](file:///Users/aftabuddinahmad/Desktop/pygame/NAVIGATION_SYSTEM.md) — Comprehensive API reference for the pathfinder logic.
* 📄 [QUICK_START_NAVIGATION.md](file:///Users/aftabuddinahmad/Desktop/pygame/QUICK_START_NAVIGATION.md) — Brief developer setup guide for pathfinder integration.
* 📁 `assets/` — Graphical files, sprites, UI elements, and map background (`Map.png`).
* 📁 `Sounds/` — Action voice bytes, alarms, feedback prompts, and soundtrack tracks.
