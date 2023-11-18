# ble_scanner.py
import time
from micropython import const
import bluetooth
import device_handler
from uart_handler import uart_write

_IRQ_SCAN_RESULT = const(5)


def bt_irq(event, data):
    if event == _IRQ_SCAN_RESULT:
        device_handler.handle_device(data)


def scan_devices(scan_duration=1, sleep_duration=10):
    uart_write("Scanning for BLE devices...\n\n\n")

    ble = bluetooth.BLE()
    ble.active(True)
    ble.irq(bt_irq)
    ble.gap_scan(0, scan_duration * 1000)

    while True:
        time.sleep(1)
        device_handler.process_devices()
        uart_write(device_handler.get_device_json())
        # uart_write(device_handler.get_device_json())
        # uart_write("\n\n\n")
        time.sleep(sleep_duration)


# Run the scanning function with default parameters
scan_devices()
