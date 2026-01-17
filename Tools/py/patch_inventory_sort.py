"""
Minecraft Dungeons - Inventory Sort Patcher
This tool patches UMG_InventoryHUD to add sorting functionality from the storage chest.

The approach: We modify the InventoryHUD to reference and use the UMG_SortSelectionPicker
widget that's already used in the Storage Chest UI.
"""

import os
import sys
import shutil
import struct
from pathlib import Path

# Paths relative to the mod kit root
SCRIPT_DIR = Path(__file__).parent
MOD_KIT_ROOT = SCRIPT_DIR.parent.parent
BMSEXPORT_PATH = MOD_KIT_ROOT / "quickbms" / "BmsExport" / "Dungeons" / "Content"
PRECOOKED_PATH = MOD_KIT_ROOT / "Precooked" / "Content"
OUTPUT_PATH = MOD_KIT_ROOT / "Dungeons" / "Content"

# Source files from the game
INVENTORY_HUD_PATH = BMSEXPORT_PATH / "UI" / "Inventory" / "UMG_InventoryHUD"
SORT_PICKER_PATH = BMSEXPORT_PATH / "Content_Season3" / "UI" / "StorageChest" / "UMG_SortSelectionPicker"
STORAGE_CONTENT_PATH = BMSEXPORT_PATH / "Content_Season2" / "UI" / "Merchant" / "UMG_StorageChestMerchantContent"
SELECT_STORAGE_PATH = BMSEXPORT_PATH / "UI" / "Merchant" / "selection" / "inventoryslot" / "UMG_SelectStorageTransferSlot"


def read_uasset(path):
    """Read a .uasset file and return its contents"""
    uasset_path = Path(str(path) + ".uasset")
    uexp_path = Path(str(path) + ".uexp")

    if not uasset_path.exists():
        print(f"Error: {uasset_path} not found")
        return None, None

    with open(uasset_path, 'rb') as f:
        uasset_data = f.read()

    uexp_data = None
    if uexp_path.exists():
        with open(uexp_path, 'rb') as f:
            uexp_data = f.read()

    return uasset_data, uexp_data


def find_name_table(data):
    """Parse the name table from a uasset file"""
    # UE4 uasset header structure
    # Magic (4 bytes): 0x9E2A83C1
    # Version info, then name table

    if len(data) < 100:
        return []

    # Check magic
    magic = struct.unpack('<I', data[0:4])[0]
    if magic != 0x9E2A83C1:
        print(f"Warning: Unexpected magic number: {hex(magic)}")
        return []

    # Parse header to find name table offset and count
    # Offset 41: NameCount (4 bytes)
    # Offset 45: NameOffset (4 bytes)
    try:
        name_count = struct.unpack('<I', data[41:45])[0]
        name_offset = struct.unpack('<I', data[45:49])[0]
    except:
        return []

    names = []
    pos = name_offset

    for i in range(min(name_count, 1000)):  # Limit to prevent infinite loops
        if pos >= len(data) - 4:
            break

        # Read string length (includes null terminator)
        str_len = struct.unpack('<I', data[pos:pos + 4])[0]
        pos += 4

        if str_len > 1000 or str_len == 0:  # Sanity check
            break

        # Handle negative length (UTF-16)
        if str_len & 0x80000000:
            str_len = -(str_len - 0x100000000) * 2

        if pos + str_len > len(data):
            break

        try:
            name = data[pos:pos + str_len - 1].decode('utf-8', errors='ignore')
            names.append(name)
        except:
            names.append("")

        pos += str_len

        # Skip hash (4 bytes)
        pos += 4

    return names


def analyze_imports(data, names):
    """Analyze import table to find widget references"""
    # Import table comes after names
    # Look for import count and offset in header
    try:
        import_count = struct.unpack('<I', data[57:61])[0]
        import_offset = struct.unpack('<I', data[61:65])[0]
    except:
        return []

    imports = []
    # Each import is 28 bytes in UE4
    pos = import_offset
    for i in range(min(import_count, 500)):
        if pos + 28 > len(data):
            break
        try:
            class_package = struct.unpack('<q', data[pos:pos + 8])[0]
            class_name = struct.unpack('<q', data[pos + 8:pos + 16])[0]
            outer_index = struct.unpack('<i', data[pos + 16:pos + 20])[0]
            object_name = struct.unpack('<i', data[pos + 20:pos + 24])[0]

            # Convert indices to names
            pkg_name = names[class_package] if 0 <= class_package < len(names) else f"idx_{class_package}"
            cls_name = names[class_name] if 0 <= class_name < len(names) else f"idx_{class_name}"
            obj_name = names[object_name] if 0 <= object_name < len(names) else f"idx_{object_name}"

            imports.append({
                'class_package': pkg_name,
                'class_name': cls_name,
                'object_name': obj_name,
                'outer_index': outer_index
            })
        except:
            pass
        pos += 28

    return imports


def find_string_in_binary(data, search_string):
    """Find all occurrences of a string in binary data"""
    search_bytes = search_string.encode('utf-8')
    positions = []
    pos = 0
    while True:
        pos = data.find(search_bytes, pos)
        if pos == -1:
            break
        positions.append(pos)
        pos += 1
    return positions


def patch_add_sort_reference(uasset_data, uexp_data):
    """
    Attempt to patch the inventory HUD to add sorting.

    This is a complex operation. We need to:
    1. Add import reference to UMG_SortSelectionPicker
    2. Add the widget to the visual hierarchy
    3. Connect the sorting events

    For safety, we'll use a simpler approach: redirect to a modified version
    """
    # This direct binary patching is too risky for production
    # Instead, let's create a wrapper approach
    return None, None


def copy_sort_widget_files():
    """Copy the sorting widget files to the mod output"""
    # The sort picker and its dependencies need to be included
    files_to_copy = [
        ("Content_Season3/UI/StorageChest/UMG_SortSelectionPicker", "Content_Season3/UI/StorageChest/UMG_SortSelectionPicker"),
        ("Content_Season3/UI/StorageChest/UMG_SortPickerItem", "Content_Season3/UI/StorageChest/UMG_SortPickerItem"),
        ("Content_Season3/UI/StorageChest/UMG_ExpandingListBase", "Content_Season3/UI/StorageChest/UMG_ExpandingListBase"),
        ("Content_Season3/UI/StorageChest/UMG_ExpandingListItem", "Content_Season3/UI/StorageChest/UMG_ExpandingListItem"),
    ]

    copied = []
    for src_rel, dst_rel in files_to_copy:
        for ext in ['.uasset', '.uexp']:
            src = BMSEXPORT_PATH / (src_rel + ext)
            dst = OUTPUT_PATH / (dst_rel + ext)

            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                copied.append(str(dst))
                print(f"  Copied: {dst.relative_to(MOD_KIT_ROOT)}")

    return copied


def analyze_and_report():
    """Analyze the files and report findings"""
    print("\n" + "=" * 60)
    print("MINECRAFT DUNGEONS - INVENTORY SORT ANALYSIS")
    print("=" * 60)

    # Analyze UMG_InventoryHUD
    print("\n[1] Analyzing UMG_InventoryHUD...")
    inv_uasset, inv_uexp = read_uasset(INVENTORY_HUD_PATH)
    if inv_uasset:
        names = find_name_table(inv_uasset)
        print(f"    File size: {len(inv_uasset):,} bytes (uasset) + {len(inv_uexp) if inv_uexp else 0:,} bytes (uexp)")
        print(f"    Name table entries: {len(names)}")

        # Check for sorting references
        has_sort = any('Sort' in n for n in names)
        has_filter = any('Filter' in n for n in names)
        print(f"    Has sorting: {has_sort}")
        print(f"    Has filtering: {has_filter}")

        # Find filter-related names
        filter_names = [n for n in names if 'Filter' in n][:10]
        if filter_names:
            print(f"    Filter functions: {filter_names[:5]}")

    # Analyze UMG_SortSelectionPicker
    print("\n[2] Analyzing UMG_SortSelectionPicker...")
    sort_uasset, sort_uexp = read_uasset(SORT_PICKER_PATH)
    if sort_uasset:
        names = find_name_table(sort_uasset)
        print(f"    File size: {len(sort_uasset):,} bytes (uasset) + {len(sort_uexp) if sort_uexp else 0:,} bytes (uexp)")
        sort_names = [n for n in names if 'Sort' in n or 'sort' in n]
        print(f"    Sort-related names: {sort_names[:10]}")

    # Analyze UMG_SelectStorageTransferSlot (has the actual sorting logic)
    print("\n[3] Analyzing UMG_SelectStorageTransferSlot...")
    storage_uasset, storage_uexp = read_uasset(SELECT_STORAGE_PATH)
    if storage_uasset:
        names = find_name_table(storage_uasset)
        print(f"    File size: {len(storage_uasset):,} bytes (uasset) + {len(storage_uexp) if storage_uexp else 0:,} bytes (uexp)")
        sort_funcs = [n for n in names if 'Sort' in n]
        print(f"    Sorting functions: {sort_funcs}")

    return inv_uasset, inv_uexp


def create_modified_inventory_hud():
    """
    Create a modified UMG_InventoryHUD that includes sorting.

    Strategy: We'll copy the SelectStorageTransferSlot's sorting approach
    and integrate it into the InventoryHUD by creating a wrapper widget.
    """
    print("\n" + "=" * 60)
    print("CREATING MODIFIED INVENTORY WITH SORTING")
    print("=" * 60)

    # For complex blueprint modifications, we need to use a different approach
    # Let's copy the necessary files and provide instructions

    precooked_ui_path = PRECOOKED_PATH / "UI" / "Inventory"
    precooked_ui_path.mkdir(parents=True, exist_ok=True)

    # Copy the original InventoryHUD files to precooked
    print("\n[Step 1] Copying base files to Precooked folder...")

    for ext in ['.uasset', '.uexp']:
        src = Path(str(INVENTORY_HUD_PATH) + ext)
        if src.exists():
            dst = precooked_ui_path / f"UMG_InventoryHUD{ext}"
            shutil.copy2(src, dst)
            print(f"  Copied: {dst.relative_to(MOD_KIT_ROOT)}")

    # Copy sort picker dependencies
    print("\n[Step 2] Copying sort picker widgets...")
    copy_sort_widget_files()

    # Copy the SelectStorageTransferSlot which has the sorting logic
    print("\n[Step 3] Copying sorting logic components...")
    select_storage_src = BMSEXPORT_PATH / "UI" / "Merchant" / "selection" / "inventoryslot"
    select_storage_dst = OUTPUT_PATH / "UI" / "Merchant" / "selection" / "inventoryslot"
    select_storage_dst.mkdir(parents=True, exist_ok=True)

    for filename in ['UMG_SelectInventorySlot', 'UMG_SelectStorageTransferSlot']:
        for ext in ['.uasset', '.uexp']:
            src = select_storage_src / f"{filename}{ext}"
            if src.exists():
                dst = select_storage_dst / f"{filename}{ext}"
                shutil.copy2(src, dst)
                print(f"  Copied: {dst.relative_to(MOD_KIT_ROOT)}")

    # Copy BPL_Merchants which has GetSortText
    print("\n[Step 4] Copying merchant utilities...")
    bpl_src = BMSEXPORT_PATH / "UI" / "Merchant"
    bpl_dst = OUTPUT_PATH / "UI" / "Merchant"
    bpl_dst.mkdir(parents=True, exist_ok=True)

    for ext in ['.uasset', '.uexp']:
        src = bpl_src / f"BPL_Merchants{ext}"
        if src.exists():
            dst = bpl_dst / f"BPL_Merchants{ext}"
            shutil.copy2(src, dst)
            print(f"  Copied: {dst.relative_to(MOD_KIT_ROOT)}")

    return True


def create_uassetgui_instructions():
    """Create instructions for using UAssetGUI to complete the modification"""
    instructions = """
================================================================================
INVENTORY SORTING MOD - MANUAL COMPLETION STEPS
================================================================================

The automated tool has copied all necessary supporting files. To complete the
modification, you need to edit UMG_InventoryHUD.uasset using UAssetGUI.

DOWNLOAD UASSETGUI:
  https://github.com/atenfyr/UAssetGUI/releases

STEPS TO ADD SORTING:

1. Open UAssetGUI and load:
   Precooked/Content/UI/Inventory/UMG_InventoryHUD.uasset

2. In the Name Map, add these new names:
   - UMG_SortSelectionPicker
   - UMG_SortSelectionPicker_C
   - /Game/Content_Season3/UI/StorageChest/UMG_SortSelectionPicker
   - InventorySort
   - onOptionSelected
   - SortItems
   - sortBy
   - EItemSortMethod

3. In the Import Table, add an import for:
   - ClassPackage: /Game/Content_Season3/UI/StorageChest/UMG_SortSelectionPicker
   - ClassName: WidgetBlueprintGeneratedClass
   - ObjectName: UMG_SortSelectionPicker_C

4. In the Export Table, find the main widget hierarchy and add a child widget
   of type UMG_SortSelectionPicker_C named "InventorySort"

5. Save the modified file

6. Run cook_assets.bat or package.bat to test

ALTERNATIVE (EASIER):
If UAssetGUI modification is too complex, you can:

1. Open the UE4 project in Unreal Editor 4.22
2. Create a new Widget Blueprint based on UMG_InventoryHUD
3. Add the UMG_SortSelectionPicker widget to the UI
4. Connect the onOptionSelected event to call SortItems on your inventory
5. Cook and package

================================================================================
"""

    instructions_path = MOD_KIT_ROOT / "Tools" / "INVENTORY_SORT_INSTRUCTIONS.txt"
    with open(instructions_path, 'w') as f:
        f.write(instructions)
    print(f"\n[INFO] Instructions saved to: {instructions_path.relative_to(MOD_KIT_ROOT)}")
    return instructions_path


def attempt_binary_patch():
    """
    Attempt to create a working patch by modifying the binary directly.
    This is experimental but might work for simple additions.
    """
    print("\n" + "=" * 60)
    print("ATTEMPTING BINARY PATCH (EXPERIMENTAL)")
    print("=" * 60)

    inv_uasset, inv_uexp = read_uasset(INVENTORY_HUD_PATH)
    if not inv_uasset or not inv_uexp:
        print("Error: Could not read inventory files")
        return False

    # Parse the name table
    names = find_name_table(inv_uasset)
    print(f"Found {len(names)} names in the asset")

    # Check if sorting already exists
    if any('SortSelectionPicker' in n for n in names):
        print("Sorting widget reference already exists!")
        return True

    # Find where the filter buttons are defined - we'll add sort nearby
    filter_refs = [i for i, n in enumerate(names) if 'FilterButton' in n or 'FiltersRow' in n]
    print(f"Filter button name indices: {filter_refs}")

    # For now, let's just copy the files and note what needs to change
    # Direct binary editing of UE4 assets is extremely complex

    print("\n[!] Direct binary patching is too risky for blueprint logic.")
    print("[!] Falling back to file preparation + manual instructions.")

    return False


def main():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     MINECRAFT DUNGEONS - INVENTORY SORT PATCHER v1.0         ║
    ║                                                              ║
    ║  This tool adds sorting functionality to the regular         ║
    ║  inventory (outside the storage chest)                       ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    # Check if BmsExport exists
    if not BMSEXPORT_PATH.exists():
        print("ERROR: BmsExport folder not found!")
        print("Please extract the game files using QuickBMS first.")
        print(f"Expected path: {BMSEXPORT_PATH}")
        return 1

    # Analyze the files
    analyze_and_report()

    # Attempt the patch
    if not attempt_binary_patch():
        # Fallback: prepare files and provide instructions
        create_modified_inventory_hud()
        create_uassetgui_instructions()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
Files have been prepared in the following locations:

  Precooked/Content/UI/Inventory/
    - UMG_InventoryHUD.uasset (base file to modify)
    - UMG_InventoryHUD.uexp

  Dungeons/Content/Content_Season3/UI/StorageChest/
    - UMG_SortSelectionPicker.* (sorting dropdown widget)
    - UMG_SortPickerItem.* (individual sort options)
    - UMG_ExpandingListBase.* (base list widget)
    - UMG_ExpandingListItem.* (list item widget)

  Dungeons/Content/UI/Merchant/
    - BPL_Merchants.* (utility functions)
    - selection/inventoryslot/* (sorting logic)

NEXT STEPS:
1. Read Tools/INVENTORY_SORT_INSTRUCTIONS.txt
2. Use UAssetGUI to edit the InventoryHUD
3. Run package.bat to create the mod
4. Test in game!
    """)

    return 0


if __name__ == "__main__":
    sys.exit(main())
