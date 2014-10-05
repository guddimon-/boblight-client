#!/usr/bin/env python

import sys
import signal
import time
import lirc
import threading
import RPi.GPIO as GPIO
import ConfigParser

import boblib


# initializie our global attributes
led_blink_loop      = None
led_blink           = None
lirc_event_loop     = None
switch_led_stripe   = None
switch_power        = None
bob                 = None
relais_led_stripe   = None


def __main__():
    global led_blink_loop
    global led_blink
    global lirc_event_loop
    global switch_led_stripe
    global switch_power
    global bob
    global relais_led_stripe

    # read configuration file
    config = ConfigParser.ConfigParser()
    config.read('boblight.cfg')
    
    switch_led_stripe   = config.getint('switch', 'switch_led_stripe')
    switch_led          = config.getint('switch', 'switch_led')
    relais_led_stripe   = config.getint('switch', 'relais_led_stripe')
    switch_power        = config.getint('switch', 'switch_power')
    
    bob_host    = config.get('boblight', 'host')
    bob_port    = config.getint('boblight', 'port')
    
    # initialize configured GPIO
    GPIO.setmode(GPIO.BOARD)
    
    GPIO.setup(switch_led_stripe, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(switch_led_stripe, GPIO.RISING, callback=switch_led_pushed, bouncetime=500)
    
    GPIO.setup(switch_led, GPIO.OUT)
    
    GPIO.setup(relais_led_stripe, GPIO.OUT, initial=0)
    
    GPIO.setup(switch_power, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(switch_power, GPIO.RISING, callback=switch_power_pushed, bouncetime=500)
    
    # start blinking 
    led_blink = GPIO.PWM(switch_led, 100)
    led_blink.start(0)
    
    led_blink_loop = BlinkThread()
    led_blink_loop.start()
    
    # start thread for IR events
    lirc_event_loop = LircThread("boblight")
    lirc_event_loop.start()
    
    # initialize boblight
    bob = boblib.Boblight(bob_host, bob_port)
    bob_client_init()
    
    for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
        signal.signal(sig, handler)
    
    try:
        while 1:
            time.sleep(1)
    
    except:
        pass
    
    


def handler(signum = None, frame = None):
    global led_blink_loop
    global led_blink
    global lirc_event_loop
    global switch_led_stripe
    global switch_power
    global bob

    print "Exit in progress..."

    # cleanup everything we used
    bob.disconnect()
    
    led_blink_loop.stop()
    led_blink.stop()
    
    lirc_event_loop.stop()
    
    GPIO.remove_event_detect(switch_led_stripe)
    GPIO.remove_event_detect(switch_power)
    GPIO.cleanup()

    while threading.active_count() > 1:
        print "Wait until all threads are stopped..."
        time.sleep(1)

    print "Exit successful."
    
    sys.exit()

class BlinkThread(threading.Thread):
    global led_blink
    global relais_led_stripe
    
    
    def run(self):
        self.run = True
        
        while self.run:
            if not GPIO.input(relais_led_stripe):
                led_blink.ChangeFrequency(200)
                for dc in range (90, 9, -5):
                    led_blink.ChangeDutyCycle(dc)
                    time.sleep(0.3)
                time.sleep(5)
                led_blink.ChangeFrequency(200)
                for dc in range (10, 91, 5):
                    led_blink.ChangeDutyCycle(dc)
                    time.sleep(0.1)
                time.sleep(1)
            else:
                led_blink.ChangeDutyCycle(10)
                time.sleep(10)
                
        print "BlinkThread stopped."

    def stop(self):
        print "Stopping BlinkThread..."
        self.run = False


class LircThread(threading.Thread):
    global led_blink_loop
    global led_blink
    global lirc_event_loop
    global switch_led_stripe
    global switch_power
    global bob


    def __init__(self, name_ir):
        super(LircThread, self).__init__()
        self.sockid = lirc.init(name_ir, blocking=False, verbose=True)


    def run(self):
        self.run = True

        while self.run:
            event = lirc.nextcode()
            if event != []:
                for e in event:
                    if e == "KEY_POWER":
                        switch_led_pushed()

                    elif e == "KEY_NUMERIC_0":
                        pass

                    elif e == "KEY_NUMERIC_1":
                        bob.setColor(1, 0, 0)
                        bob.setPriority(200)

                    elif e == "KEY_NUMERIC_2":
                        bob.setColor(0, 1, 0)
                        bob.setPriority(200)

                    elif e == "KEY_NUMERIC_3":
                        bob.setColor(0, 0, 1)
                        bob.setPriority(200)

                    elif e == "KEY_NUMERIC_4":
                        bob.setColor(1, 1, 0)
                        bob.setPriority(200)

                    elif e == "KEY_NUMERIC_5":
                        bob.setColor(1, 0, 1)
                        bob.setPriority(200)

                    elif e == "KEY_NUMERIC_6":
                        bob.setColor(0, 1, 1)
                        bob.setPriority(200)

                    elif e == "KEY_NUMERIC_7":
                        pass

                    elif e == "KEY_NUMERIC_8":
                        pass

                    elif e == "KEY_NUMERIC_9":
                        pass

                    elif e == "KEY_ZOOM":
                        pass

                    elif e == "KEY_VOLUMEUP":
                        pass

                    elif e == "KEY_MUTE":
                        pass

                    elif e == "KEY_CHANNEL":
                        pass

                    elif e == "KEY_CHANNELUP":
                        pass

                    elif e == "KEY_VOLUMEDOWN":
                        pass

                    elif e == "KEY_CHANNELDOWN":
                        pass

                    elif e == "KEY_UP":
                        pass

                    elif e == "KEY_DOWN":
                        pass

                    elif e == "KEY_LEFT":
                        pass

                    elif e == "KEY_RIGHT":
                        pass

                    elif e == "KEY_OK":
                        pass

                    elif e == "KEY_MENU":
                        pass

                    elif e == "KEY_PREVIOUS":
                        pass

                    elif e == "KEY_RECORD":
                        pass

                    elif e == "KEY_PAUSE":
                        pass

                    elif e == "KEY_NEXT":
                        pass

                    elif e == "KEY_REWIND":
                        pass

                    elif e == "KEY_PLAY":
                        pass

                    elif e == "KEY_STOP":
                        pass

                    elif e == "KEY_FASTFORWARD":
                        pass

                    elif e == "KEY_TV":
                        bob_client_init()

                    elif e == "KEY_TEXT":
                        pass

                    elif e == "KEY_RADIO":
                        pass

                    elif e == "KEY_EPG":
                        pass

                    else:
                        print e

            time.sleep(0.1)
            
        print "LircThread stopped."

    def stop(self):
        print "Stopping LircThread..."
        self.run = False


def switch_led_pushed(switch_led_stripe=None):
    GPIO.output(relais_led_stripe, not GPIO.input(relais_led_stripe))

def switch_power_pushed(switch_power=None):
    print "todo"


def bob_client_init():
    global bob
    
    bob.setPriority(255)
    bob.setInterpolation(0)
    bob.setSpeed(100)
    bob.setColor(1, 1, 1)
    bob.setInterpolation(1)
    bob.setSpeed(0)


__main__()