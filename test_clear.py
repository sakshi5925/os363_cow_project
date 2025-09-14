#!/usr/bin/env python3
"""
Interactive test of COW functionality (Fixed)
"""

from cow_snapshot import CowSnapshotSystem
import os
import shutil

print("🧪 INTERACTIVE COW SNAPSHOT TEST")
print("=" * 40)

# Ask user for disk and block sizes (in KB)
disk_size_kb = int(input("💾 Enter disk size (KB): ").strip())
block_size_kb = int(input("📦 Enter block size (KB): ").strip())

# Convert KB to bytes
disk_size = disk_size_kb * 1024
block_size = block_size_kb * 1024

# Create new system
system = CowSnapshotSystem(disk_size=disk_size_kb, block_size=block_size_kb)
system.format_disk()  # Always start clean

# 1. Write initial data
print("\n1️⃣ Writing initial data...")
block_index = int(input("📍 Enter block index to write: ").strip())
position = block_index * block_size  # convert block index to byte position
initial_data = input("✏️ Enter initial data to write: ").strip()
system.write_data(position, initial_data)
print(f"✅ Initial data written to block {block_index}: '{initial_data}'")

# 2. Take snapshot
print("\n2️⃣ Taking snapshot...")
latency = system.take_snapshot()
print(f"📸 Snapshot taken in {latency:.6f} ms")

# 3. Modify data after snapshot
print("\n3️⃣ Modifying data after snapshot...")
modified_data = input("✏️ Enter modified data to write: ").strip()
system.write_data(position, modified_data)
print(f"✅ Modified data written to block {block_index}: '{modified_data}'")

# 4. Comparison
print("\n4️⃣ COMPARISON:")
read_len = len(initial_data)  # Only read what you wrote
print("   Reading from CURRENT disk:", end=" ")
current = system.read_data(position, read_len)
print(current)

print("   Reading from SNAPSHOT:    ", end=" ")
snapshot = system.read_data(position, read_len, from_snapshot=True)
print(snapshot)

# 5. Verification
print("\n5️⃣ VERIFICATION:")
if initial_data in snapshot and modified_data in current:
    print("   ✅ SUCCESS: Snapshot preserved original data!")
    print("   ✅ SUCCESS: Current disk shows modified data!")
else:
    print("   ❌ TEST FAILED")

# 6. Space usage
print(f"\n6️⃣ SPACE USAGE:")
print(f"   Only {len(system.bitmap)} blocks copied to COW storage")
print(f"   out of {system.disk_size//system.block_size} total blocks")

print("\n🎉 TEST COMPLETED!")

# Cleanup option
storage_dir = "cow_storage"
if os.path.exists(storage_dir):
    choice = input(f"\n🧹 Delete '{storage_dir}' and snapshots? (y/n): ").strip().lower()
    if choice == "y":
        shutil.rmtree(storage_dir)
        print(f"✅ Deleted '{storage_dir}' directory!")
    else:
        print(f"⚠️ Keeping '{storage_dir}' directory.")
