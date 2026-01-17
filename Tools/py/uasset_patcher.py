"""
Minecraft Dungeons - UAsset Patcher for Inventory Sorting
Advanced binary patching tool that modifies the UMG_InventoryHUD blueprint
to include sorting functionality.

This tool uses knowledge of the UE4 uasset format to inject the necessary
references and logic.
"""

import os
import sys
import struct
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional
import copy

SCRIPT_DIR = Path(__file__).parent
MOD_KIT_ROOT = SCRIPT_DIR.parent.parent
BMSEXPORT_PATH = MOD_KIT_ROOT / "quickbms" / "BmsExport" / "Dungeons" / "Content"
PRECOOKED_PATH = MOD_KIT_ROOT / "Precooked" / "Content"


@dataclass
class UAssetHeader:
    """UE4 Asset Header Structure"""
    magic: int  # 0x9E2A83C1
    legacy_version: int
    legacy_ue3_version: int
    file_version_ue4: int
    file_version_licensee: int
    custom_version_count: int
    total_header_size: int
    folder_name_len: int
    folder_name: str
    package_flags: int
    name_count: int
    name_offset: int
    gatherable_text_data_count: int
    gatherable_text_data_offset: int
    export_count: int
    export_offset: int
    import_count: int
    import_offset: int
    depends_offset: int
    soft_package_references_count: int
    soft_package_references_offset: int
    searchable_names_offset: int
    thumbnail_table_offset: int
    guid: bytes
    generations: list
    saved_by_engine_version: tuple
    compatible_with_engine_version: tuple
    compression_flags: int
    compressed_chunks: list
    package_source: int
    additional_packages: list
    asset_registry_data_offset: int
    bulk_data_start_offset: int
    world_tile_info_data_offset: int
    chunk_ids: list
    preload_dependency_count: int
    preload_dependency_offset: int


class UAssetParser:
    """Parser for UE4 .uasset files"""

    def __init__(self, uasset_path: Path, uexp_path: Optional[Path] = None):
        self.uasset_path = uasset_path
        self.uexp_path = uexp_path

        with open(uasset_path, 'rb') as f:
            self.uasset_data = bytearray(f.read())

        self.uexp_data = None
        if uexp_path and uexp_path.exists():
            with open(uexp_path, 'rb') as f:
                self.uexp_data = bytearray(f.read())

        self.names: List[str] = []
        self.imports: List[dict] = []
        self.exports: List[dict] = []
        self._parse()

    def _read_int32(self, data: bytes, offset: int) -> int:
        return struct.unpack('<i', data[offset:offset + 4])[0]

    def _read_uint32(self, data: bytes, offset: int) -> int:
        return struct.unpack('<I', data[offset:offset + 4])[0]

    def _read_int64(self, data: bytes, offset: int) -> int:
        return struct.unpack('<q', data[offset:offset + 8])[0]

    def _write_int32(self, data: bytearray, offset: int, value: int):
        data[offset:offset + 4] = struct.pack('<i', value)

    def _write_uint32(self, data: bytearray, offset: int, value: int):
        data[offset:offset + 4] = struct.pack('<I', value)

    def _parse(self):
        """Parse the uasset header and tables"""
        data = self.uasset_data

        # Verify magic
        magic = self._read_uint32(data, 0)
        if magic != 0x9E2A83C1:
            raise ValueError(f"Invalid uasset magic: {hex(magic)}")

        # Parse key offsets (UE4 4.22 format)
        self.name_count = self._read_int32(data, 41)
        self.name_offset = self._read_int32(data, 45)
        self.export_count = self._read_int32(data, 49)
        self.export_offset = self._read_int32(data, 53)
        self.import_count = self._read_int32(data, 57)
        self.import_offset = self._read_int32(data, 61)

        # Parse name table
        self._parse_names()

        # Parse import table
        self._parse_imports()

        # Parse export table
        self._parse_exports()

    def _parse_names(self):
        """Parse the name table"""
        data = self.uasset_data
        pos = self.name_offset

        for i in range(self.name_count):
            if pos >= len(data):
                break

            # Read string length
            str_len = self._read_int32(data, pos)
            pos += 4

            # Handle UTF-16 strings (negative length)
            is_utf16 = False
            if str_len < 0:
                is_utf16 = True
                str_len = -str_len

            if str_len > 10000:  # Sanity check
                break

            # Read string
            if is_utf16:
                name = data[pos:pos + str_len * 2].decode('utf-16-le', errors='ignore').rstrip('\x00')
                pos += str_len * 2
            else:
                name = data[pos:pos + str_len].decode('utf-8', errors='ignore').rstrip('\x00')
                pos += str_len

            self.names.append(name)

            # Skip hash (4 bytes) - only for case-insensitive
            # For UE4.22+, there's also case preserving hash
            pos += 4  # Non-case-preserving hash

        self.name_table_end = pos

    def _parse_imports(self):
        """Parse the import table"""
        data = self.uasset_data
        pos = self.import_offset

        for i in range(self.import_count):
            if pos + 28 > len(data):
                break

            imp = {
                'class_package_idx': self._read_int64(data, pos),
                'class_name_idx': self._read_int64(data, pos + 8),
                'outer_index': self._read_int32(data, pos + 16),
                'object_name_idx': self._read_int32(data, pos + 20),
                'offset': pos
            }

            # Resolve names
            cp_idx = imp['class_package_idx']
            cn_idx = imp['class_name_idx']
            on_idx = imp['object_name_idx']

            imp['class_package'] = self.names[cp_idx] if 0 <= cp_idx < len(self.names) else f"idx_{cp_idx}"
            imp['class_name'] = self.names[cn_idx] if 0 <= cn_idx < len(self.names) else f"idx_{cn_idx}"
            imp['object_name'] = self.names[on_idx] if 0 <= on_idx < len(self.names) else f"idx_{on_idx}"

            self.imports.append(imp)
            pos += 28

        self.import_table_end = pos

    def _parse_exports(self):
        """Parse the export table (partial - just for reference)"""
        data = self.uasset_data
        pos = self.export_offset

        # Export entries are variable size in UE4, this is simplified
        for i in range(min(self.export_count, 100)):
            if pos + 104 > len(data):  # Minimum export entry size
                break

            exp = {
                'class_index': self._read_int32(data, pos),
                'super_index': self._read_int32(data, pos + 4),
                'template_index': self._read_int32(data, pos + 8),
                'outer_index': self._read_int32(data, pos + 12),
                'object_name_idx': self._read_int32(data, pos + 16),
                'object_flags': self._read_uint32(data, pos + 20),
                'serial_size': self._read_int64(data, pos + 24),
                'serial_offset': self._read_int64(data, pos + 32),
                'offset': pos
            }

            on_idx = exp['object_name_idx']
            exp['object_name'] = self.names[on_idx] if 0 <= on_idx < len(self.names) else f"idx_{on_idx}"

            self.exports.append(exp)
            pos += 104  # This is approximate, actual size varies

    def find_name_index(self, name: str) -> int:
        """Find the index of a name in the name table"""
        try:
            return self.names.index(name)
        except ValueError:
            return -1

    def add_name(self, name: str) -> int:
        """Add a new name to the name table and return its index"""
        existing = self.find_name_index(name)
        if existing >= 0:
            return existing

        # Calculate where to insert the new name
        # Names are stored as: length (4 bytes) + string (with null) + hash (4 bytes)

        # Create the name entry bytes
        name_bytes = name.encode('utf-8') + b'\x00'
        name_len = len(name_bytes)

        # Simple hash (FNV-1a style, simplified)
        hash_val = 0
        for c in name.lower():
            hash_val = ((hash_val ^ ord(c)) * 0x01000193) & 0xFFFFFFFF

        # Build the entry
        entry = struct.pack('<I', name_len) + name_bytes + struct.pack('<I', hash_val)

        # Insert at the end of the name table
        insert_pos = self.name_table_end
        self.uasset_data[insert_pos:insert_pos] = entry

        # Update counts and offsets
        self.names.append(name)
        new_idx = len(self.names) - 1
        self.name_count += 1
        self.name_table_end += len(entry)

        # Update header
        self._write_int32(self.uasset_data, 41, self.name_count)

        # Shift all offsets that come after the name table
        shift_amount = len(entry)
        self._shift_offsets_after(insert_pos, shift_amount)

        return new_idx

    def _shift_offsets_after(self, position: int, amount: int):
        """Shift all offsets that point to data after the given position"""
        # This is a simplified version - in practice, more offsets need updating

        # Update export offset if needed
        if self.export_offset > position:
            self.export_offset += amount
            self._write_int32(self.uasset_data, 53, self.export_offset)

        # Update import offset if needed
        if self.import_offset > position:
            self.import_offset += amount
            self._write_int32(self.uasset_data, 61, self.import_offset)

    def add_import(self, class_package: str, class_name: str, object_name: str, outer_index: int = 0) -> int:
        """Add a new import entry"""
        # First, ensure the names exist
        cp_idx = self.add_name(class_package)
        cn_idx = self.add_name(class_name)
        on_idx = self.add_name(object_name)

        # Create the import entry (28 bytes)
        entry = struct.pack('<q', cp_idx)  # class_package_idx (8 bytes)
        entry += struct.pack('<q', cn_idx)  # class_name_idx (8 bytes)
        entry += struct.pack('<i', outer_index)  # outer_index (4 bytes)
        entry += struct.pack('<i', on_idx)  # object_name_idx (4 bytes)
        entry += struct.pack('<i', 0)  # padding/additional (4 bytes)

        # Insert at the end of the import table
        insert_pos = self.import_table_end
        self.uasset_data[insert_pos:insert_pos] = entry

        # Update count
        self.import_count += 1
        self._write_int32(self.uasset_data, 57, self.import_count)

        # Track the new import
        new_import = {
            'class_package_idx': cp_idx,
            'class_name_idx': cn_idx,
            'outer_index': outer_index,
            'object_name_idx': on_idx,
            'class_package': class_package,
            'class_name': class_name,
            'object_name': object_name,
            'offset': insert_pos
        }
        self.imports.append(new_import)
        self.import_table_end += len(entry)

        # Return negative index (imports are referenced with negative indices)
        return -(len(self.imports))

    def save(self, output_uasset: Path, output_uexp: Optional[Path] = None):
        """Save the modified asset"""
        with open(output_uasset, 'wb') as f:
            f.write(self.uasset_data)

        if self.uexp_data and output_uexp:
            with open(output_uexp, 'wb') as f:
                f.write(self.uexp_data)

    def print_summary(self):
        """Print a summary of the asset"""
        print(f"Names: {self.name_count}")
        print(f"Imports: {self.import_count}")
        print(f"Exports: {self.export_count}")
        print(f"\nFirst 20 names:")
        for i, name in enumerate(self.names[:20]):
            print(f"  [{i}] {name}")


def patch_inventory_for_sorting():
    """
    Main patching function that adds sorting to the inventory HUD.

    Strategy:
    1. Add necessary name entries for sort-related classes and functions
    2. Add import entries for the sort picker widget
    3. The actual widget hierarchy modification requires more complex changes
       to the export data, which we'll do by copying from the storage chest
    """

    print("=" * 60)
    print("INVENTORY SORT - UASSET PATCHER")
    print("=" * 60)

    # Paths
    inv_uasset = BMSEXPORT_PATH / "UI" / "Inventory" / "UMG_InventoryHUD.uasset"
    inv_uexp = BMSEXPORT_PATH / "UI" / "Inventory" / "UMG_InventoryHUD.uexp"

    out_dir = PRECOOKED_PATH / "UI" / "Inventory"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_uasset = out_dir / "UMG_InventoryHUD.uasset"
    out_uexp = out_dir / "UMG_InventoryHUD.uexp"

    # Make a backup copy first
    print("\n[1] Creating backup and loading asset...")
    shutil.copy2(inv_uasset, out_dir / "UMG_InventoryHUD.uasset.backup")
    shutil.copy2(inv_uexp, out_dir / "UMG_InventoryHUD.uexp.backup")

    # Parse the inventory HUD
    try:
        parser = UAssetParser(inv_uasset, inv_uexp)
        print(f"    Loaded: {inv_uasset.name}")
        print(f"    Names: {parser.name_count}, Imports: {parser.import_count}, Exports: {parser.export_count}")
    except Exception as e:
        print(f"    Error parsing asset: {e}")
        return False

    # Check if already patched
    if parser.find_name_index('UMG_SortSelectionPicker_C') >= 0:
        print("\n[!] Asset already contains sort picker reference - may already be patched")

    # Add the required names for sorting
    print("\n[2] Adding sorting-related names...")
    names_to_add = [
        '/Game/Content_Season3/UI/StorageChest/UMG_SortSelectionPicker',
        'UMG_SortSelectionPicker_C',
        'InventorySort',
        'OnSortChanged',
        'onOptionSelected',
        'SortItems',
        'sortBy',
        'EItemSortMethod',
        'GetSelectedSort',
        'SetInventorySort',
        'ApplySorting',
        'sortMethod',
        'CurrentSortMethod'
    ]

    for name in names_to_add:
        idx = parser.add_name(name)
        print(f"    Added/Found name [{idx}]: {name}")

    # Add import for the sort picker widget class
    print("\n[3] Adding import references...")

    # We need to add imports for the sort picker
    # Import format: ClassPackage, ClassName, ObjectName
    sort_picker_import = parser.add_import(
        '/Game/Content_Season3/UI/StorageChest/UMG_SortSelectionPicker',
        'WidgetBlueprintGeneratedClass',
        'UMG_SortSelectionPicker_C',
        0
    )
    print(f"    Added import for UMG_SortSelectionPicker_C (index: {sort_picker_import})")

    # Save the modified asset
    print("\n[4] Saving modified asset...")
    parser.save(out_uasset, out_uexp)
    print(f"    Saved: {out_uasset}")
    print(f"    Saved: {out_uexp}")

    # Verify the changes
    print("\n[5] Verifying changes...")
    try:
        verify_parser = UAssetParser(out_uasset, out_uexp)
        print(f"    New name count: {verify_parser.name_count}")
        print(f"    New import count: {verify_parser.import_count}")

        # Check for our added names
        for name in names_to_add[:3]:
            idx = verify_parser.find_name_index(name)
            status = "✓" if idx >= 0 else "✗"
            print(f"    {status} {name}")
    except Exception as e:
        print(f"    Warning: Verification failed: {e}")

    print("\n" + "=" * 60)
    print("PATCHING COMPLETE")
    print("=" * 60)
    print("""
NOTE: This patch adds the necessary NAME and IMPORT references for the
sort picker widget. However, the full integration requires additional
modifications to the widget hierarchy and event bindings.

For a complete solution, you'll need to:
1. Use UAssetGUI to add the widget to the visual hierarchy
2. Or use Unreal Editor 4.22 to create a modified blueprint

The patched file is in:
  Precooked/Content/UI/Inventory/UMG_InventoryHUD.uasset

Run package.bat to include it in your mod.
""")

    return True


def main():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     MINECRAFT DUNGEONS - UASSET PATCHER                      ║
    ║     Inventory Sorting Modification                           ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    if not BMSEXPORT_PATH.exists():
        print("ERROR: BmsExport folder not found!")
        print("Please run QuickBMS to extract game files first.")
        return 1

    success = patch_inventory_for_sorting()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
