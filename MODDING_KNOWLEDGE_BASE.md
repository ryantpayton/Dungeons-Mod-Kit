# Minecraft Dungeons Modding Knowledge Base

> **Last Updated:** January 17, 2026  
> **Purpose:** Complete documentation of Minecraft Dungeons modding techniques, tools, and discoveries.  
> **AI Context:** This document serves as a knowledge transfer for AI assistants to continue modding work without prior chat history.

---

## Table of Contents

1. [Game Overview](#game-overview)
2. [File Structure](#file-structure)
3. [Tools Reference](#tools-reference)
4. [PAK File Creation](#pak-file-creation)
5. [JSON Modding](#json-modding)
6. [Binary Asset Modding (UAsset/UExp)](#binary-asset-modding-uassetuexp)
7. [Camera Rotation Mod](#camera-rotation-mod)
8. [Night Mode / Ambience Mod](#night-mode--ambience-mod)
9. [Common Pitfalls & Solutions](#common-pitfalls--solutions)
10. [File Locations Quick Reference](#file-locations-quick-reference)
11. [Mod Installation](#mod-installation)
12. [Future Research Areas](#future-research-areas)

---

## Game Overview

- **Game:** Minecraft Dungeons
- **Engine:** Unreal Engine 4.22
- **Platform:** Windows (Steam version)
- **Game Location:** `E:\SteamLibrary\steamapps\common\MinecraftDungeons`
- **Mod Folder:** `E:\SteamLibrary\steamapps\common\MinecraftDungeons\Dungeons\Content\Paks\~mods\`

### Key Points

- Mods are loaded from the `~mods` folder (the `~` prefix ensures it loads after base game paks)
- PAK files are Unreal Engine 4 package files
- Game uses both JSON data files and binary UAsset/UExp files
- JSON files can be modified with any text editor
- Binary files require specialized tools (UAssetGUI)

---

## File Structure

### Workspace Structure

```
D:\Desktop\repos\Git\Dungeons-Mod-Kit\
├── quickbms/
│   └── BmsExport/
│       └── Dungeons/
│           └── Content/           # Extracted game files (reference)
│               ├── Actors/
│               │   └── Characters/
│               │       └── Player/
│               │           ├── BP_PlayerCharacter.uasset
│               │           └── BP_PlayerCharacter.uexp
│               └── data/
│                   └── levels/
│                       └── lobby/
│                           └── lobby.json
├── ModBuild/
│   └── Night/                     # Final mod paks
│       ├── CameraRotate.pak       # Camera only
│       ├── CrimsonForest90.pak    # Camera + ambience
│       ├── Enderwilds90.pak
│       ├── NetherWastes90.pak
│       ├── ObsidianPinnacle90.pak
│       └── SoulSandValley90.pak
├── Tools/
│   ├── py/
│   │   └── u4pak.py               # PAK creation tool
│   └── UAssetGUI.exe              # Binary asset editor
└── UE4Project/                    # Unreal Editor project
```

### Game PAK Structure

Inside game paks, files follow this structure:

```
Dungeons/
└── Content/
    ├── Actors/          # Game objects, characters, etc.
    ├── data/            # JSON configuration files
    │   ├── levels/      # Level definitions
    │   ├── items/       # Item data
    │   └── ...
    ├── Localization/    # Language files
    └── UI/              # User interface assets
```

---

## Tools Reference

### u4pak.py

**Location:** `D:\Desktop\repos\Git\Dungeons-Mod-Kit\Tools\py\u4pak.py`  
**Purpose:** Create and extract PAK files for Unreal Engine 4

#### Commands

**List PAK contents:**

```powershell
python D:\Desktop\repos\Git\Dungeons-Mod-Kit\Tools\py\u4pak.py list "path\to\file.pak"
```

**Extract PAK file:**

```powershell
python D:\Desktop\repos\Git\Dungeons-Mod-Kit\Tools\py\u4pak.py unpack "path\to\file.pak" "output\folder"
```

**Create PAK file:**

```powershell
python D:\Desktop\repos\Git\Dungeons-Mod-Kit\Tools\py\u4pak.py pack "output.pak" "Dungeons"
```

> **CRITICAL:** The folder structure passed to `pack` must start with `Dungeons/Content/...` to match game paths!

### UAssetGUI

**Location:** `D:\Desktop\repos\Git\Dungeons-Mod-Kit\Tools\UAssetGUI.exe`  
**Version:** 1.0.3  
**Purpose:** Edit binary UAsset/UExp files with proper serialization

#### Usage

1. Open UAssetGUI.exe
2. Set Unreal version to **4.22** (File → Set Serialization Version)
3. Open the .uasset file (it auto-loads the .uexp)
4. Navigate to the export you want to edit
5. Make changes
6. Save (File → Save)

> **IMPORTANT:** Always use UAssetGUI for binary files! Manual hex editing causes "Serialization Error: Corrupt data" crashes.

### QuickBMS

**Location:** `D:\Desktop\repos\Git\Dungeons-Mod-Kit\quickbms\`  
**Purpose:** Extract game PAK files using dungeons.bms script

Already extracted files are in: `quickbms\BmsExport\Dungeons\Content\`

---

## PAK File Creation

### Step-by-Step Process

1. **Create folder structure matching game paths:**

   ```
   YourMod/
   └── Dungeons/
       └── Content/
           └── [path to files you're modifying]
   ```

2. **Copy and modify files:**
   - For JSON: Copy from `quickbms\BmsExport\`, edit with text editor
   - For UAsset/UExp: Copy both files, edit with UAssetGUI

3. **Pack the mod:**

   ```powershell
   cd YourMod
   python D:\Desktop\repos\Git\Dungeons-Mod-Kit\Tools\py\u4pak.py pack "YourMod.pak" Dungeons
   ```

4. **Install:**
   - Copy .pak to `E:\SteamLibrary\steamapps\common\MinecraftDungeons\Dungeons\Content\Paks\~mods\`

### Example: Creating a Lobby Mod

```powershell
# Create folder structure
mkdir -p "ModBuild\MyMod\Dungeons\Content\data\levels\lobby"

# Copy original lobby.json
Copy-Item "quickbms\BmsExport\Dungeons\Content\data\levels\lobby\lobby.json" `
          "ModBuild\MyMod\Dungeons\Content\data\levels\lobby\"

# Edit the file (make your changes)
notepad "ModBuild\MyMod\Dungeons\Content\data\levels\lobby\lobby.json"

# Pack it
cd "ModBuild\MyMod"
python D:\Desktop\repos\Git\Dungeons-Mod-Kit\Tools\py\u4pak.py pack "MyMod.pak" Dungeons
```

---

## JSON Modding

### Lobby.json Structure

**Location:** `Dungeons\Content\data\levels\lobby\lobby.json`

Key properties:

```json
{
	"name": "Lobby",
	"level-tag": "camp",
	"resource-packs": ["SquidCoast"],
	"ambience-level-id": "Enderwilds", // ADD THIS for night mode
	"region-id": "squidcoast",
	"level-id": "lobby"
	// ... more properties
}
```

### Ambience Level IDs (Tested)

These can be used in `"ambience-level-id"` to change lighting:

| ID                 | Effect                     |
| ------------------ | -------------------------- |
| `Enderwilds`       | Dark blue tint, night-like |
| `ObsidianPinnacle` | Lighter, less dramatic     |
| `CrimsonForest`    | Red/warm tones             |
| `soulsandvalley`   | Blue-green tones           |
| `netherwastes`     | Orange/red tones           |

> **Note:** Add `"ambience-level-id"` AFTER `"resource-packs"` in the JSON for proper loading.

### JSON Modification Tips

- Keep original file as reference
- Don't remove existing entries unless intentional
- JSON is case-sensitive for property names
- Level IDs may be lowercase (e.g., `soulsandvalley` not `SoulSandValley`)

---

## Binary Asset Modding (UAsset/UExp)

### Understanding UAsset/UExp

- **.uasset** - Header and metadata
- **.uexp** - Actual data/content
- Both files are required and must be modified together
- Files use Unreal Engine serialization format

### UAssetGUI Workflow

1. **Open file:**
   - File → Open → Select .uasset file
   - The .uexp is loaded automatically

2. **Set correct engine version:**
   - For Minecraft Dungeons: **UE4.22**
   - File → Set Serialization Version → UE4_22

3. **Navigate exports:**
   - Expand "Exports" in the tree view
   - Each export is a component/object
   - Properties are in the right panel

4. **Edit values:**
   - Click on property to edit
   - Change values in the editor
   - Press Enter or click away to confirm

5. **Save:**
   - File → Save
   - Both .uasset and .uexp are updated

### Finding the Right Export

- Use grep/search to find property names in extracted files
- Export numbers are consistent across game versions
- Component names hint at functionality (e.g., "SpringArm" = camera)

---

## Camera Rotation Mod

### The Discovery

The game camera is controlled by a Spring Arm component attached to the player character, NOT by level ambience triggers or camera angle assets.

### File Location

```
Dungeons\Content\Actors\Characters\Player\BP_PlayerCharacter.uasset
Dungeons\Content\Actors\Characters\Player\BP_PlayerCharacter.uexp
```

### Modification Details

**Export:** 318 (LovikaSpringArm_GEN_VARIABLE)  
**Property:** RelativeRotation (FRotator)

| Property | Original | Modified | Effect                  |
| -------- | -------- | -------- | ----------------------- |
| Pitch    | -45      | -45      | No change               |
| Yaw      | 45       | 90       | Rotates camera 45° left |
| Roll     | 0        | 0        | No change               |

### Step-by-Step Camera Mod

1. Copy original files:

   ```powershell
   $src = "D:\Desktop\repos\Git\Dungeons-Mod-Kit\quickbms\BmsExport\Dungeons\Content\Actors\Characters\Player"
   $dst = "D:\Desktop\repos\Git\Dungeons-Mod-Kit\ModBuild\CameraMod\Dungeons\Content\Actors\Characters\Player"
   mkdir -p $dst
   Copy-Item "$src\BP_PlayerCharacter.uasset" $dst
   Copy-Item "$src\BP_PlayerCharacter.uexp" $dst
   ```

2. Open in UAssetGUI:
   - Open `BP_PlayerCharacter.uasset`
   - Set version to UE4.22
   - Navigate to Export 318 (LovikaSpringArm_GEN_VARIABLE)
   - Find `RelativeRotation` property
   - Change Yaw (Value index 2) from 45 to desired angle
   - Save

3. Pack the mod:
   ```powershell
   cd "D:\Desktop\repos\Git\Dungeons-Mod-Kit\ModBuild\CameraMod"
   python D:\Desktop\repos\Git\Dungeons-Mod-Kit\Tools\py\u4pak.py pack "CameraRotate.pak" Dungeons
   ```

### Camera Angle Reference

- **Original:** Yaw = 45° (standard isometric view)
- **90°:** Rotated 45° counterclockwise (Tower glitch recreation)
- **0°:** Rotated 45° clockwise
- **135°:** Rotated 90° counterclockwise

---

## Night Mode / Ambience Mod

### How It Works

The lobby (camp) level can load ambience settings from other levels by specifying `ambience-level-id` in lobby.json.

### Creating Night Mode Mod

1. Create folder structure:

   ```powershell
   mkdir -p "ModBuild\NightMod\Dungeons\Content\data\levels\lobby"
   ```

2. Copy original lobby.json:

   ```powershell
   Copy-Item "quickbms\BmsExport\Dungeons\Content\data\levels\lobby\lobby.json" `
             "ModBuild\NightMod\Dungeons\Content\data\levels\lobby\"
   ```

3. Edit lobby.json - Add this line after `"resource-packs"`:

   ```json
   "ambience-level-id": "Enderwilds",
   ```

4. Pack:
   ```powershell
   cd "ModBuild\NightMod"
   python D:\Desktop\repos\Git\Dungeons-Mod-Kit\Tools\py\u4pak.py pack "NightMode.pak" Dungeons
   ```

### Combined Mod (Camera + Night)

To create a mod with both effects:

1. Create folder structure with both paths:

   ```
   CombinedMod/
   └── Dungeons/
       └── Content/
           ├── Actors/Characters/Player/
           │   ├── BP_PlayerCharacter.uasset  (modified camera)
           │   └── BP_PlayerCharacter.uexp
           └── data/levels/lobby/
               └── lobby.json                  (with ambience-level-id)
   ```

2. Pack as single .pak file

---

## Common Pitfalls & Solutions

### Problem: "Serialization Error: Corrupt data" on game load

**Cause:** Binary files were edited with hex editor instead of UAssetGUI  
**Solution:** Use UAssetGUI with correct UE4.22 version setting

### Problem: Mod doesn't load / No effect

**Cause:** Wrong folder structure in PAK  
**Solution:** Ensure path starts with `Dungeons\Content\...` matching game structure

### Problem: JSON changes not working

**Cause:** Syntax error or wrong property placement  
**Solution:** Validate JSON, check property placement order

### Problem: Merchants missing from camp

**Cause:** Mod removed object-groups from lobby.json  
**Solution:** Only add new properties, don't remove existing ones

### Problem: Camera mod doesn't work

**Cause:** Modified wrong file (AT_SetCameraAngel doesn't control main camera)  
**Solution:** Modify BP_PlayerCharacter.uasset Export 318

### Problem: UAssetGUI can't open file

**Cause:** Wrong Unreal version selected  
**Solution:** Set version to UE4.22 before opening

---

## File Locations Quick Reference

### Source Files (Extracted Game Data)

| File             | Path                                                                                |
| ---------------- | ----------------------------------------------------------------------------------- |
| Player Character | `quickbms\BmsExport\Dungeons\Content\Actors\Characters\Player\BP_PlayerCharacter.*` |
| Lobby Definition | `quickbms\BmsExport\Dungeons\Content\data\levels\lobby\lobby.json`                  |
| Level Data       | `quickbms\BmsExport\Dungeons\Content\data\levels\[levelname]\`                      |

### Tools

| Tool      | Path                  |
| --------- | --------------------- |
| u4pak.py  | `Tools\py\u4pak.py`   |
| UAssetGUI | `Tools\UAssetGUI.exe` |
| QuickBMS  | `quickbms\`           |

### Output

| Mod              | Path                                                                              |
| ---------------- | --------------------------------------------------------------------------------- |
| Night Mods       | `ModBuild\Night\`                                                                 |
| Install Location | `E:\SteamLibrary\steamapps\common\MinecraftDungeons\Dungeons\Content\Paks\~mods\` |

---

## Mod Installation

1. Navigate to game mods folder:

   ```
   E:\SteamLibrary\steamapps\common\MinecraftDungeons\Dungeons\Content\Paks\~mods\
   ```

2. Copy your .pak file into the folder

3. Start the game

4. To disable: Remove or rename the .pak file

> **Tip:** Only have one mod active at a time if they modify the same files, or combine them into one .pak.

---

## Future Research Areas

### Unexplored

- [ ] Item stat modifications
- [ ] Enemy behavior changes
- [ ] Level geometry modifications
- [ ] UI customization
- [ ] Sound/music replacement
- [ ] Texture modding
- [ ] Custom levels

### Known File Types

- `.uasset` / `.uexp` - Binary game assets
- `.json` - Configuration data
- `.locres` - Localization (see Locres Editor tool)
- `.ushaderbytecode` - Compiled shaders

### Useful Level IDs for Ambience Testing

Found in game files, not all tested:

- Enderwilds
- ObsidianPinnacle
- CrimsonForest
- soulsandvalley
- netherwastes
- CreeperWoods
- SoggySwamp
- PumpkinPastures
- CactiCanyon
- DesertTemple
- HighblockHalls
- MooShroom

---

## Quick Commands Reference

```powershell
# List PAK contents
python D:\Desktop\repos\Git\Dungeons-Mod-Kit\Tools\py\u4pak.py list "file.pak"

# Extract PAK
python D:\Desktop\repos\Git\Dungeons-Mod-Kit\Tools\py\u4pak.py unpack "file.pak" "output/"

# Create PAK (run from folder containing Dungeons/)
python D:\Desktop\repos\Git\Dungeons-Mod-Kit\Tools\py\u4pak.py pack "output.pak" Dungeons

# Copy mod to game
Copy-Item "mod.pak" "E:\SteamLibrary\steamapps\common\MinecraftDungeons\Dungeons\Content\Paks\~mods\"
```

---

## AI Assistant Context

If you're an AI continuing this project:

1. **Game Engine:** Unreal Engine 4.22
2. **Key Tool:** UAssetGUI for binary edits (NEVER use hex editor)
3. **Camera Control:** BP_PlayerCharacter.uasset → Export 318 → RelativeRotation → Yaw
4. **Night Mode:** lobby.json → add `"ambience-level-id": "Enderwilds"`
5. **PAK Creation:** Use u4pak.py, ensure `Dungeons\Content\` path structure
6. **User's Goal:** Recreate "Tower glitch" visual (dark ambience + rotated camera)

### Successfully Created Mods

- `CameraRotate.pak` - Camera Yaw=90 only
- `Enderwilds90.pak` - Camera + Enderwilds ambience
- `CrimsonForest90.pak` - Camera + Crimson Forest ambience
- `SoulSandValley90.pak` - Camera + Soul Sand Valley ambience
- `NetherWastes90.pak` - Camera + Nether Wastes ambience
- `ObsidianPinnacle90.pak` - Camera + Obsidian Pinnacle ambience

---

_Document created for Dungeons Mod Kit project_
