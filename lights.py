# IMPORTANT for first time users 
# Press your bridge button
# the connect method will return a username
#username = Hue.connect(bridge_ip=YOUR_BRIDGE_IP)
#print("username is: ",username)

import sys
import warnings
import json

# Suppress all warnings
warnings.filterwarnings('ignore')

from huesdk import Discover, Hue

YOUR_USERNAME = "Ll1Beffi-loir78SOXeX5to2mIzNV7Q-gi3lZ-TO"

def main():
    # Auto-discover bridge
    discover = Discover()
    bridges = discover.find_hue_bridge_mdns(timeout=5)
    
    # Parse JSON string if needed
    if isinstance(bridges, str):
        bridges = json.loads(bridges)
    
    if not bridges: 
        print("No Hue bridge found")
        return
    
    bridge_ip = bridges[0]["internalipaddress"]
    
    # Create Hue instance
    hue = Hue(bridge_ip=bridge_ip, username=YOUR_USERNAME)
    
    # Control lights based on argument
    if len(sys.argv) > 1:
        command = sys.argv[1]. lower()
        if command == "on":
            hue.on()
            print("Lights on")
        elif command == "off":
            hue.off()
            print("Lights off")
        elif command == "status":
            lights = hue.get_lights()
            for light in lights:
                state = "ON" if light.is_on else "OFF"
                print(f"{light.name}: {state}")
        else:
            print("Usage: python lights.py [on|off|status]")
    else:
        print("Usage: python lights.py [on|off|status]")

if __name__ == "__main__": 
    main()