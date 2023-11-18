from machine import Pin, SPI, PWM
import framebuf
import time, random
import os
import network
import machine
import time

from micropython import const
import machine

uart = machine.UART(0, baudrate=9600)
BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9


class LCD_1inch8(framebuf.FrameBuffer):
    def __init__(self):
        self.width = 162  # Adjusted width for the 1.8-inch display
        self.height = 132  # Adjusted height for the 1.8-inch display

        self.cs = Pin(CS, Pin.OUT)
        self.rst = Pin(RST, Pin.OUT)

        self.cs(1)
        self.spi = SPI(1, baudrate=115200, polarity=0, phase=0, sck=Pin(SCK), mosi=Pin(MOSI), miso=None)
        self.dc = Pin(DC, Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()

        self.red = 0xf800
        self.green = 0x07E0
        self.blue = 0x001F
        self.white = 0xFFFF

    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize dispaly"""
        self.rst(1)
        self.rst(0)
        self.rst(1)

        self.write_cmd(0x36)
        self.write_data(0x70)

        self.write_cmd(0x3A)
        self.write_data(0x05)

        self.write_cmd(0xB2)
        self.write_data(0x0C)
        self.write_data(0x0C)
        self.write_data(0x00)
        self.write_data(0x33)
        self.write_data(0x33)

        self.write_cmd(0xB7)
        self.write_data(0x35)

        self.write_cmd(0xBB)
        self.write_data(0x19)

        self.write_cmd(0xC0)
        self.write_data(0x2C)

        self.write_cmd(0xC2)
        self.write_data(0x01)

        self.write_cmd(0xC3)
        self.write_data(0x12)

        self.write_cmd(0xC4)
        self.write_data(0x20)

        self.write_cmd(0xC6)
        self.write_data(0x0F)

        self.write_cmd(0xD0)
        self.write_data(0xA4)
        self.write_data(0xA1)

        self.write_cmd(0xE0)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0D)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2B)
        self.write_data(0x3F)
        self.write_data(0x54)
        self.write_data(0x4C)
        self.write_data(0x18)
        self.write_data(0x0D)
        self.write_data(0x0B)
        self.write_data(0x1F)
        self.write_data(0x23)

        self.write_cmd(0xE1)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0C)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2C)
        self.write_data(0x3F)
        self.write_data(0x44)
        self.write_data(0x51)
        self.write_data(0x2F)
        self.write_data(0x1F)
        self.write_data(0x1F)
        self.write_data(0x20)
        self.write_data(0x23)

        self.write_cmd(0x21)

        self.write_cmd(0x11)

        self.write_cmd(0x29)

    def show(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0xef)

        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0xEF)

        self.write_cmd(0x2C)

        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)


pwm = PWM(Pin(BL))
pwm.freq(1000)
pwm.duty_u16(32768)  # max 65535

LCD = LCD_1inch8()

keyA = Pin(15, Pin.IN, Pin.PULL_UP)
keyB = Pin(17, Pin.IN, Pin.PULL_UP)
keyX = Pin(19, Pin.IN, Pin.PULL_UP)
keyY = Pin(21, Pin.IN, Pin.PULL_UP)

up = Pin(2, Pin.IN, Pin.PULL_UP)
down = Pin(18, Pin.IN, Pin.PULL_UP)
left = Pin(16, Pin.IN, Pin.PULL_UP)
right = Pin(20, Pin.IN, Pin.PULL_UP)
ctrl = Pin(3, Pin.IN, Pin.PULL_UP)

import bluetooth
import binascii
import time

_IRQ_SCAN_RESULT = const(5)
devices = {}


def bt_irq(event, data):
    if event == _IRQ_SCAN_RESULT:
        addr_type, addr, connectable, rssi, adv_data = data
        address = binascii.hexlify(addr).decode()
        devices[address] = rssi
        uart.write("-----------------------------------------------\n")
        uart.write(f"addr_type : {addr_type}\n")
        uart.write(f"addr : {binascii.hexlify(addr).decode()}\n")
        uart.write(f"connectable : {connectable}\n")
        uart.write(f"rssi : {rssi}\n")
        uart.write(f"adv_data : {binascii.hexlify(adv_data).decode()}\n")
        uart.write("-----------------------------------------------\n")


ble = bluetooth.BLE()
ble.active('active')
ble.irq(bt_irq)
ble.gap_scan(1000, 60000)

while 1:
    time.sleep(1)
    LCD.fill(0)
    LCD.text("Bluetooth devices", 10, 0, LCD.green)

    # sort by rssi
    devs = sorted(devices.items(), key=lambda item: item[1], reverse=True)
    LCD.text("Device count: ",10, 15, LCD.white)
    LCD.text(str(len(devs)),120, 15, LCD.white)

    y = 30
    for key, value in devs:
        uart.write("-----------------------------")
        uart.write()
        addr = key
        rssi = value
        LCD.text(addr + " " + str(rssi), 10, y, LCD.white)
        # color bars by signal strength
        if rssi > -75:
            color = LCD.green
        elif rssi > -95:
            color = LCD.blue
        else:
            color = LCD.red
        LCD.fill_rect(150, y, 120 + rssi, 8, color)
        y += 10
    LCD.show()
    devices = {}


