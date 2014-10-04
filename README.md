boblight-client
===============

This code is for my project to control the lights connected to a Raspberry Pi running boblightd with an IR remote control.

It gives the possibility to switch the power supply of my LED stripe on and off using a hardware button I connected to a GPIO, or even by pushing the on/off button on my old Pinnacle remote control I had lying around.

If either the button in hardware or remote control is pushed, the code switches a relais which is connected to another GPIO.

For the time being I added code for the buttons 1 to 6 on my remote control. Each of them with another color:
	1: red
	2: green
	3: blue
	4: yellow
	5: violet
	6: cyan


How to use
----------

1. Install lirc, python-lirc, python-rpi.gpio
2. You need to get your IR remote running using lirc. See my configuration "lirc.conf" in ./config to get some inspiration.
3. It is necessary that lirc passes commands to this python script. Therefore it is necessary to have a mapping file named "lircrc" which you can find in ./config as well.
4. Add buttons to your Raspberry Pi if you want to use the complete code


To be done
----------

- add configuration for using buttons
- find a bug where color is sent to boblightd, but color does not change at all
- add ability to reconnect with boblightd in case the connection was lost
- add some code to make boblib.py more robust
