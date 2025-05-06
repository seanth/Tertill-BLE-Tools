The Tertill weeding robots were made by Franklin Robotics (https://robotsguide.com/robots/tertill). They stopped making the robots in early 2025. I'm attempting to provide some basic tools for people interested in them.

-nRF52832 BLE processor from Nordic
-The devices identify themselves with names like "T1X-nnnn" where n are alphanumeric characters


scanForTertill.py
	This script scan for BLE devices that have names matching T1X-nnnn and will then list the name and address of devices found.

connectToTertill.py
	This script will connect to Tertill devices and return all the information that can be gotten using apps on phones/tablets.
	User and define the address (if known). If run without additional arguments, it will use scanForTertill.py to look for devices to connect to. If multiple devices are found, the user will be given the ability to choose from a list.

In theory there should be ways to send commands to the devices, but I have not worked that out. -STH 2025-0506