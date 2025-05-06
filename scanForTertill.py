#!/usr/bin/env python3
import asyncio
import re
from bleak import BleakScanner

###Tertill weeding robots use a device name of T1X-nnnn where nnnn is any alpha-numeric sequence
###The name returned by the devices does not match the name on the barcode on the bottom of the robot
###Barcode and human readbale might say "T1S-23EB" but the BLE inquery will return "T1X-23EB"

async def scanForDevices():
    print("Scanning for Tertill devices...")
    theDevices = await BleakScanner.discover()
    
    # Pattern for Tertill devices: T1X-nnnn where nnnn is any alpha-numeric sequence
    tertillPattern = re.compile(r"T1X-[0-9A-Za-z]{4}")
    
    tertillList = []
    tertillNames = []
    print("\nTertill devices names and addresses:")
    for aDevice in theDevices:
        if aDevice.name and tertillPattern.match(aDevice.name):
            tertillList.append(aDevice.address)
            tertillNames.append(aDevice.name)
            print("   %s: %s" % (aDevice.name, aDevice.address))
    
    if len(tertillList) == 0:
        print("   No Tertill devices found in scan.")
        
    # Return both addresses and names for more flexibility
    return tertillList, tertillNames

if __name__ == "__main__":
    tertillDevices, tertillNames = asyncio.run(scanForDevices())