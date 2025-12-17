import asyncio
from govee_local_api import GoveeController

async def control_plug():
    # Create controller with auto-discovery
    controller = GoveeController()
    await controller.start()
    
    # Wait for device discovery
    await asyncio.sleep(3)
    print(controller.devices)
    
    # Get your plug (first device found)
    plug = list(controller.devices. values())[0]

    
    # Turn on
    await plug.turn_on()
    
    # Turn off
    await plug.turn_off()

# Run it
asyncio.run(control_plug())
