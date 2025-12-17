"""Simple web interface to control heater and lights."""
import asyncio
import json
import warnings
from threading import Thread, Lock
import gradio as gr
from kasa import Discover
from huesdk import Discover as HueDiscover, Hue

warnings.filterwarnings('ignore')

# Configuration
HEATER_DEVICE_NAME = "Heater dev env"
HUE_USERNAME = "Ll1Beffi-loir78SOXeX5to2mIzNV7Q-gi3lZ-TO"

# Global device instances
heater_device = None
hue_instance = None
device_lock = Lock()
event_loop = None
loop_thread = None


def start_event_loop():
    """Start a background event loop for async operations."""
    global event_loop
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    event_loop.run_forever()


def run_async_in_loop(coro):
    """Run an async function in the background event loop."""
    return asyncio.run_coroutine_threadsafe(coro, event_loop).result()


async def discover_heater():
    """Discover and return the heater device."""
    devices = await Discover.discover()
    for dev in devices.values():
        await dev.update()
        if dev.alias == HEATER_DEVICE_NAME:
            return dev
    return None


def discover_hue():
    """Discover and return the Hue instance."""
    discover = HueDiscover()
    bridges = discover.find_hue_bridge_mdns(timeout=5)
    if isinstance(bridges, str):
        bridges = json.loads(bridges)
    if bridges:
        bridge_ip = bridges[0]["internalipaddress"]
        return Hue(bridge_ip=bridge_ip, username=HUE_USERNAME)
    return None


def initialize_devices():
    """Initialize device connections at startup."""
    global heater_device, hue_instance, loop_thread
    
    print("🔍 Discovering devices...")
    
    # Start background event loop for async operations
    loop_thread = Thread(target=start_event_loop, daemon=True)
    loop_thread.start()
    
    # Wait a bit for the loop to start
    import time
    time.sleep(0.5)
    
    # Discover heater
    try:
        heater_device = run_async_in_loop(discover_heater())
        print(f"✅ Heater found: {heater_device.alias if heater_device else 'Not found'}")
    except Exception as e:
        print(f"❌ Heater discovery failed: {e}")
    
    # Discover Hue
    try:
        hue_instance = discover_hue()
        print(f"✅ Hue bridge found: {'Yes' if hue_instance else 'No'}")
    except Exception as e:
        print(f"❌ Hue discovery failed: {e}")


async def heater_action(action):
    """Perform action on heater."""
    if not heater_device:
        return "❌ Heater not connected"
    
    with device_lock:
        await heater_device.update()
        if action == "on":
            await heater_device.turn_on()
        elif action == "off":
            await heater_device.turn_off()
        await heater_device.update()
        return "✅ Heater is ON" if heater_device.is_on else "⭕ Heater is OFF"


def lights_action(action):
    """Perform action on lights."""
    if not hue_instance:
        return "❌ Hue bridge not connected"
    
    with device_lock:
        if action == "on":
            hue_instance.on()
        elif action == "off":
            hue_instance.off()
        
        lights = hue_instance.get_lights()
        if lights and any(light.is_on for light in lights):
            return "✅ Lights are ON"
        return "⭕ Lights are OFF"


def get_heater_status():
    """Get heater status."""
    if not heater_device:
        return "❌ Heater not connected", False
    
    try:
        run_async_in_loop(heater_device.update())
        is_on = heater_device.is_on
        return ("✅ Heater is ON" if is_on else "⭕ Heater is OFF"), is_on
    except:
        return "❌ Error reading heater", False


def get_lights_status():
    """Get lights status."""
    if not hue_instance:
        return "❌ Hue bridge not connected", False
    
    try:
        lights = hue_instance.get_lights()
        is_on = lights and any(light.is_on for light in lights)
        return ("✅ Lights are ON" if is_on else "⭕ Lights are OFF"), is_on
    except:
        return "❌ Error reading lights", False


def control_device(device, action):
    """Control a device."""
    if device == "heater":
        return run_async_in_loop(heater_action(action))
    else:
        return lights_action(action)


def update_all_button_visibility():
    """Determine which all-button to show."""
    _, heater_on = get_heater_status()
    _, lights_on = get_lights_status()
    
    if heater_on or lights_on:
        return gr.update(visible=True), gr.update(visible=False)
    return gr.update(visible=False), gr.update(visible=True)


def heater_control(action):
    """Control heater and update button visibility."""
    status = control_device("heater", action)
    off_btn, on_btn = update_all_button_visibility()
    return status, off_btn, on_btn


def lights_control(action):
    """Control lights and update button visibility."""
    status = control_device("lights", action)
    off_btn, on_btn = update_all_button_visibility()
    return status, off_btn, on_btn


def refresh_status():
    """Refresh both device statuses."""
    heater_status = get_heater_status()[0]
    lights_status = get_lights_status()[0]
    off_btn, on_btn = update_all_button_visibility()
    return heater_status, lights_status, off_btn, on_btn


def control_all(action):
    """Control both devices."""
    heater_status = control_device("heater", action)
    lights_status = control_device("lights", action)
    off_btn, on_btn = update_all_button_visibility()
    return heater_status, lights_status, off_btn, on_btn


# Initialize devices before building interface
initialize_devices()

# Build Gradio interface
with gr.Blocks(title="Smart Home Control") as app:
    gr.Markdown("# 🏠 Smart Home Control Panel")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 🔥 Heater")
            heater_status = gr.Textbox(label="Status", interactive=False)
            with gr.Row():
                heater_on_btn = gr.Button("Turn ON", variant="primary")
                heater_off_btn = gr.Button("Turn OFF")
        
        with gr.Column():
            gr.Markdown("### 💡 Lights")
            lights_status = gr.Textbox(label="Status", interactive=False)
            with gr.Row():
                lights_on_btn = gr.Button("Turn ON", variant="primary")
                lights_off_btn = gr.Button("Turn OFF")
    
    gr.Markdown("---")
    with gr.Row():
        refresh_btn = gr.Button("🔄 Refresh All", size="lg")
        turn_off_all_btn = gr.Button("🛑 Turn OFF All", variant="stop", size="lg")
        turn_on_all_btn = gr.Button("✅ Turn ON All", variant="primary", size="lg", visible=False)
    
    # Wire up events
    outputs = [heater_status, lights_status, turn_off_all_btn, turn_on_all_btn]
    
    heater_on_btn.click(lambda: heater_control("on"), outputs=[heater_status, turn_off_all_btn, turn_on_all_btn])
    heater_off_btn.click(lambda: heater_control("off"), outputs=[heater_status, turn_off_all_btn, turn_on_all_btn])
    lights_on_btn.click(lambda: lights_control("on"), outputs=[lights_status, turn_off_all_btn, turn_on_all_btn])
    lights_off_btn.click(lambda: lights_control("off"), outputs=[lights_status, turn_off_all_btn, turn_on_all_btn])
    
    refresh_btn.click(refresh_status, outputs=outputs)
    turn_off_all_btn.click(lambda: control_all("off"), outputs=outputs)
    turn_on_all_btn.click(lambda: control_all("on"), outputs=outputs)
    
    app.load(refresh_status, outputs=outputs)


if __name__ == "__main__":
    print("Starting Smart Home Control Panel...")
    print("Access the interface at: http://localhost:7860")

    app.launch(share=True)
