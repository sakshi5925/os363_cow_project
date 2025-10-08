# """
# Interactive test of COW functionality
# """

# from cow_snapshot import CowSnapshotSystem
# import os
# import shutil

# print("🧪 INTERACTIVE COW SNAPSHOT TEST")
# print("=" * 40)

# disk_size_kb = int(input("💾 Enter disk size (KB): ").strip())
# block_size_kb = int(input("📦 Enter block size (KB): ").strip())

# system = CowSnapshotSystem(disk_size_kb, block_size_kb)
# system.format_disk()

# # 1️⃣ Write initial data
# print("\n1️⃣ Writing initial data...")
# block_index = int(input("📍 Enter block index to write: ").strip())
# position = block_index * system.block_size
# initial_data = input("✏️ Enter initial data to write: ").strip()
# system.write_data(position, initial_data)
# print(f"✅ Initial data written to block {block_index}: '{initial_data}'")

# # 2️⃣ Take snapshot
# print("\n2️⃣ Taking snapshot...")
# latency = system.take_snapshot()
# print(f"📸 Snapshot taken in {latency:.6f} ms")

# # 3️⃣ Modify data
# print("\n3️⃣ Modifying data after snapshot...")
# modified_data = input("✏️ Enter modified data to write: ").strip()
# system.write_data(position, modified_data)
# print(f"✅ Modified data written to block {block_index}: '{modified_data}'")

# # 4️⃣ Comparison
# print("\n4️⃣ COMPARISON:")
# current = system.read_data(position, max(len(initial_data), len(modified_data)))
# snapshot = system.read_data(position, len(initial_data), from_snapshot=True)

# print(f"   Current disk: '{current}'")
# print(f"   Snapshot:     '{snapshot}'")

# # 5️⃣ Verification
# print("\n5️⃣ VERIFICATION:")
# if snapshot == initial_data and current == modified_data:
#     print("   ✅ SUCCESS: Snapshot preserved original data!")
#     print("   ✅ SUCCESS: Current disk shows modified data!")
# else:
#     print("   ❌ TEST FAILED")

# # 6️⃣ Space usage
# print(f"\n6️⃣ SPACE USAGE:")
# print(f"   Only {len(system.bitmap)} blocks copied to COW storage")
# print(f"   out of {system.disk_size // system.block_size} total blocks")

# # Cleanup
# storage_dir = "cow_storage"
# if os.path.exists(storage_dir):
#     choice = input(f"\n🧹 Delete '{storage_dir}' and snapshots? (y/n): ").strip().lower()
#     if choice == "y":
#         shutil.rmtree(storage_dir)
#         print(f"✅ Deleted '{storage_dir}' directory!")
#     else:
#         print(f"⚠️ Keeping '{storage_dir}' directory.")

# print("\n🎉 TEST COMPLETED!")


import tkinter as tk
from tkinter import ttk, messagebox
from cow_snapshot import CowSnapshotSystem
import os
import shutil

class CowGuiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("COW Snapshot Simulator")
        self.system = None
        
        self.create_widgets()

    def create_widgets(self):
        # Disk Settings Frame
        disk_frame = ttk.LabelFrame(self.root, text="Disk Settings")
        disk_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(disk_frame, text="Disk Size (KB):").grid(row=0, column=0, padx=5)
        self.disk_entry = ttk.Entry(disk_frame, width=10)
        self.disk_entry.grid(row=0, column=1, padx=5)
        self.disk_entry.insert(0, "1024")

        ttk.Label(disk_frame, text="Block Size (KB):").grid(row=0, column=2, padx=5)
        self.block_entry = ttk.Entry(disk_frame, width=10)
        self.block_entry.grid(row=0, column=3, padx=5)
        self.block_entry.insert(0, "64")

        ttk.Button(disk_frame, text="Initialize Disk", command=self.init_disk).grid(row=0, column=4, padx=5)

        # Write Data Frame
        write_frame = ttk.LabelFrame(self.root, text="Write Data")
        write_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(write_frame, text="Block Index:").grid(row=0, column=0, padx=5)
        self.write_block_entry = ttk.Entry(write_frame, width=5)
        self.write_block_entry.grid(row=0, column=1, padx=5)

        ttk.Label(write_frame, text="Data:").grid(row=0, column=2, padx=5)
        self.write_data_entry = ttk.Entry(write_frame, width=30)
        self.write_data_entry.grid(row=0, column=3, padx=5)

        ttk.Button(write_frame, text="Write", command=self.write_data).grid(row=0, column=4, padx=5)

        # Snapshot Frame
        snapshot_frame = ttk.LabelFrame(self.root, text="Snapshot")
        snapshot_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(snapshot_frame, text="Take Snapshot", command=self.take_snapshot).pack(side="left", padx=5)
        self.snapshot_label = ttk.Label(snapshot_frame, text="No snapshot yet")
        self.snapshot_label.pack(side="left", padx=10)

        # Read Data Frame
        read_frame = ttk.LabelFrame(self.root, text="Read Data")
        read_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(read_frame, text="Block Index:").grid(row=0, column=0, padx=5)
        self.read_block_entry = ttk.Entry(read_frame, width=5)
        self.read_block_entry.grid(row=0, column=1, padx=5)

        ttk.Label(read_frame, text="Length:").grid(row=0, column=2, padx=5)
        self.read_len_entry = ttk.Entry(read_frame, width=5)
        self.read_len_entry.grid(row=0, column=3, padx=5)

        self.read_from_snapshot = tk.BooleanVar()
        ttk.Checkbutton(read_frame, text="Read from Snapshot", variable=self.read_from_snapshot).grid(row=0, column=4, padx=5)

        ttk.Button(read_frame, text="Read", command=self.read_data).grid(row=0, column=5, padx=5)

        self.read_output = tk.Text(self.root, height=5)
        self.read_output.pack(fill="x", padx=10, pady=5)

        # Status Frame
        status_frame = ttk.LabelFrame(self.root, text="System Status")
        status_frame.pack(fill="x", padx=10, pady=5)
        self.status_text = tk.Text(status_frame, height=6)
        self.status_text.pack(fill="x", padx=5, pady=5)

        # Cleanup Button
        ttk.Button(self.root, text="Cleanup COW Storage", command=self.cleanup).pack(pady=5)

    def init_disk(self):
        disk_size = int(self.disk_entry.get())
        block_size = int(self.block_entry.get())
        self.system = CowSnapshotSystem(disk_size, block_size)
        self.system.format_disk()
        messagebox.showinfo("Info", "Disk initialized successfully!")
        self.update_status()

    def write_data(self):
        if not self.system:
            messagebox.showerror("Error", "Initialize the disk first!")
            return
        block_index = int(self.write_block_entry.get())
        data = self.write_data_entry.get()
        position = block_index * self.system.block_size
        self.system.write_data(position, data)
        messagebox.showinfo("Info", f"Data written to block {block_index}")
        self.update_status()

    def take_snapshot(self):
        if not self.system:
            messagebox.showerror("Error", "Initialize the disk first!")
            return
        latency = self.system.take_snapshot()
        self.snapshot_label.config(text=f"Snapshot taken ({latency:.2f} ms)")
        messagebox.showinfo("Snapshot", f"Snapshot created in {latency:.2f} ms")
        self.update_status()

    def read_data(self):
        if not self.system:
            messagebox.showerror("Error", "Initialize the disk first!")
            return
        block_index = int(self.read_block_entry.get())
        length = int(self.read_len_entry.get())
        position = block_index * self.system.block_size
        data = self.system.read_data(position, length, from_snapshot=self.read_from_snapshot.get())
        self.read_output.delete("1.0", tk.END)
        self.read_output.insert(tk.END, data)

    def update_status(self):
        if not self.system:
            return
        self.status_text.delete("1.0", tk.END)
        lines = [
            f"Disk Size: {self.system.disk_size // 1024} KB",
            f"Block Size: {self.system.block_size // 1024} KB",
            f"Blocks copied to COW: {len(self.system.bitmap)}",
            f"Snapshot active: {'Yes' if self.system.snapshot_bitmap else 'No'}",
            f"Disk file preview (first 50 bytes):"
        ]
        try:
            with open(self.system.disk_file, 'rb') as f:
                content = f.read(50)
            lines.append(content.decode(errors='ignore').strip())
        except:
            lines.append("(binary data)")
        self.status_text.insert(tk.END, "\n".join(lines))

    def cleanup(self):
        if os.path.exists("cow_storage"):
            shutil.rmtree("cow_storage")
        if self.system:
            self.system.bitmap.clear()
            self.system.snapshot_bitmap = None
        messagebox.showinfo("Cleanup", "COW storage cleared!")
        self.update_status()

if __name__ == "__main__":
    root = tk.Tk()
    app = CowGuiApp(root)
    root.mainloop()
