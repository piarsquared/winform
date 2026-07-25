# winform

A Windows-only last resort USB disk recovery utility.

## About

winform is basically a utility which is used to restore USB flash drives that have been left in an unusable state after being written to with tools like Rufus, dd, or other raw disk imaging utilities. When a USB drive is flashed with an image in DD mode (where a filesystem is completely copied to the USB device), Windows may no longer recognize the original partitions or filesystem because of the lack of support or drivers for that respective filesystem. Disk Management may also even show the drive as RAW, unallocated, or otherwise unusable and probably not show at all.

winform attempts to return the device to a normal state by:

- Detecting connected USB storage devices (safely, might I add)
- Wiping existing partition data
- Creating a new partition
- Formatting the drive as NTFS
- Assigning a new drive letter

> [!NOTE]
> I created this software on the latest build of windows which is a bit iffy with GPT partitions. If you are on an earlier (or newer) build it might fuss at this script.
