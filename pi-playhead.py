#!/usr/bin/env python3

import time
import json
import os

from tm1637 import TM1637Decimal

from pythonosc import udp_client
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher
from threading import Thread

DIO = 4
CLK = 5
QLAB_IP = "192.168.123.2"
RASPBERRY_PI_IP = "192.168.123.1" #"192.168.0.236"

blank_string="      "
blank = False
tm = TM1637Decimal(CLK, DIO, 1)
resolution = 0.25


def update_screen(message):
    input_length = 0
    no_decimal = ""
    if blank:
        message = blank_string
    else:
#if "." not in message:
#            no_decimal = "--"
#        else:
#            no_decimal = ""
        if type(message) is int:
            message = str(message)
    input_length = len("".join(e for e in message if e.isalnum()))
    if input_length > 6:
        input_length = 6
#        print(message[0:5])
        message = message[0:6]
#    tm.show(blank_string[input_length:] + message)
#    tm.write(swap(tm.encode_string(blank_string[input_length:] + message + no_decimal)))
    tm.write(swap(tm.encode_string(blank_string[input_length:] + message)))

def swap(segs):
    length = len(segs)
    if length == 4 or length == 5:
        segs.extend(bytearray([0] * (6 - length)))
    segs[0], segs[2] = segs[2], segs[0]
    if length >= 4:
        segs[3], segs[5] = segs[5], segs[3]
    return segs

def make_message(address, *args):
    data = json.loads(args[0])
    update_screen(data['data'])
#    update_screen("123456")

def set_brightness(address, *args):
    val=args[0]
    if val < 1:
        val = 1
    tm.brightness(val)

def set_refresh_rate(address, *args):
    global resolution
    resolution = args[0]

def blank_screen(address, *args):
    global blank
    blank = args[0]

def osc_client():
    while True:
        response = os.system("ping -W 0.1 -c 1 192.168.123.2")
        if response == 0:
            client = udp_client.SimpleUDPClient(QLAB_IP, 53000)
            client.send_message("/cue/playhead/number", None)
            time.sleep(resolution)
        else:
            update_screen("NOQLAB")

def osc_server():
    from pythonosc import osc_server
    dispatcher = Dispatcher()
    dispatcher.map("/reply/cue_id/*/number", make_message)
    dispatcher.map("/settings/brightness", set_brightness)
    dispatcher.map("/settings/refreshRate", set_refresh_rate)
    dispatcher.map("/settings/blank", blank_screen)
    server = osc_server.ThreadingOSCUDPServer((RASPBERRY_PI_IP, 53001), dispatcher)
    server.serve_forever()

update_screen("      ")
time.sleep(1)
update_screen("Loadin")
time.sleep(2)
update_screen("v0.1.13")
time.sleep(2)

Thread(target=osc_client).start()

osc_server()

