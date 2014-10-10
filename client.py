#!/usr/bin/env python

import sys
import signal
import time
import lirc
import threading
import RPi.GPIO as GPIO
import ConfigParser
from Queue import Queue, Empty

import boblib

from lcdproc.server import Server

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
    global lcd

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
    
    # Queues for sharing data between threads
    global q_lcd
    q_lcd = Queue()
        
    # start blinking 
    led_blink = GPIO.PWM(switch_led, 100)
    led_blink.start(0)
    
    led_blink_loop = BlinkThread()
    led_blink_loop.start()
    
    # initialize boblight
    bob = boblib.Boblight(bob_host, bob_port)
    bob_client_init()

    # start thread for IR events
    lirc_event_loop = LircThread("boblight")
    lirc_event_loop.start()
    
    # start thread for LCD
    lcd = ThreadLCD()
    lcd.start()
    
    for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
        signal.signal(sig, handler)
    
    try:
        while 1:
            time.sleep(1)
    
    except:
        pass
    
    


def handler(signum = None, frame = None):
    print "Exit in progress..."

    # cleanup everything we used
    lcd.stop()
    
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
    list_LCD = dict()

    def __init__(self, name_ir):
        super(LircThread, self).__init__()
        self.sockid = lirc.init(name_ir, blocking=False, verbose=True)
        
        self.list_LCD.update({
                              "bob_server_host":    bob.getHost(),
                              "bob_server_port":    bob.getPort(),
                              "bob_count_lights":   bob.getLightsCount(),
                              "bob_priority":       bob.getPriority()
                              })


    def run(self):
        self.run = True

        while self.run:
            event = lirc.nextcode()
            if event != []:
                for e in event:
                    if e == "KEY_POWER":
                        switch_led_pushed()
                        self.list_LCD.update({
                                              "key": "Power On/Off"
                        })
                        self.sendToLCD()

                    elif e == "KEY_NUMERIC_0":
                        pass

                    elif e == "KEY_NUMERIC_1":
                        bob.setColor(1, 0, 0)
                        bob.setPriority(200)
                        self.list_LCD.update({
                                              "key": "Alles ROT",
                                              "bob_priority": 200
                        })
                        self.sendToLCD()

                    elif e == "KEY_NUMERIC_2":
                        bob.setColor(0, 1, 0)
                        bob.setPriority(200)
                        self.list_LCD.update({
                                              "key": "Alles GRUEN",
                                              "bob_priority": 200
                        })
                        self.sendToLCD()

                    elif e == "KEY_NUMERIC_3":
                        bob.setColor(0, 0, 1)
                        bob.setPriority(200)
                        self.list_LCD.update({
                                              "key": "Alles BLAU",
                                              "bob_priority": 200
                        })
                        self.sendToLCD()

                    elif e == "KEY_NUMERIC_4":
                        bob.setColor(1, 1, 0)
                        bob.setPriority(200)
                        self.list_LCD.update({
                                              "key": "Alles GELB",
                                              "bob_priority": 200
                        })
                        self.sendToLCD()

                    elif e == "KEY_NUMERIC_5":
                        bob.setColor(1, 0, 1)
                        bob.setPriority(200)
                        self.list_LCD.update({
                                              "key": "Alles VIOLETT",
                                              "bob_priority": 200
                        })
                        self.sendToLCD()

                    elif e == "KEY_NUMERIC_6":
                        bob.setColor(0, 1, 1)
                        bob.setPriority(200)
                        self.list_LCD.update({
                                              "key": "Alles CYAN",
                                              "bob_priority": 200
                        })
                        self.sendToLCD()

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
        
    def sendToLCD(self):
        q_lcd.put(self.list_LCD)
        q_lcd.join()


class ThreadLCD(threading.Thread):
    def __init__(self):
        super(ThreadLCD, self).__init__()
        pass
    
    def run(self):
        lcd = Server("192.168.2.100", debug=False)
        lcd.start_session()
        
        info = None
        
        self.run = True
        while self.run:
            try:
                data = q_lcd.get_nowait()
                q_lcd.task_done()
                
                key = str(data.get("key"))
                bob_server_host = str(data.get("bob_server_host"))
                bob_server_port = str(data.get("bob_server_port"))
                bob_count_lights = str(data.get("bob_count_lights"))
                bob_priority = str(data.get("bob_priority"))
                
                if info != None:
                    lcd.del_screen("Info")

                info = lcd.add_screen("Info")
                info.set_heartbeat("off")
                info.add_string_widget("boblight", text="Boblight:")
                info.add_string_widget("bob_server", text=bob_server_host+":"+bob_server_port, x=1, y=2)
                info.add_string_widget("bob_count_lights", text=bob_count_lights, x=1, y=3)
                info.add_string_widget("bob_priority", text=bob_priority, x=1, y=4)
                info.add_string_widget("key_IR", text=key, x=21, y=2)

                info.set_duration(11)
                info.set_timeout(10)
            except Empty:
                pass

            time.sleep(1)
            
        print "ThreadLCD stopped."
            
    def stop(self):
        print "Stopping ThreadLCD..."
        self.run = False
        try:
            q_lcd.task_done()
        except ValueError:
            pass


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