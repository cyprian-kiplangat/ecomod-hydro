import asyncio
from bleak import BleakScanner, BleakClient

# Your Meter Pro's MAC address (from the API response)
DEVICE_MAC = "B0:E9:FE:53:67:A4"  # Formatted version of B0E9FE5367A4

# SwitchBot Meter Pro service UUIDs
SERVICE_UUID = "cba20d00-224d-11e6-9fb8-0002a5d5c51b"
TEMP_HUMIDITY_CHAR = "cba20d02-224d-11e6-9fb8-0002a5d5c51b"

def parse_meter_data(data):
    """Parse temperature and humidity from Meter Pro data"""
    if len(data) < 6:
        return None
    
    # Battery level (first byte)
    battery = data[2] & 0b01111111
    
    # Temperature (bytes 3-4)
    temp_data = data[4] & 0b01111111
    temp_decimal = data[3] & 0b00001111
    temperature = temp_data + (temp_decimal / 10.0)
    
    # Check if temperature is negative
    if data[4] & 0b10000000:
        temperature = -temperature
    
    # Humidity (byte 5)
    humidity = data[5] & 0b01111111
    
    return {
        'temperature': temperature,
        'humidity': humidity,
        'battery': battery
    }

async def read_meter_pro():
    """Connect and read data from Meter Pro"""
    print(f"Searching for device {DEVICE_MAC}...")
    
    # Scan for the device
    devices = await BleakScanner. discover(timeout=10.0)
    target_device = None
    
    for device in devices:
        if device.address. upper() == DEVICE_MAC.upper():
            target_device = device
            print(f"Found device: {device.name} ({device.address})")
            break
    
    if not target_device:
        print("Device not found!  Make sure:")
        print("1. Bluetooth is enabled on your computer")
        print("2. Meter Pro is nearby (within Bluetooth range)")
        print("3. The MAC address is correct")
        return
    
    # Connect to device
    async with BleakClient(target_device.address) as client:
        print(f"Connected:  {client.is_connected}")
        
        # Read temperature and humidity
        data = await client.read_gatt_char(TEMP_HUMIDITY_CHAR)
        print(f"\nRaw data: {data. hex()}")
        
        # Parse the data
        result = parse_meter_data(data)
        
        if result:
            print("\n=== Meter Pro Data ===")
            print(f"Temperature: {result['temperature']}°C")
            print(f"Humidity: {result['humidity']}%")
            print(f"Battery: {result['battery']}%")
        else:
            print("Failed to parse data")

# Run the async function
if __name__ == "__main__": 
    asyncio.run(read_meter_pro())
