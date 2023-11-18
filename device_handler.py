# device_handler.py
import binascii
import json

import uart_handler

seen_devices = set()  # Set to keep track of seen devices
devices = []  # List to store device information


def make_device(addr_type, addr, connectable, rssi, adv_data, raw_packet):
    device = {
        'addr_type': addr_type,
        'addr': addr,
        'connectable': connectable,
        'rssi': rssi,
        'adv_data': binascii.hexlify(adv_data).decode(),
        'raw_packet': raw_packet,
    }

    # Distance approximation
    n_constant = 2
    n_measured_power = -69
    distance = round(pow(10, ((n_measured_power - int(rssi)) / (10 * n_constant))), 2)
    device['distance'] = str(distance)
    return device


def handle_device(data):
    addr_type, addr, connectable, rssi, adv_data = data
    raw_packet = get_raw_packet(adv_data)
    address = binascii.hexlify(addr).decode()

    # Check if the device with this address is already seen
    if address not in seen_devices:
        devices.append(make_device(addr_type, address, connectable, rssi, adv_data, raw_packet))
        seen_devices.add(address)  # Mark the device as seen


def get_raw_packet(adv_data):
    # Use a fixed-length slice of the advertising data as a representation of the raw packet
    raw_packet = adv_data[:10]  # Adjust the length as needed
    return binascii.hexlify(raw_packet).decode()


def get_device_json():
    process_devices()
    device_count = len(devices)
    device_list = devices.copy()  # Copy the devices list to avoid modifying the original list
    devices.clear()  # Clear the original list for the next scan
    seen_devices.clear()  # Clear the set of seen devices
    # uart_handler.uart_write(json.dumps({"device_count": device_count}))
    return json.dumps({"device_count": device_count, "device_list": device_list})


def process_devices():
    global devices, seen_devices
    # Accumulate device information in a list
    devices_info = []
    for device in devices:
        device_info = {
            "addr_type": device['addr_type'],
            "addr": device['addr'],
            "connectable": device['connectable'],
            "rssi": device['rssi'],
            "distance": device['distance']
        }
        devices_info.append(device_info)

