# uart_handler.py
from machine import UART

uart = UART(0, baudrate=9600)

def uart_write(data):
    uart.write(data.encode('utf-8'))
