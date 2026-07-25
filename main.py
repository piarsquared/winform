# Winform by piarsquared 7/24/2026

# 1. Get whichever drive has the usb
# 2. We need to get confirmation to write over everything
# 3. We need to actually format the USB drive to NTFS and make it reusable

import os
import wmi
import subprocess
import time
import sys
import textwrap

logo = r"""
         _      ___             
 _    __(_)__  / _/__  ______ _ 
| |/|/ / / _ \/ _/ _ \/ __/  ' \
|__,__/_/_//_/_/ \___/_/ /_/_/_/
"""

def clear_term():
    os.system('cls' if os.name == 'nt' else 'clear')

clear_term()

print(logo)

def beautifier(disks):

    for index, drive in enumerate(disks, start=1):
        print(f"{index}. {drive['Caption']}, {drive['Size']}")

def grab_usb():

    wm = wmi.WMI()
    usb_drives = []

    for disk in wm.Win32_DiskDrive():
        
        if disk.InterfaceType=="USB":

            Size_GB = round(int(disk.Size) / (1024 ** 3))

            usb_drives.append({

                "Caption": disk.Caption, 
                "Model": disk.Model, # Returns same thing as caption most of the time.
                "ID": disk.DeviceID, # you can most likely ignore this for the beautification menu. Important for diskclean.
                "Size": f"{Size_GB}GB",
                "Index": disk.Index

            })

    if usb_drives:

        beautifier(usb_drives)
        return usb_drives
        
    else:
        return "No USB devices detected."



while True:

    drives = grab_usb()

    if isinstance(drives, list):

        try:
            selection = int(input("\nEnter the number of the drive to format: "))

            if selection < 1 or selection > len(drives):
                raise IndexError

            selected_drive = drives[selection - 1]

            last_chance = input("Are you sure you would like to erase ALL data on the device and format it? [y/n] > ").lower()

            if last_chance == "y":

                print("\nPartitioning...")
                target_index = selected_drive["Index"]


                ps_script = f"""$ErrorActionPreference = 'Stop'

$diskNumber = {target_index}

$disk = Get-Disk -Number $diskNumber

if ($disk.BusType -ne "USB") {{
    throw "Refusing to format a non-USB disk."
}}

if ($disk.IsOffline) {{
    Set-Disk -Number $diskNumber -IsOffline $false
}}

if ($disk.IsReadOnly) {{
    Set-Disk -Number $diskNumber -IsReadOnly $false
}}

$diskpartScript = @"
select disk $diskNumber
attributes disk clear readonly noerr
convert gpt
clean
create partition primary
format fs=ntfs quick label=USB
assign
exit
"@

$tempFile = Join-Path $env:TEMP "winform_diskpart.txt"

$diskpartScript | Set-Content $tempFile -Encoding ASCII

diskpart /s $tempFile

$exit = $LASTEXITCODE

Remove-Item $tempFile

if ($exit -ne 0) {{
    throw "DiskPart failed with exit code $exit."
}}

Update-HostStorageCache
Start-Sleep -Seconds 3

$vol = Get-Volume -FileSystemLabel "USB" -ErrorAction SilentlyContinue

if (-not $vol) {{
    throw "DiskPart completed, but no formatted volume was found."
}}

Write-Host ""
Write-Host "`nSuccessfully formatted USB drive."


"""

                try:
                    result = subprocess.run(
                        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                        text=True,
                        capture_output=True,
                        check=True
                    )

                    print(result.stdout)
                    
                    print("\nSuccess! Drive has been formatted to NTFS and is ready to use.")
                    break

                except subprocess.CalledProcessError as e:

                    print("\nPowerShell output:")
                    print(e.stdout)

                    print("\nPowerShell error:")
                    print(e.stderr)

            elif last_chance == "n":
                selection2 = input("Would you like to restart the program? [y/n] > ")

                if selection2 == "y":
                    clear_term()
                    print(logo) 

                else:
                    clear_term()
                    print("Goodbye.")
                    sys.exit()


        except ValueError:
            print("Invalid selection.")
            time.sleep(2)
            clear_term()
            print(logo)

        except IndexError:
            print("Invalid selection.")
            time.sleep(2)
            clear_term()
            print(logo)

    else:
        print("No drives detected. Refreshing in 2s...")
        time.sleep(2)
        clear_term()
        print(logo) 
        drives = grab_usb()