#!/usr/bin/env python3
import asyncio
import sys
import logging
from bleak import BleakClient, BleakScanner
from datetime import timedelta
import scanForTertill

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Tertill BLE Characteristics
DEVICE_INFO_SERVICE = "0000180a-0000-1000-8000-00805f9b34fb"
MANUFACTURER_CHAR = "00002a29-0000-1000-8000-00805f9b34fb"
SERIAL_NUMBER_CHAR = "00002a25-0000-1000-8000-00805f9b34fb"
HARDWARE_REV_CHAR = "00002a27-0000-1000-8000-00805f9b34fb"
SOFTWARE_REV_CHAR = "00002a28-0000-1000-8000-00805f9b34fb"

BATTERY_SERVICE = "0000180f-0000-1000-8000-00805f9b34fb"
BATTERY_LEVEL_CHAR = "00002a19-0000-1000-8000-00805f9b34fb"

CUSTOM_SERVICE = "6b690001-bac8-4212-a09f-339ba842c2a5"
BATTERY_VOLTAGE_CHAR = "6b690002-bac8-4212-a09f-339ba842c2a5"
SOLAR_POWER_CHAR = "6b690003-bac8-4212-a09f-339ba842c2a5"
TEMPERATURE_CHAR = "6b690004-bac8-4212-a09f-339ba842c2a5"
SOLAR_VOLTAGE_CHAR = "6b690005-bac8-4212-a09f-339ba842c2a5"
USB_VOLTAGE_CHAR = "6b690006-bac8-4212-a09f-339ba842c2a5"
STATUS_CHAR = "6b690007-bac8-4212-a09f-339ba842c2a5"
#8 = usb charging
#0 = standby
#16 = running

#I actually don't know for sure what these are
VERSION_CHAR = "6b690008-bac8-4212-a09f-339ba842c2a5"
#I suspect this is the build id of the firmware
BUILD_ID_CHAR = "6b690009-bac8-4212-a09f-339ba842c2a5"

ROBOT_TIMES_CHAR = "6b69000a-bac8-4212-a09f-339ba842c2a5"

NORDIC_UART_SERVICE = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
NORDIC_UART_RX_CHAR = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
NORDIC_UART_TX_CHAR = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

def decodeRobotTime(rawData):
    #Decode the robot time from raw data using the 50Hz timer formula.
    #Uses a 50Hz timer tick (20ms per tick) as the base unit.
    #Formula: hours = ticks/100/60/60*2
    theHours = rawData/100/60/60*2
    return theHours

async def findTertillDevice():
    #Scan for Tertill devices and let user select one if multiple are found.
    tertillAddresses, tertillNames = await scanForTertill.scanForDevices()
    
    if not tertillAddresses:
        logger.info("No Tertill devices found in scan.")
        anAddress = input("Enter a Tertill device address manually: ")
        return anAddress
    
    if len(tertillAddresses) == 1:
        logger.info("Found one Tertill device: %s (%s)" % (tertillNames[0], tertillAddresses[0]))
        return tertillAddresses[0]
    
    logger.info("Found %d Tertill devices:" % len(tertillAddresses))
    # Display each device with an index
    for i in range(len(tertillAddresses)):
        aName = tertillNames[i]
        anAddr = tertillAddresses[i]
        print("%d. %s (%s)" % (i+1, aName, anAddr))
    
    while True:
        try:
            selection = int(input("Select a device (1-{}): ".format(len(tertillAddresses))))
            if 1 <= selection <= len(tertillAddresses):
                return tertillAddresses[selection-1]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a number.")

#not working yet. STH 2025-0506
# async def notifyCallback(sender, data):
#     #Handle notifications from BLE characteristics.
#     char_uuid = sender.split(":")[-1].strip()
    
#     if char_uuid == TEMPERATURE_CHAR:
#         temp_celsius = int.from_bytes(data, byteorder='little') / 100
#         logger.info(f"Temperature update: {temp_celsius:.2f}°C")
#     elif char_uuid == BATTERY_LEVEL_CHAR:
#         battery_level = int.from_bytes(data, byteorder='little')
#         logger.info(f"Battery level update: {battery_level}%")
#     else:
#         logger.info(f"Notification from {char_uuid}: {data.hex()}")

async def readTertillData(address=None):
    """Connect to Tertill and read all available data."""
    if not address:
        address = await findTertillDevice()
    
    logger.info("Connecting to Tertill at %s..." % address)
    
    async with BleakClient(address) as client:
        logger.info("Connected to Tertill")
        
        # Read basic device information
        theManufacturer = await client.read_gatt_char(MANUFACTURER_CHAR)
        theSerialNumber = await client.read_gatt_char(SERIAL_NUMBER_CHAR)
        theHWRevision = await client.read_gatt_char(HARDWARE_REV_CHAR)
        theSWRevision = await client.read_gatt_char(SOFTWARE_REV_CHAR)
        
        print("\n=== Device Information ===")
        print("Manufacturer: %s" % theManufacturer.decode())
        print("Serial Number: %s" % theSerialNumber.decode())
        print("Hardware Revision: %s" % theHWRevision.decode())
        print("Software Revision: %s" % theSWRevision.decode())
        
        # Read battery level
        batteryData = await client.read_gatt_char(BATTERY_LEVEL_CHAR)
        # ASCII value to integer (e.g., ']' = 93)
        # Convert battery data to percentage
        if len(batteryData) == 1:
            # If single byte, it's an ASCII character where the value = percentage
            theBatteryPct = ord(batteryData)
        else:
            # Otherwise, convert from bytes to integer
            theBatteryPct = int.from_bytes(batteryData, byteorder='little')
        
        # Read custom service characteristics
        batteryVoltageData = await client.read_gatt_char(BATTERY_VOLTAGE_CHAR)
        solarPowerData = await client.read_gatt_char(SOLAR_POWER_CHAR)
        temperatureData = await client.read_gatt_char(TEMPERATURE_CHAR)
        solarVoltageData = await client.read_gatt_char(SOLAR_VOLTAGE_CHAR)
        usbVoltageData = await client.read_gatt_char(USB_VOLTAGE_CHAR)
        statusData = await client.read_gatt_char(STATUS_CHAR)
        versionData = await client.read_gatt_char(VERSION_CHAR)
        buildIdData = await client.read_gatt_char(BUILD_ID_CHAR)
        robotTimesData = await client.read_gatt_char(ROBOT_TIMES_CHAR)
        
        # Convert data to readable values
        theBatteryVoltage = int.from_bytes(batteryVoltageData, byteorder='little') / 1000
        theSolarPower = int.from_bytes(solarPowerData, byteorder='little') / 1000
        theTemperatureCelsius = int.from_bytes(temperatureData, byteorder='little') / 100
        theSolarVoltage = int.from_bytes(solarVoltageData, byteorder='little') / 1000
        theUsbVoltage = int.from_bytes(usbVoltageData, byteorder='little') / 1000
        theStatus = int.from_bytes(statusData, byteorder='little')
        theVersion = versionData.decode() if len(versionData) > 0 else "Unknown"
        # Check if version data is available
        if len(versionData) > 0:
            theVersion = versionData.decode()
        else:
            theVersion = "Unknown"
        # Decode the build ID data to a string
        if len(buildIdData) > 0:
            theBuildId = buildIdData.decode()
        else:
            theBuildId = "Unknown"
        
        # Decode robot times
        if len(robotTimesData) < 12:
            totalRobotTime = "error"
            drivingTime = "error"
            whackerTime = "error"
        else:
            # Extract times as little-endian 32-bit integers
            totalRobotTime = int.from_bytes(robotTimesData[0:4], byteorder='little')
            totalRobotTime = decodeRobotTime(totalRobotTime)

            drivingTime = int.from_bytes(robotTimesData[4:8], byteorder='little')
            drivingTime = decodeRobotTime(totalRobotTime)

            whackerTime = int.from_bytes(robotTimesData[8:12], byteorder='little')
            whackerTime = decodeRobotTime(totalRobotTime)
        
        print("\n=== Power Information ===")
        print("Battery Level: %d%%" % theBatteryPct)
        print("Battery Voltage: %.2fV" % theBatteryVoltage)
        print("Solar Power: %.2fV" % theSolarPower)
        print("Solar Voltage: %.2fV" % theSolarVoltage)
        print("USB Voltage: %.2fV" % theUsbVoltage)

        print("\n=== Operational Information ===")
        print("Temperature: %.2f°C" % theTemperatureCelsius)
        print("Status Code?: %d" % theStatus)
        print("Version?: %s" % theVersion)
        print("Build ID?: %s" % theBuildId)

        print("\n=== Runtime Information ===")
        print("Total Runtime: (%.2f hours)" % totalRobotTime)
        print("Driving Time: (%.2f hours)" % drivingTime)
        print("Whacker Time: (%.2f hours)" % whackerTime)
                
        # # Monitor for notifications (optional)
        # if input("\nWould you like to monitor for notifications? (y/n): ").lower() == 'y':
        #     logger.info("Setting up notifications...")
            
        #     await client.start_notify(TEMPERATURE_CHAR, notifyCallback)
        #     await client.start_notify(BATTERY_LEVEL_CHAR, notifyCallback)
            
        #     logger.info("Monitoring notifications. Press Ctrl+C to stop.")
        #     try:
        #         await asyncio.sleep(300)  # Monitor for 5 minutes
        #     except asyncio.CancelledError:
        #         pass
        #     finally:
        #         await client.stop_notify(TEMPERATURE_CHAR)
        #         await client.stop_notify(BATTERY_LEVEL_CHAR)
        
        logger.info("Disconnecting from Tertill...")

#not working yet. STH 2025-0506
# async def sendCommand(address, command):
#     #Send a command to the Tertill via Nordic UART.
#     async with BleakClient(address) as client:
#         logger.info("Connected to Tertill, sending command: %s" % command")
        
#         # Convert string to bytes
#         command_bytes = command.encode()
        
#         # Send command via Nordic UART RX characteristic
#         await client.write_gatt_char(NORDIC_UART_RX_CHAR, command_bytes, response=False)
#         logger.info("Command sent successfully")
        
#         # Wait for a response (optional)
#         def uart_rx_callback(sender, data):
#             logger.info("Response received: %s" % data.decode())
        
#         await client.start_notify(NORDIC_UART_TX_CHAR, uart_rx_callback)
#         await asyncio.sleep(5)  # Wait 5 seconds for response
#         await client.stop_notify(NORDIC_UART_TX_CHAR)

async def main():
    """Main function to run the script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Tertill BLE Interface')
    parser.add_argument('--address', '-a', help='BLE address of Tertill device')
    parser.add_argument('--command', '-c', help='Command to send to Tertill')
    
    args = parser.parse_args()
    
    if args.command and args.address:
        await sendCommand(args.address, args.command)
    else:
        await readTertillData(args.address)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Script terminated by user")
    except Exception as e:
        logger.error("Error: %s" % e)