#!/usr/bin/env python

import time
import lirc
import threading
import RPi.GPIO as GPIO
import ConfigParser

import boblib

GPIO.setmode(GPIO.BOARD)

class LircThread(threading.Thread):
    def run(self):
        self.run = True
        self.sockid = lirc.init("boblight", blocking=False, verbose=True)

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

    def stop(self):
        self.run = False


def switch_led_pushed(switch_led=None):
    GPIO.output(relais_led, not GPIO.input(relais_led))

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


config = ConfigParser.ConfigParser()
config.read('switch.cfg')

switch_led = config.getint('switch', 'switch_led')
led = config.getint('switch', 'led')
relais_led = config.getint('switch', 'relais_led')
switch_power = config.getint('switch', 'switch_power')

# # Pin P1/26 auf Raspi (GPIO 7): Schalter an/aus
# switch_led = 7
GPIO.setup(switch_led, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(switch_led, GPIO.RISING, callback=switch_led_pushed, bouncetime=500)

# # Pin P1/24 auf Raspi (GPIO 8): LED vom Schalter
# led = 8
GPIO.setup(led, GPIO.OUT)
led_blink = GPIO.PWM(led, 100)

# # Pin P1/12 auf Raspi (GPIO 18): Schaltrelais fuer LED-Kette
# relais_led = 18
GPIO.setup(relais_led, GPIO.OUT, initial=0)

# # Pin P1/22 auf Raspi (GPIO 25): Dienst neustarten / Softwarereboot (2sec) / Herunterfahren (5sec)
# switch_power = 25
GPIO.setup(switch_power, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(switch_power, GPIO.RISING, callback=switch_power_pushed, bouncetime=500)

led_blink.start(0)

lirc_event_loop = LircThread()
lirc_event_loop.start()


bob = boblib.Boblight("127.0.0.1", 19333)
print bob

bob_client_init()

try:
    while 1:
        if not GPIO.input(relais_led):
            led_blink.ChangeFrequency(50)
            for dc in range (90, 9, -5):
                led_blink.ChangeDutyCycle(dc)
                time.sleep(0.1)
            time.sleep(5)
            led_blink.ChangeFrequency(200)
            for dc in range (10, 91, 5):
                led_blink.ChangeDutyCycle(dc)
                time.sleep(0.1)
            time.sleep(1)
        else:
            led_blink.ChangeDutyCycle(10)
            time.sleep(10)

except:
    pass


bob.disconnect()

lirc_event_loop.stop()

GPIO.remove_event_detect(switch_led)
GPIO.remove_event_detect(switch_power)
GPIO.cleanup()
