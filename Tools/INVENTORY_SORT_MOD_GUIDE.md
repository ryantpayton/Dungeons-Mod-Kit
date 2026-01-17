# Inventory Sort Mod - Step by Step Guide

This guide walks you through adding inventory sorting to the regular inventory screen using Unreal Editor 4.22.

## Prerequisites

- ✅ Unreal Engine 4.22 installed (`C:\Program Files\Epic Games\UE_4.22`)
- ✅ Mod kit with extracted game files

## Overview

The sorting functionality already exists in the **Storage Chest** UI (`UMG_SelectStorageTransferSlot`). We will:

1. Open the UE4 project in Unreal Editor
2. Add the Sort Picker widget to the Inventory HUD
3. Wire up the sorting logic
4. Cook and package the mod

---

## Step 1: Open the UE4 Project

1. Navigate to: `D:\Desktop\repos\Git\Dungeons-Mod-Kit\UE4Project`
2. Double-click `Dungeons.uproject` (or open from Epic Games Launcher)
3. Wait for the editor to load and compile shaders (first time may take several minutes)

---

## Step 2: Open the Inventory HUD Widget

1. In the **Content Browser** (bottom panel), navigate to:
   ```
   Content > UI > Inventory
   ```
2. Double-click `UMG_InventoryHUD` to open the Widget Blueprint editor

---

## Step 3: Study the Storage Chest for Reference

1. Open another reference widget by navigating to:
   ```
   Content > UI > Merchant > selection > inventoryslot
   ```
2. Double-click `UMG_SelectStorageTransferSlot` to see how sorting is implemented
3. In the **Designer** tab, find the `InventorySort` widget in the hierarchy
4. Note how the `UMG_SortSelectionPicker` is placed

---

## Step 4: Add the Sort Picker to Inventory HUD

### Option A: Simple Approach (Add Sort Picker Widget)

1. In `UMG_InventoryHUD` Designer view, find the **Palette** panel (usually on the left)
2. Search for `UMG_SortSelectionPicker`
3. Drag it onto your inventory panel - position it near the Filter buttons
4. In the **Details** panel, configure:
   - **Name**: `InventorySort`
   - **Visibility**: Visible
   - **Is Enabled**: True

### Option B: Copy from Storage Chest

1. In `UMG_SelectStorageTransferSlot`, find the `InventorySort` widget
2. Right-click → Copy
3. Switch to `UMG_InventoryHUD`
4. Right-click on a container → Paste

---

## Step 5: Connect the Sorting Logic

1. Switch to the **Graph** tab in `UMG_InventoryHUD`
2. Create a new Variable:
   - Name: `CurrentSortMethod`
   - Type: `EItemSortMethod` (search for it)
   - Default: `None` or `Rarity`

3. Create Event Binding:
   - Find your `InventorySort` widget in the variables
   - Drag it to the graph and select "On Selection Changed"
   - Connect it to call `SortItems` function on the inventory grid

4. In the Event Graph, add logic:
   ```
   Event OnSortSelectionChanged(NewSortMethod)
   → Set CurrentSortMethod = NewSortMethod
   → Call SortItems(NewSortMethod) on the SlotGrid/InventoryGrid widget
   ```

---

## Step 6: Add Required References (if needed)

If the editor shows missing references, ensure these assets exist:

```
Content > Content_Season3 > UI > StorageChest:
  - EItemSortMethod (enum)
  - UMG_SortSelectionPicker (widget)
  - UMG_SortPickerItem (widget)
```

Copy them from the extracted game files if missing:

```
quickbms/BmsExport/Dungeons/Content/Content_Season3/UI/StorageChest/
```

---

## Step 7: Save and Compile

1. Click **Compile** in the Blueprint toolbar (check mark icon)
2. Ensure no errors appear in the bottom log
3. Click **Save** (Ctrl+S)

---

## Step 8: Cook the Assets

1. Close Unreal Editor
2. Open Command Prompt in the mod kit folder
3. Run:
   ```batch
   cook_assets.bat
   ```
4. Wait for cooking to complete

---

## Step 9: Package the Mod

1. After cooking completes, run:
   ```batch
   package.bat
   ```
2. The output will tell you where the .pak file was created

---

## Step 10: Install the Mod

1. Copy the `.pak` file to your game's mod folder:
   ```
   E:\SteamLibrary\steamapps\common\MinecraftDungeons\Dungeons\Content\Paks\~mods\
   ```
2. Create the `~mods` folder if it doesn't exist

3. Rename your pak file to start with `~` (e.g., `~InventorySort.pak`)

---

## Step 11: Test the Mod

1. Launch Minecraft Dungeons
2. Open your inventory
3. Look for the new Sort dropdown

---

## Troubleshooting

### Sort picker doesn't appear

- Make sure the widget is marked as Visible
- Check the Z-order (it might be behind other elements)
- Ensure the widget is inside a visible container

### Game crashes on startup

- The .pak file structure might be wrong
- Check that cooking completed without errors
- Try removing other mods to isolate the issue

### Sorting doesn't work when clicked

- Check the Event Graph connections
- Ensure `SortItems` function is being called
- Verify `EItemSortMethod` enum is accessible

---

## Alternative: Quick Keybind Approach

If the visual widget approach is too complex, you can try:

1. Add a keyboard shortcut that cycles through sort methods
2. Bind a key (like `V`) to call `SortItems()` directly
3. This requires modifying `UMG_InventoryHUD` Event Graph only

---

## File Locations Quick Reference

| Asset                     | Path                                                                        |
| ------------------------- | --------------------------------------------------------------------------- |
| Inventory HUD             | `Content/UI/Inventory/UMG_InventoryHUD`                                     |
| Storage Chest (reference) | `Content/UI/Merchant/selection/inventoryslot/UMG_SelectStorageTransferSlot` |
| Sort Picker Widget        | `Content/Content_Season3/UI/StorageChest/UMG_SortSelectionPicker`           |
| Sort Method Enum          | `Content/Content_Season3/UI/StorageChest/EItemSortMethod`                   |
| Sort Picker Item          | `Content/Content_Season3/UI/StorageChest/UMG_SortPickerItem`                |

---

## Need More Help?

If you get stuck, the key concepts are:

1. Widget Blueprint Designer for visual layout
2. Widget Blueprint Graph for logic/events
3. The `SortItems()` function already exists in `UMG_SelectInventorySlot`
4. `EItemSortMethod` enum has the sort options (Rarity, Power, Type, etc.)
