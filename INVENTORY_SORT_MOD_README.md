# Minecraft Dungeons - Inventory Sort Mod

This mod adds sorting functionality to the regular inventory screen, similar to how you can sort items in the Storage Chest.

## Current Status: **Work in Progress**

The mod currently includes all the necessary **supporting files** for sorting functionality:

- Sort selection picker widget (dropdown UI)
- Sort picker item widgets
- Sorting logic components
- Sort sound effects

**However**, the complete integration with the main inventory HUD requires additional blueprint modification that cannot be fully automated.

## What's Included

| File                              | Purpose                                              |
| --------------------------------- | ---------------------------------------------------- |
| `UMG_SortSelectionPicker.*`       | The sort dropdown widget                             |
| `UMG_SortPickerItem.*`            | Individual sort option items                         |
| `UMG_ExpandingListBase.*`         | Base list widget for dropdowns                       |
| `UMG_ExpandingListItem.*`         | List item widget                                     |
| `UMG_SelectInventorySlot.*`       | Contains `SortItems()` function                      |
| `UMG_SelectStorageTransferSlot.*` | Full sorting logic reference                         |
| `BPL_Merchants.*`                 | Merchant utility functions including `GetSortText()` |
| `sfx_ui_diabloSort.*`             | Sort sound effect                                    |

## Installation (Testing)

1. Copy `Dungeons_InventorySort_Test.pak` to your game's `~mods` folder:

   ```
   C:\Games\Minecraft Dungeons\Dungeons\Content\Paks\~mods\
   ```

2. Launch the game and check if sorting appears in the inventory

## Complete Integration Options

If the simple installation doesn't add sorting to your inventory, you'll need to complete the integration manually:

### Option A: Using UAssetGUI (Recommended)

1. Download [UAssetGUI](https://github.com/atenfyr/UAssetGUI/releases)

2. Open `Precooked/Content/UI/Inventory/UMG_InventoryHUD.uasset`

3. In the Name Map, add:
   - `UMG_SortSelectionPicker_C`
   - `/Game/Content_Season3/UI/StorageChest/UMG_SortSelectionPicker`
   - `InventorySort`
   - `onOptionSelected`

4. In the Import Table, add an import for the sort picker widget

5. Find the FiltersRow in the widget hierarchy and add a UMG_SortSelectionPicker child

6. Save and run `package.bat`

### Option B: Using Unreal Editor 4.22

1. Install Unreal Engine 4.22 from Epic Games Store

2. Open `UE4Project/Dungeons.uproject`

3. Create a new Widget Blueprint or modify the existing one

4. Add the UMG_SortSelectionPicker widget to your layout

5. Connect the sorting events in the Event Graph

6. Run `cook_assets.bat` then `package.bat`

## Tools Included

| Tool                                 | Description                               |
| ------------------------------------ | ----------------------------------------- |
| `Tools/py/inventory_sort_mod.py`     | Main setup script - copies required files |
| `Tools/py/uasset_patcher.py`         | Attempts to patch the inventory uasset    |
| `Tools/py/patch_inventory_sort.py`   | Analysis and file preparation             |
| `Tools/build_inventory_sort_mod.bat` | One-click build script                    |

## How Sorting Works in the Game

The game's sorting system uses:

1. **EItemSortMethod** - Enum defining sort options (Power, Rarity, Type, etc.)
2. **SortItems()** - Function that reorders the item array
3. **UMG_SortSelectionPicker** - UI widget for selecting sort method
4. **SetInventoryFilterSort()** - Applies the selected sort to inventory

The Storage Chest UI (`UMG_StorageChestMerchantContent`) already has this fully implemented. This mod attempts to bring the same functionality to the regular inventory.

## Technical Details

The inventory HUD (`UMG_InventoryHUD.uasset`) is a 1.2MB compiled Blueprint with:

- 3293 name entries
- 8568 imports
- Complex widget hierarchy

Modifying this requires understanding the UE4 uasset binary format and carefully adding:

1. New name references
2. Import entries for the sort picker class
3. Widget instances in the hierarchy
4. Event bindings for sort selection

## Contributing

If you successfully complete the integration, please share your modified files so others can benefit!

## Credits

- Dungeons Mod Kit by [Dokucraft](https://github.com/Dokucraft/Dungeons-Mod-Kit)
- Original game by Mojang Studios / Double Eleven
