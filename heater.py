"""Simple script to control the Heater dev env device."""
import asyncio
import sys
from kasa import Discover

DEVICE_NAME = "Heater dev env"

async def find_device():
    """Discover and return the heater device."""
    devices = await Discover. discover()
    for dev in devices.values():
        await dev. update()
        if dev.alias == DEVICE_NAME: 
            return dev
    return None

async def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['on', 'off', 'status']:
        print("Usage: python heater. py [on|off|status]")
        sys.exit(1)
    
    command = sys.argv[1]
    device = await find_device()
    
    if not device:
        print(f"Device '{DEVICE_NAME}' not found!")
        sys.exit(1)
    
    if command == 'on':
        print(f"Turning ON '{device.alias}'...")
        await device.turn_on()
        print("Heater is now ON")
    elif command == 'off':
        print(f"Turning OFF '{device.alias}'...")
        await device.turn_off()
        print("Heater is now OFF")
    else:  # status
        status = "ON" if device.is_on else "OFF"
        print(f"'{device.alias}' is currently {status}")
        print(f"Host: {device.host}")

if __name__ == "__main__":
    asyncio.run(main())