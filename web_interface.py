"""Simple web interface to control heater and lights."""
import subprocess
import sys
import os
import gradio as gr

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_script(script_name, command):
    """Run a script and return output."""
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPT_DIR, script_name), command],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip() if result.returncode == 0 else f"❌ Error: {result.stderr.strip()}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def get_status(device):
    """Get device status and return normalized format."""
    result = run_script(f"{device}.py", "status")
    if "currently ON" in result or (device == "lights" and "ON" in result):
        return f"✅ {device.title()} is ON", True
    elif "currently OFF" in result or (device == "lights" and "OFF" in result and "ON" not in result):
        return f"⭕ {device.title()} is OFF", False
    return result, None


def control_device(device, action):
    """Control a device and return consistent status."""
    run_script(f"{device}.py", action)
    return get_status(device)[0]


def update_all_button_visibility():
    """Check device statuses and determine which button to show."""
    _, heater_on = get_status("heater")
    _, lights_on = get_status("lights")
    
    # Show "Turn OFF All" if either device is ON
    if heater_on or lights_on:
        return gr.update(visible=True), gr.update(visible=False)
    else:
        return gr.update(visible=False), gr.update(visible=True)


def heater_control(action):
    """Control heater and update all-button visibility."""
    status = control_device("heater", action)
    off_btn, on_btn = update_all_button_visibility()
    return status, off_btn, on_btn


def lights_control(action):
    """Control lights and update all-button visibility."""
    status = control_device("lights", action)
    off_btn, on_btn = update_all_button_visibility()
    return status, off_btn, on_btn


def refresh_status():
    """Refresh both device statuses and button visibility."""
    heater_status = get_status("heater")[0]
    lights_status = get_status("lights")[0]
    off_btn, on_btn = update_all_button_visibility()
    return heater_status, lights_status, off_btn, on_btn


def control_all(action):
    """Control both devices."""
    heater_status = control_device("heater", action)
    lights_status = control_device("lights", action)
    off_btn, on_btn = update_all_button_visibility()
    return heater_status, lights_status, off_btn, on_btn


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
