Project: Device-Mapper COW Snapshot Simulator

Abstract

A GUI-based simulator that mimics Linux’s device-mapper snapshot feature using the Copy-on-Write (COW) mechanism.
Snapshots are created instantly (metadata-only), and only modified blocks are copied later, making it fast and space-efficient.
Users can perform write operations, measure snapshot latency, and revert to previous states for data recovery.


Objectives

Simulate a COW snapshot target in a graphical interface.

Create instant, low-latency snapshots.

Efficiently handle write operations using Copy-on-Write logic.

Measure snapshot latency and display it.

Revert to snapshot for easy recovery.




Key Features

Virtual Device Management: Configurable base device and block size.

Instant Snapshots: Metadata-only; latency shown in ms.

COW Storage: Saves only modified blocks.

Dual Views: Read from base or snapshot device.

Revert Feature: Instantly restore device to snapshot state.

Real-Time Status Panel: Shows base, snapshot, and COW usage.



Working Principle
Base Device: virtual_base_device.img acts as a fake disk.

Snapshot Creation: Records block metadata (no data copied).

COW Write: When modifying a block, old data is copied to cow_storage/.

Snapshot Read: Reads old data from COW or base device as needed.

Revert: Restores the device to the saved snapshot version.


How to Run

sudo apt-get install python3-tk -y
Run: python3 test_clear.py
Use GUI to write data, create snapshots, make changes, verify, and revert
