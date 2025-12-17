import asyncio
from bleak import BleakScanner

DEVICE_MAC = "B0:E9:FE:53:67:A4"

def parse_advertisement(data):
    """Parse SwitchBot advertisement data"""
    if len(data) < 6:
        return None
    
    # SwitchBot Meter broadcasts data in advertisements
    service_data = data. get('service_data', {})
    manufacturer_data = data. get('manufacturer_data', {})
    
    return {
        'service_data':  service_data,
        'manufacturer_data': manufacturer_data
    }

async def scan_meter_pro():
    """Scan for Meter Pro advertisements"""
    print(f"Scanning for {DEVICE_MAC}...")
    print("Press Ctrl+C to stop\n")
    
    def callback(device, advertising_data):
        if device.address.upper() == DEVICE_MAC.upper():
            print(f"Found:  {device.name} ({device. address})")
            print(f"RSSI: {advertising_data.rssi} dBm")
            print(f"Service Data: {advertising_data.service_data}")
            print(f"Manufacturer Data: {advertising_data.manufacturer_data}")
            print("-" * 50)
    
    scanner = BleakScanner(callback)
    await scanner.start()
    await asyncio.sleep(30.0)  # Scan for 30 seconds - FIXED! 
    await scanner.stop()

if __name__ == "__main__": 
    asyncio.run(scan_meter_pro())
