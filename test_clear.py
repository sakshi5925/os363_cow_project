#!/usr/bin/env python3
"""
OS 363 Project: Device-Mapper COW Snapshot Simulator
Team: Gungun Agarwal, Sakshi, Anika Garg
Description: A simulator that implements the core concepts of a Linux device-mapper
             snapshot target using Copy-on-Write (COW).
Version: 3.0 (Final)
"""

import os
import time
import shutil
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

# ==============================================================================
# ## Backend: The Copy-on-Write System Logic
# ==============================================================================

class CowSnapshotSystem:
    def __init__(self, disk_size_kb=1024, block_size_kb=64):
        """Initialize the COW snapshot system"""
        self.disk_size = disk_size_kb * 1024
        self.block_size = block_size_kb * 1024
        self.base_device_file = "virtual_base_device.img"
        self.cow_dir = "cow_storage"
        self.cow_bitmap = {}
        self.snapshot_protected_blocks = None
        self.live_blocks = set()
        self.snapshot_time = None
        
        Path(self.cow_dir).mkdir(exist_ok=True)
        self.format_disk()
    
    def format_disk(self):
        """Formats the base device and clears COW storage."""
        for f in os.listdir(self.cow_dir):
            try:
                os.remove(os.path.join(self.cow_dir, f))
            except OSError:
                pass
            
        with open(self.base_device_file, 'wb') as f:
            f.write(b'\x00' * self.disk_size)
            
        self.cow_bitmap.clear()
        self.live_blocks.clear()
        self.snapshot_protected_blocks = None
        self.snapshot_time = None

    def take_snapshot(self):
        """Creates an instant, metadata-only snapshot of the base device."""
        start = time.perf_counter()
        self.snapshot_protected_blocks = self.live_blocks.copy()
        self.cow_bitmap.clear()
        self.snapshot_time = time.time()
        latency = (time.perf_counter() - start) * 1000
        return latency

    def write_data(self, block_index, data):
        """Appends data with a space to the end of existing content in a block."""
        block_id = block_index
        block_start = block_id * self.block_size
        
        # 1. Read the existing block to find the end of the data.
        with open(self.base_device_file, 'rb') as f:
            f.seek(block_start)
            block_content = f.read(self.block_size)
        
        existing_data = block_content.rstrip(b'\x00')
        
        # 2. Prepare the new data and calculate the append position.
        if existing_data:
            # If there's data, add a space before appending the new data.
            data_to_write = b" " + data.encode()
            append_position = block_start + len(existing_data)
        else:
            # If the block is empty, just write the new data from the start.
            data_to_write = data.encode()
            append_position = block_start

        # 3. Check if the new data will fit in the block.
        if len(existing_data) + len(data_to_write) > self.block_size:
            messagebox.showerror("Error", f"Not enough space in block {block_id} to append data.")
            return

        # Perform COW check before modifying the block
        if (self.snapshot_protected_blocks is not None and
                block_id in self.snapshot_protected_blocks and
                block_id not in self.cow_bitmap):
            
            original_data = block_content
            timestamp = int(time.time() * 1000)
            fname = f"{self.cow_dir}/block_{block_id}_{timestamp}.cow"
            with open(fname, 'wb') as f:
                f.write(original_data)
            self.cow_bitmap[block_id] = fname

        # 4. Write the new data at the calculated append position.
        with open(self.base_device_file, 'r+b') as f:
            f.seek(append_position)
            f.write(data_to_write)
            f.flush()
            os.fsync(f.fileno())
            
        self.live_blocks.add(block_id)

    def read_data(self, position, length, from_snapshot=False):
        """Reads data from the live base device or the virtual snapshot device."""
        result = bytearray(length)
        bytes_actually_read = 0
        
        bytes_to_process = length
        current_offset = 0

        while bytes_to_process > 0:
            current_pos = position + current_offset
            if current_pos >= self.disk_size: break

            block_id = current_pos // self.block_size
            offset_in_block = current_pos % self.block_size
            
            bytes_to_read_in_chunk = min(bytes_to_process, self.block_size - offset_in_block)
            data_chunk = None

            if from_snapshot:
                if self.snapshot_protected_blocks is None: break
                
                if block_id in self.cow_bitmap:
                    with open(self.cow_bitmap[block_id], 'rb') as f:
                        f.seek(offset_in_block)
                        data_chunk = f.read(bytes_to_read_in_chunk)
                elif block_id in self.snapshot_protected_blocks:
                    with open(self.base_device_file, 'rb') as f:
                        f.seek(current_pos)
                        data_chunk = f.read(bytes_to_read_in_chunk)
                else:
                    data_chunk = b'\x00' * bytes_to_read_in_chunk
            else:
                with open(self.base_device_file, 'rb') as f:
                    f.seek(current_pos)
                    data_chunk = f.read(bytes_to_read_in_chunk)

            if not data_chunk: break

            result[current_offset:current_offset + len(data_chunk)] = data_chunk
            bytes_actually_read += len(data_chunk)
            bytes_to_process -= bytes_to_read_in_chunk
            current_offset += bytes_to_read_in_chunk

        return result[:bytes_actually_read].decode(errors='ignore').rstrip('\x00')

# ==============================================================================
# ## Frontend: The Tkinter GUI Application
# ==============================================================================

class CowGuiApp:
    def __init__(self, root):
        self.version = "3.0 (Final)" # Version number for verification
        self.root = root
        self.root.title(f"Device-Mapper COW Simulator - v{self.version}")
        self.system = None
        self.create_widgets()
        self.init_disk()

    def create_widgets(self):
        style = ttk.Style(self.root)
        style.theme_use('clam')
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)

        disk_frame = ttk.LabelFrame(main_frame, text="⚙️ Device Setup")
        disk_frame.pack(fill="x", pady=5)
        ttk.Label(disk_frame, text="Base Device Size (KB):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.disk_entry = ttk.Entry(disk_frame, width=10)
        self.disk_entry.grid(row=0, column=1, padx=5, pady=5)
        self.disk_entry.insert(0, "1024")
        ttk.Label(disk_frame, text="Block Size (KB):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.block_entry = ttk.Entry(disk_frame, width=10)
        self.block_entry.grid(row=0, column=3, padx=5, pady=5)
        self.block_entry.insert(0, "64")
        ttk.Button(disk_frame, text="Initialize / Format", command=self.init_disk).grid(row=0, column=4, padx=10, pady=5)

        write_frame = ttk.LabelFrame(main_frame, text="✏️ Append to Block")
        write_frame.pack(fill="x", pady=5)
        ttk.Label(write_frame, text="Block Index:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.write_block_entry = ttk.Entry(write_frame, width=8)
        self.write_block_entry.grid(row=0, column=1, padx=5, pady=5)
        self.write_block_entry.insert(0, "0")
        ttk.Label(write_frame, text="Data to Append:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.write_data_entry = ttk.Entry(write_frame, width=40)
        self.write_data_entry.grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(write_frame, text="Append", command=self.write_data).grid(row=0, column=4, padx=10, pady=5)

        snapshot_frame = ttk.LabelFrame(main_frame, text="📸 Snapshot Control")
        snapshot_frame.pack(fill="x", pady=5)
        ttk.Button(snapshot_frame, text="Create Instant Snapshot", command=self.take_snapshot).pack(side="left", padx=5, pady=5)
        self.snapshot_label = ttk.Label(snapshot_frame, text="No snapshot active", font=('Segoe UI', 9, 'italic'))
        self.snapshot_label.pack(side="left", padx=10)

        read_frame = ttk.LabelFrame(main_frame, text="📖 Read Data")
        read_frame.pack(fill="x", pady=5)
        ttk.Label(read_frame, text="Block Index:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.read_block_entry = ttk.Entry(read_frame, width=8)
        self.read_block_entry.grid(row=0, column=1, padx=5, pady=5)
        self.read_block_entry.insert(0, "0")
        ttk.Label(read_frame, text="Length:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.read_len_entry = ttk.Entry(read_frame, width=8)
        self.read_len_entry.grid(row=0, column=3, padx=5, pady=5)
        self.read_len_entry.insert(0, "100")
        self.read_from_snapshot = tk.BooleanVar()
        ttk.Checkbutton(read_frame, text="Read from Snapshot Device", variable=self.read_from_snapshot).grid(row=0, column=4, padx=10, pady=5)
        ttk.Button(read_frame, text="Read", command=self.read_data).grid(row=0, column=5, padx=10, pady=5)

        self.read_output = tk.Text(main_frame, height=3, relief="sunken", borderwidth=1, background="#f0f0f0")
        self.read_output.pack(fill="x", pady=5)

        status_frame = ttk.LabelFrame(main_frame, text="📊 System Status")
        status_frame.pack(fill="x", pady=5)
        self.status_text = tk.Text(status_frame, height=4, relief="sunken", borderwidth=1, background="#f0f0f0")
        self.status_text.pack(fill="x", padx=5, pady=5)
        
        status_bar = ttk.Frame(main_frame, relief="sunken")
        status_bar.pack(side="bottom", fill="x", pady=(10, 0))
        ttk.Label(status_bar, text=f"Version: {self.version}").pack(side="left", padx=5)

    def init_disk(self):
        try:
            disk_size = int(self.disk_entry.get())
            block_size = int(self.block_entry.get())
            self.system = CowSnapshotSystem(disk_size, block_size)
            messagebox.showinfo("Success", "Base device and COW storage have been initialized.")
            self.snapshot_label.config(text="No snapshot active")
            self.update_status()
        except ValueError:
            messagebox.showerror("Error", "Device and block sizes must be integers.")
        except Exception as e:
            messagebox.showerror("Error", f"An initialization error occurred: {e}")

    def write_data(self):
        if not self.system: return
        try:
            block_index = int(self.write_block_entry.get())
            data = self.write_data_entry.get()
            self.system.write_data(block_index, data)
            self.update_status()
            self.write_data_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Block index must be an integer.")
        except Exception as e:
            messagebox.showerror("Error", f"A write error occurred: {e}")

    def take_snapshot(self):
        if not self.system: return
        latency = self.system.take_snapshot()
        self.snapshot_label.config(text=f"Snapshot Active (Creation Latency: {latency:.4f} ms)")
        messagebox.showinfo("Snapshot Created", f"Virtual snapshot device is now active.\nCreation latency: {latency:.4f} ms")
        self.update_status()

    def read_data(self):
        if not self.system: return
        try:
            block_index = int(self.read_block_entry.get())
            length = int(self.read_len_entry.get())
            position = block_index * self.system.block_size
            if not (0 <= position < self.system.disk_size):
                messagebox.showerror("Error", "Read position is outside the device bounds.")
                return
            source = "Snapshot Device" if self.read_from_snapshot.get() else "Base Device"
            data = self.system.read_data(position, length, from_snapshot=self.read_from_snapshot.get())
            self.read_output.delete("1.0", tk.END)
            self.read_output.insert("1.0", f"--- Data from {source} ---\n")
            self.read_output.insert(tk.END, data)
        except ValueError:
            messagebox.showerror("Error", "Block index and length must be integers.")
        except Exception as e:
            messagebox.showerror("Error", f"A read error occurred: {e}")

    def update_status(self):
        """Updates the status panel with device-mapper terminology."""
        if not self.system: return
        self.status_text.delete("1.0", tk.END)
        
        is_snap_active = self.system.snapshot_protected_blocks is not None
        snap_status = "Active" if is_snap_active else "Inactive"
        
        lines = [
            f"Base Device: '{self.system.base_device_file}' ({self.system.disk_size // 1024} KB)",
            f"COW Storage: {len(self.system.cow_bitmap)} modified block(s) stored.",
            f"Snapshot Device: {snap_status}",
        ]
        self.status_text.insert(tk.END, "\n".join(lines))

if __name__ == "__main__":
    root = tk.Tk()
    app = CowGuiApp(root)
    root.mainloop()