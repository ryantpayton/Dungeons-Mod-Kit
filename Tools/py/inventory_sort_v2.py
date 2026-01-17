"""
Minecraft Dungeons - Inventory Sort Mod (Alternative Approach)
This script attempts a different strategy: replacing key inventory components
with modified versions that include sorting.
"""

import os
import sys
import struct
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
MOD_KIT_ROOT = SCRIPT_DIR.parent.parent
BMSEXPORT_PATH = MOD_KIT_ROOT / "quickbms" / "BmsExport" / "Dungeons" / "Content"
PRECOOKED_PATH = MOD_KIT_ROOT / "Precooked" / "Content"
DUNGEONS_PATH = MOD_KIT_ROOT / "Dungeons" / "Content"


def read_name_table(uasset_path):
    """Read the name table from a uasset file"""
    with open(uasset_path, 'rb') as f:
        data = f.read()

    name_count = struct.unpack('<i', data[41:45])[0]
    name_offset = struct.unpack('<i', data[45:49])[0]

    pos = name_offset
    names = []
    for i in range(min(name_count, 5000)):
        if pos >= len(data) - 4:
            break
        str_len = struct.unpack('<i', data[pos:pos + 4])[0]
        pos += 4
        if str_len < 0:
            str_len = -str_len
            name = data[pos:pos + str_len * 2].decode('utf-16-le', errors='ignore').rstrip('\x00')
            pos += str_len * 2
        elif 0 < str_len < 1000:
            name = data[pos:pos + str_len].decode('utf-8', errors='ignore').rstrip('\x00')
            pos += str_len
        else:
            break
        names.append(name)
        pos += 4  # hash

    return names, data


def find_bytes_pattern(data, pattern):
    """Find all occurrences of a byte pattern"""
    results = []
    start = 0
    while True:
        pos = data.find(pattern, start)
        if pos == -1:
            break
        results.append(pos)
        start = pos + 1
    return results


def patch_uasset_names(uasset_data, names_to_add):
    """
    Add new names to a uasset file's name table.
    Returns the modified data and a mapping of new name indices.
    """
    data = bytearray(uasset_data)

    # Read header info
    name_count = struct.unpack('<i', data[41:45])[0]
    name_offset = struct.unpack('<i', data[45:49])[0]

    # Find the end of the name table
    pos = name_offset
    for i in range(name_count):
        if pos >= len(data) - 4:
            break
        str_len = struct.unpack('<i', data[pos:pos + 4])[0]
        pos += 4
        if str_len < 0:
            pos += (-str_len) * 2
        elif str_len > 0:
            pos += str_len
        pos += 4  # hash

    name_table_end = pos

    # Add new names
    new_indices = {}
    new_data = bytearray()

    for name in names_to_add:
        name_bytes = name.encode('utf-8') + b'\x00'

        # Simple hash
        hash_val = 0
        for c in name.lower():
            hash_val = ((hash_val ^ ord(c)) * 0x01000193) & 0xFFFFFFFF

        new_data.extend(struct.pack('<I', len(name_bytes)))
        new_data.extend(name_bytes)
        new_data.extend(struct.pack('<I', hash_val))

        new_indices[name] = name_count
        name_count += 1

    # Insert the new name entries
    data[name_table_end:name_table_end] = new_data

    # Update the name count in header
    data[41:45] = struct.pack('<i', name_count)

    # Update all offsets after the name table
    offset_to_update = [
        (49, 4),   # export count offset references
        (53, 4),   # export offset
        (57, 4),   # import count
        (61, 4),   # import offset
        (65, 4),   # depends offset
    ]

    shift = len(new_data)
    for offset, size in offset_to_update:
        if offset + size <= len(data):
            old_val = struct.unpack('<i', data[offset:offset + size])[0]
            if old_val > name_table_end:
                data[offset:offset + size] = struct.pack('<i', old_val + shift)

    return bytes(data), new_indices


def create_sorting_mod_v2():
    """
    Alternative approach: Copy the UMG_SelectStorageTransferSlot and modify
    it to work as a standalone inventory sorter.
    """
    print("=" * 60)
    print("INVENTORY SORT MOD - ALTERNATIVE APPROACH")
    print("=" * 60)

    # The SelectStorageTransferSlot already has full sorting implementation
    # We'll copy it and the related files

    print("\n[1] Copying storage transfer slot (has sorting logic)...")

    src_dir = BMSEXPORT_PATH / "UI" / "Merchant" / "selection" / "inventoryslot"
    dst_dir = DUNGEONS_PATH / "UI" / "Merchant" / "selection" / "inventoryslot"
    dst_dir.mkdir(parents=True, exist_ok=True)

    for filename in ["UMG_SelectInventorySlot", "UMG_SelectStorageTransferSlot"]:
        for ext in [".uasset", ".uexp"]:
            src = src_dir / f"{filename}{ext}"
            dst = dst_dir / f"{filename}{ext}"
            if src.exists():
                shutil.copy2(src, dst)
                print(f"  ✓ Copied {filename}{ext}")

    print("\n[2] Copying sort picker widgets...")

    src_dir = BMSEXPORT_PATH / "Content_Season3" / "UI" / "StorageChest"
    dst_dir = DUNGEONS_PATH / "Content_Season3" / "UI" / "StorageChest"
    dst_dir.mkdir(parents=True, exist_ok=True)

    for filename in ["UMG_SortSelectionPicker", "UMG_SortPickerItem",
                     "UMG_ExpandingListBase", "UMG_ExpandingListItem"]:
        for ext in [".uasset", ".uexp"]:
            src = src_dir / f"{filename}{ext}"
            dst = dst_dir / f"{filename}{ext}"
            if src.exists():
                shutil.copy2(src, dst)
                print(f"  ✓ Copied {filename}{ext}")

    print("\n[3] Copying StorageChestMerchantContent (has sorting implementation)...")

    src_dir = BMSEXPORT_PATH / "Content_Season2" / "UI" / "Merchant"
    dst_dir = DUNGEONS_PATH / "Content_Season2" / "UI" / "Merchant"
    dst_dir.mkdir(parents=True, exist_ok=True)

    for filename in ["UMG_StorageChestMerchantContent", "UMG_StorageChestMerchantWidget",
                     "UMG_FilterSelection"]:
        for ext in [".uasset", ".uexp"]:
            src = src_dir / f"{filename}{ext}"
            dst = dst_dir / f"{filename}{ext}"
            if src.exists():
                shutil.copy2(src, dst)
                print(f"  ✓ Copied {filename}{ext}")

    print("\n[4] Attempting to patch InventoryHUD to use sorting components...")

    # Read the inventory HUD
    inv_uasset = BMSEXPORT_PATH / "UI" / "Inventory" / "UMG_InventoryHUD.uasset"
    inv_uexp = BMSEXPORT_PATH / "UI" / "Inventory" / "UMG_InventoryHUD.uexp"

    with open(inv_uasset, 'rb') as f:
        uasset_data = f.read()
    with open(inv_uexp, 'rb') as f:
        uexp_data = f.read()

    # Read the storage chest to understand the sorting structure
    storage_uasset = BMSEXPORT_PATH / "Content_Season2" / "UI" / "Merchant" / "UMG_StorageChestMerchantContent.uasset"
    storage_uexp = BMSEXPORT_PATH / "Content_Season2" / "UI" / "Merchant" / "UMG_StorageChestMerchantContent.uexp"

    with open(storage_uasset, 'rb') as f:
        storage_uasset_data = f.read()
    with open(storage_uexp, 'rb') as f:
        storage_uexp_data = f.read()

    # Add sorting-related names to the inventory HUD
    names_to_add = [
        "/Game/Content_Season3/UI/StorageChest/UMG_SortSelectionPicker",
        "UMG_SortSelectionPicker_C",
        "InventorySort",
        "onOptionSelected",
        "OnSortOptionSelected",
        "SortItems",
        "sortBy",
        "EItemSortMethod",
        "GetSelectedSort",
        "sortMethod",
        "ApplyFiltersAndSorting",
        "SetInventoryFilterSort",
        "CurrentSortMethod",
        "BndEvt__InventorySort_K2Node_ComponentBoundEvent_onOptionSelected__DelegateSignature",
    ]

    patched_uasset, name_indices = patch_uasset_names(uasset_data, names_to_add)

    print(f"  Added {len(names_to_add)} new names to InventoryHUD")
    for name, idx in name_indices.items():
        print(f"    [{idx}] {name[:50]}...")

    # Save the patched files
    out_dir = DUNGEONS_PATH / "UI" / "Inventory"
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir / "UMG_InventoryHUD.uasset", 'wb') as f:
        f.write(patched_uasset)
    with open(out_dir / "UMG_InventoryHUD.uexp", 'wb') as f:
        f.write(uexp_data)

    print(f"\n  ✓ Saved patched InventoryHUD to {out_dir}")

    # Also copy merchant utilities
    print("\n[5] Copying additional utilities...")

    bpl_src = BMSEXPORT_PATH / "UI" / "Merchant"
    bpl_dst = DUNGEONS_PATH / "UI" / "Merchant"
    bpl_dst.mkdir(parents=True, exist_ok=True)

    for ext in [".uasset", ".uexp"]:
        src = bpl_src / f"BPL_Merchants{ext}"
        dst = bpl_dst / f"BPL_Merchants{ext}"
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✓ Copied BPL_Merchants{ext}")

    # Copy sound effect
    sfx_src = BMSEXPORT_PATH / "AudioForce" / "04_playback_soundCue" / "03_sfx_ui"
    sfx_dst = DUNGEONS_PATH / "AudioForce" / "04_playback_soundCue" / "03_sfx_ui"
    sfx_dst.mkdir(parents=True, exist_ok=True)

    for ext in [".uasset", ".uexp"]:
        src = sfx_src / f"sfx_ui_diabloSort{ext}"
        dst = sfx_dst / f"sfx_ui_diabloSort{ext}"
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✓ Copied sfx_ui_diabloSort{ext}")

    print("\n" + "=" * 60)
    print("PATCH COMPLETE")
    print("=" * 60)
    print("""
The InventoryHUD has been patched with sorting name references.

IMPORTANT: This patch adds the NAME TABLE entries for sorting, but the
actual widget instantiation and event binding requires modifying the
serialized object data in the uexp file, which is extremely complex.

For a working solution, you have two options:

OPTION A - Use UAssetGUI (Recommended):
  1. Download UAssetGUI from: https://github.com/atenfyr/UAssetGUI/releases
  2. Open: Dungeons/Content/UI/Inventory/UMG_InventoryHUD.uasset
  3. In the export data, find the widget tree
  4. Add a new UMG_SortSelectionPicker widget instance
  5. Connect the onOptionSelected event
  6. Save and repackage

OPTION B - Use Unreal Editor 4.22:
  1. Open UE4Project/Dungeons.uproject in UE4 4.22
  2. Create a child Blueprint of UMG_InventoryHUD  
  3. Add the sort picker widget in the designer
  4. Implement the sorting event handler
  5. Run cook_assets.bat, then package.bat
""")

    return True


def main():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     MINECRAFT DUNGEONS - INVENTORY SORT MOD v2              ║
    ║            Alternative Patching Approach                     ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    if not BMSEXPORT_PATH.exists():
        print("ERROR: quickbms/BmsExport not found!")
        return 1

    create_sorting_mod_v2()
    return 0


if __name__ == "__main__":
    sys.exit(main())
