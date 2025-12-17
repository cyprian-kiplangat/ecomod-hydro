import time
import hashlib
import hmac
import base64
import uuid
import requests
import json

# Your credentials
TOKEN = '255c68116f1fe09fc1c6733271a62c556451720a8b9e01d787610e66b8b115f5bd78070be75783d78b42a8b9b1580b15'  # Replace with your token
SECRET = '0db483fc3005d3c824a16c99a2aebcd5'  # Replace with your secret key

def generate_sign(token, secret, nonce):
    """Generate authentication signature"""
    t = int(round(time.time() * 1000))
    string_to_sign = '{}{}{}'.format(token, t, nonce)
    string_to_sign = bytes(string_to_sign, 'utf-8')
    secret = bytes(secret, 'utf-8')
    sign = base64.b64encode(hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())
    return sign, t

def get_devices():
    """Get list of all devices"""
    nonce = str(uuid.uuid4())
    sign, t = generate_sign(TOKEN, SECRET, nonce)
    
    headers = {
        'Authorization': TOKEN,
        'Content-Type': 'application/json',
        'charset': 'utf8',
        't': str(t),
        'sign': str(sign, 'utf-8'),
        'nonce': nonce
    }
    
    response = requests.get('https://api.switch-bot.com/v1.1/devices', headers=headers)
    return response.json()

def get_meter_status(device_id):
    """Get Meter Pro status (temperature, humidity, battery)"""
    nonce = str(uuid.uuid4())
    sign, t = generate_sign(TOKEN, SECRET, nonce)
    
    headers = {
        'Authorization': TOKEN,
        'Content-Type': 'application/json',
        'charset': 'utf8',
        't': str(t),
        'sign': str(sign, 'utf-8'),
        'nonce': nonce
    }
    
    response = requests.get(f'https://api.switch-bot.com/v1.1/devices/{device_id}/status', headers=headers)
    return response.json()

# Main execution
if __name__ == "__main__":
    # Get all devices
    #print("Fetching devices...")
    devices = get_devices()
    print(json.dumps(devices, indent=2))
    
    # Find your Meter Pro and get its status
    # Replace 'YOUR_DEVICE_ID' with your actual Meter Pro device ID from the devices list
    device_id = 'B0E9FE5367A4'
    print("\nFetching Meter Pro status...")
    status = get_meter_status(device_id)
    print(json.dumps(status, indent=2))
