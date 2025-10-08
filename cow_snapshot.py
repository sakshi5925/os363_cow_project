# #!/usr/bin/env python3
# """
# OS 363 Project: Copy-on-Write Snapshot Simulator
# Team: Gungun Agarwal, Sakshi, Anika Garg
# """

# import os
# import time
# from pathlib import Path

# class CowSnapshotSystem:
#     def __init__(self, disk_size=1024, block_size=64):
#         """Initialize the COW snapshot system"""
#         self.disk_size = disk_size * 1024  # Size in bytes
#         self.block_size = block_size * 1024  # Block size in bytes
#         self.disk_file = "virtual_disk.img"
#         self.cow_dir = "cow_storage"
#         self.bitmap = {}  # Tracks which blocks have been copied
#         self.snapshot_time = None
#         self.snapshot_bitmap = None
#         self.initialized_blocks = set()  # Track initialized blocks
#         self.initialize_system()
    
#     def initialize_system(self):
#         """Set up the initial virtual environment"""
#         Path(self.cow_dir).mkdir(exist_ok=True)
#         if not os.path.exists(self.disk_file):
#             print(f"Creating virtual disk ({self.disk_size//1024} KB)...")
#             with open(self.disk_file, 'wb') as f:
#                 f.write(b'\x00' * self.disk_size)
#             print("✓ Virtual disk created successfully!")
    
#     def format_disk(self):
#         """Format the virtual disk"""
#         with open(self.disk_file, 'wb') as f:
#             f.write(b'\x00' * self.disk_size)
#         self.bitmap = {}
#         self.snapshot_bitmap = None
#         self.initialized_blocks.clear()
#         print("✓ Virtual disk formatted!")

#     def take_snapshot(self):
#         """Take an instant snapshot"""
#         start_time = time.time()
#         self.snapshot_bitmap = {}

#         # Save the state of all blocks
#         for block_id in range(self.disk_size // self.block_size):
#             block_start = block_id * self.block_size
#             with open(self.disk_file, 'rb') as f:
#                 f.seek(block_start)
#                 block_data = f.read(self.block_size)

#             if block_data.strip(b'\x00'):  # Only save non-empty blocks
#                 timestamp = int(time.time() * 1000)
#                 cow_filename = f"{self.cow_dir}/block_{block_id}_{timestamp}.cow"
#                 with open(cow_filename, 'wb') as f:
#                     f.write(block_data)
#                 self.snapshot_bitmap[block_id] = cow_filename

#         self.snapshot_time = time.time()
#         latency_ms = (self.snapshot_time - start_time) * 1000

#         print("✓ Snapshot created successfully!")
#         print(f"  Latency: {latency_ms:.6f} milliseconds")
#         print("  Data at snapshot stored for COW reads")
#         return latency_ms

#     def write_data(self, position, data):
#         """Write data to disk using Copy-on-Write"""
#         print(f"\nWriting data at position {position}...")

#         block_id = position // self.block_size
#         block_start = block_id * self.block_size

#         # Trigger Copy-on-Write if snapshot exists and block not yet copied
#         if self.snapshot_bitmap and block_id not in self.bitmap:
#             print(f"  Copy-on-Write triggered for block {block_id}")
#             with open(self.disk_file, 'rb') as f:
#                 f.seek(block_start)
#                 original_data = f.read(self.block_size)

#             timestamp = int(time.time() * 1000)
#             cow_filename = f"{self.cow_dir}/block_{block_id}_{timestamp}.cow"
#             with open(cow_filename, 'wb') as f:
#                 f.write(original_data)

#             self.bitmap[block_id] = cow_filename
#             print(f"  ✓ Original data saved to: {cow_filename}")

#         # Write new data to disk
#         with open(self.disk_file, 'r+b') as f:
#             f.seek(block_start)
#              # fill the block with zeros first
#             f.write(b'\x00' * self.block_size)
#             f.seek(position)
#             f.write(data.encode())
#         print(f"  ✓ New data written to disk")
#         print(f"  Data written: '{data}'")

#     def read_data(self, position, length, from_snapshot=False):
#         """Read data from disk or snapshot"""
#         source = "snapshot" if from_snapshot else "current disk"
#         print(f"\nReading {length} bytes from position {position} ({source})...")

#         if from_snapshot:
#             if self.snapshot_bitmap is None:
#                 print("  ❌ No snapshot exists! Reading current disk instead.")
#                 return self.read_data(position, length, from_snapshot=False)

#             result = b''
#             current_pos = position
#             bytes_remaining = length

#             while bytes_remaining > 0:
#                 block_id = current_pos // self.block_size
#                 block_start = block_id * self.block_size
#                 offset_in_block = current_pos - block_start
#                 bytes_to_read = min(self.block_size - offset_in_block, bytes_remaining)

#                 if block_id in self.snapshot_bitmap:
#                     with open(self.snapshot_bitmap[block_id], 'rb') as f:
#                         f.seek(offset_in_block)
#                         data_chunk = f.read(bytes_to_read)
#                 else:
#                     with open(self.disk_file, 'rb') as f:
#                         f.seek(current_pos)
#                         data_chunk = f.read(bytes_to_read)

#                 result += data_chunk
#                 current_pos += len(data_chunk)
#                 bytes_remaining -= len(data_chunk)

#             print(f"  Data from snapshot: '{result.decode()}'")
#             return result.decode()
#         else:
#             with open(self.disk_file, 'rb') as f:
#                 f.seek(position)
#                 data = f.read(length)
#             print(f"  Data from current disk: '{data.decode()}'")
#             return data.decode()

#     def show_status(self):
#         """Show system status"""
#         print("\n" + "="*60)
#         print("SYSTEM STATUS:")
#         print(f"Virtual Disk: {self.disk_file} ({self.disk_size//1024} KB)")
#         print(f"Block Size: {self.block_size//1024} KB")
#         print(f"COW Storage: {len(os.listdir(self.cow_dir))} blocks saved")
#         print(f"Current blocks tracked: {list(self.bitmap.keys())}")
#         if self.snapshot_bitmap is not None:
#             print(f"Snapshot blocks tracked: {list(self.snapshot_bitmap.keys())}")
#         try:
#             with open(self.disk_file, 'rb') as f:
#                 content = f.read(50)
#             print(f"Disk content starts with: '{content.decode().strip()}'")
#         except:
#             print("Disk content: (binary data)")
#         if self.snapshot_time:
#             print(f"Snapshot active (taken at: {time.ctime(self.snapshot_time)})")
#         print("="*60)


# def run_demo():
#     """Demo of the system"""
#     print("🐮 OS 363 - Copy-on-Write Snapshot Simulator")
#     print("=============================================")
#     print("Team: Gungun Agarwal, Sakshi, Anika Garg\n")

#     cow_system = CowSnapshotSystem(disk_size=1024, block_size=64)
#     cow_system.show_status()

#     print("\n2. Writing initial data...")
#     cow_system.write_data(0, "Operating Systems Project 363 - Initial Data!")
#     cow_system.write_data(50, "This is our COW implementation.")
#     cow_system.show_status()

#     print("\n3. Taking snapshot...")
#     latency = cow_system.take_snapshot()
#     cow_system.show_status()

#     print("\n4. Modifying data after snapshot...")
#     cow_system.write_data(0, "MODIFIED: New data after snapshot!")
#     cow_system.write_data(100, "Additional new data written after snapshot.")
#     cow_system.show_status()

#     print("\n5. Demonstrating reads...")
#     print("\nCurrent disk:")
#     cow_system.read_data(0, 40)
#     print("\nSnapshot:")
#     cow_system.read_data(0, 40, from_snapshot=True)

#     print("\n" + "="*60)
#     print("RESULTS:")
#     print(f"Snapshot latency: {latency:.6f} ms")
#     print(f"Blocks in COW: {len(cow_system.bitmap)}")
#     print("="*60)
#     print("\n✅ PROJECT COMPLETED SUCCESSFULLY!")


# if __name__ == "__main__":
#     run_demo()


#!/usr/bin/env python3
#!/usr/bin/env python3
"""
OS 363 Project: Advanced Copy-on-Write Snapshot Simulator
Team: Gungun Agarwal, Sakshi, Anika Garg
"""

import os
import time
from pathlib import Path
from colorama import init, Fore, Style

init(autoreset=True)  # Auto-reset color after each print

class CowSnapshotSystem:
    def __init__(self, disk_size_kb=1024, block_size_kb=64):
        """Initialize the COW snapshot system"""
        self.disk_size = disk_size_kb * 1024
        self.block_size = block_size_kb * 1024
        self.disk_file = "virtual_disk.img"
        self.cow_dir = "cow_storage"
        self.bitmap = {}
        self.snapshot_bitmap = None
        self.snapshot_time = None
        Path(self.cow_dir).mkdir(exist_ok=True)
        if not os.path.exists(self.disk_file):
            self.format_disk()
    
    def format_disk(self):
        """Format the virtual disk"""
        with open(self.disk_file, 'wb') as f:
            f.write(b'\x00' * self.disk_size)
        self.bitmap.clear()
        self.snapshot_bitmap = None
        print(Fore.GREEN + f"\n✓ Virtual disk formatted ({self.disk_size//1024} KB)!\n" + Style.RESET_ALL)

    def take_snapshot(self):
        """Take a snapshot of all non-empty blocks"""
        start = time.time()
        self.snapshot_bitmap = {}
        for block_id in range(self.disk_size // self.block_size):
            start_pos = block_id * self.block_size
            with open(self.disk_file, 'rb') as f:
                f.seek(start_pos)
                block_data = f.read(self.block_size)
            if block_data.strip(b'\x00'):
                timestamp = int(time.time() * 1000)
                fname = f"{self.cow_dir}/block_{block_id}_{timestamp}.cow"
                with open(fname, 'wb') as f:
                    f.write(block_data)
                self.snapshot_bitmap[block_id] = fname
        latency = (time.time() - start) * 1000
        self.snapshot_time = time.time()
        print(Fore.CYAN + f"🐮 Snapshot created successfully! Latency: {latency:.6f} ms\n" + Style.RESET_ALL)
        return latency

    def write_data(self, position, data):
        """Write data to disk using Copy-on-Write"""
        block_id = position // self.block_size
        block_start = block_id * self.block_size

        if self.snapshot_bitmap and block_id not in self.bitmap:
            # Copy-on-Write triggered
            with open(self.disk_file, 'rb') as f:
                f.seek(block_start)
                original_data = f.read(self.block_size)
            timestamp = int(time.time() * 1000)
            fname = f"{self.cow_dir}/block_{block_id}_{timestamp}.cow"
            with open(fname, 'wb') as f:
                f.write(original_data)
            self.bitmap[block_id] = fname
            print(Fore.MAGENTA + f"💾 Copy-on-Write triggered for block {block_id}")
            print(Fore.YELLOW + f"  ✓ Original data saved to: {fname}" + Style.RESET_ALL)

        # Clear block and write new data
        with open(self.disk_file, 'r+b') as f:
            f.seek(block_start)
            f.write(b'\x00' * self.block_size)
            f.seek(position)
            f.write(data.encode())
        print(Fore.GREEN + f"📝 New data written to disk: '{data}'\n" + Style.RESET_ALL)

    def read_data(self, position, length, from_snapshot=False):
        """Read data from disk or snapshot"""
        result = b''
        bytes_remaining = length
        current_pos = position

        while bytes_remaining > 0:
            block_id = current_pos // self.block_size
            block_start = block_id * self.block_size
            offset = current_pos - block_start
            read_len = min(self.block_size - offset, bytes_remaining)

            if from_snapshot and self.snapshot_bitmap and block_id in self.snapshot_bitmap:
                with open(self.snapshot_bitmap[block_id], 'rb') as f:
                    f.seek(offset)
                    chunk = f.read(read_len)
            else:
                with open(self.disk_file, 'rb') as f:
                    f.seek(current_pos)
                    chunk = f.read(read_len)

            result += chunk
            current_pos += len(chunk)
            bytes_remaining -= len(chunk)

        data_str = result.decode().rstrip('\x00')
        source = "Snapshot" if from_snapshot else "Current Disk"
        color = Fore.CYAN if from_snapshot else Fore.LIGHTGREEN_EX
        print(color + f"📖 Read from {source}: '{data_str}'\n" + Style.RESET_ALL)
        return data_str

    def show_status(self):
        """Show system status in coding-style visual"""
        print(Fore.BLUE + "\n" + "="*60)
        print("💻 COW Snapshot System Status")
        print("="*60)
        print(Fore.YELLOW + f"Virtual Disk: {self.disk_file} ({self.disk_size//1024} KB)")
        print(f"Block Size: {self.block_size//1024} KB")
        print(f"COW Storage Blocks: {len(os.listdir(self.cow_dir))}")
        print(f"Current copied blocks: {list(self.bitmap.keys())}")
        if self.snapshot_bitmap:
            print(f"Snapshot blocks: {list(self.snapshot_bitmap.keys())}")
        if self.snapshot_time:
            print(f"Snapshot active at: {time.ctime(self.snapshot_time)}")
        print("="*60 + Style.RESET_ALL)


def interactive_demo():
    """Interactive demo with user input"""
    cow = CowSnapshotSystem(disk_size_kb=512, block_size_kb=32)
    print(Fore.CYAN + "\n🐮 Welcome to Advanced COW Snapshot Simulator!" + Style.RESET_ALL)

    while True:
        print(Fore.LIGHTWHITE_EX + "\nChoose an action:")
        print("1️⃣  Write Data")
        print("2️⃣  Read Data")
        print("3️⃣  Take Snapshot")
        print("4️⃣  Show Status")
        print("5️⃣  Format Disk")
        print("6️⃣  Exit\n" + Style.RESET_ALL)

        choice = input(Fore.LIGHTYELLOW_EX + "Enter choice: " + Style.RESET_ALL)
        if choice == '1':
            pos = int(input("Position to write: "))
            data = input("Data to write: ")
            cow.write_data(pos, data)
        elif choice == '2':
            pos = int(input("Position to read: "))
            length = int(input("Number of bytes: "))
            snap = input("Read from snapshot? (y/n): ").lower() == 'y'
            cow.read_data(pos, length, from_snapshot=snap)
        elif choice == '3':
            cow.take_snapshot()
        elif choice == '4':
            cow.show_status()
        elif choice == '5':
            cow.format_disk()
        elif choice == '6':
            print(Fore.LIGHTMAGENTA_EX + "Exiting... Bye!" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "❌ Invalid choice!" + Style.RESET_ALL)


if __name__ == "__main__":
    interactive_demo()
