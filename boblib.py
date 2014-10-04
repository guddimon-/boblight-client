from telnetlib import Telnet
from string import split

class Color:
    def __init__(self, red=0, green=0, blue=0):
        self.setColor(red, green, blue)
        
    def setColor(self, red=0, green=0, blue=0):
        self._red = red
        self._green = green
        self._blue = blue
        
    def getRed(self):
        return self._red
    
    def getGreen(self):
        return self._green
    
    def getBlue(self):
        return self._blue


class Light(object):
    def __init__(self, name, vSanFrom=0, vScanTo=0, hScanFrom=0, hScanTo=0, setManually=False, color=Color(), speed=0, interpolation=False):
        self._name = name
        self._vScanFrom = vSanFrom
        self._vScanTo = vSanFrom
        self._hScanFrom = hScanFrom
        self._hScanTo = hScanTo
        self._setManually = setManually
        self._color = color
        self._speed = speed
        self._interpolation = interpolation
    
    def setInterpolation(self, interpolation):
        self._interpolation = interpolation
            
    def setSetManually(self, setManually):
        self._setManually = setManually
        
    def setSpeed(self, speed):
        self._speed = speed
        
    def getName(self):
        return self._name
    
    def getSpeed(self):
        return self._speed
    
    def getColor(self):
        return self._color
    
    def getHScanFrom(self):
        return self._hScanFrom
    
    def getHScanTo(self):
        return self._hScanTo
    
    def getVScanFrom(self):
        return self._vScanFrom
    
    def getVScanTo(self):
        return self._vScanTo
    
    def getInterpolation(self):
        return self._interpolation


class Boblight:
    _HELLO                  = "hello\n"
    _GETLIGHTS              = "get lights\n"
    _SETPRIORITY            = "set _priority {0}\n"
    _SETLIGHTRGB            = "set _light {0} rgb {1} {2} {3}\n"
    _SETLIGHTSPEED          = "set _light {0} _speed {1}\n"
    _SETLIGHTINTERPOLATION  = "set _light {0} _interpolation {1}\n"
    _SYNC                   = "sync\n"
    _PING                   = "ping\n"
    
    _EOL        = "\n"
    _SPLITTER   = " "
    
    def __init__(self, host="", port=19333, priority=254):
        if host != "":
            self.connect(host, port)
        self._setPriority(priority)
        
    def connect(self, host, port):
        self._tn = Telnet(host, port)
        
        self._tn.write(self._HELLO)
        self._tn.read_until("\n")
        
        self.getLightsFromServer()
    
    def getLightsFromServer(self):
        self._tn.write(self._GETLIGHTS)
        self._light = []
        lights = self._tn.read_until("\n")

        size = int(lights.split(self._SPLITTER)[1])
        
        for i in range(0, size):
            light = self._tn.read_until("\n", 10)
            light_split = split(light, self._SPLITTER)

            self._light.append(Light(light_split[1], light_split[3], light_split[4], light_split[5], light_split[6]))

    def _sendPriority(self):
        self._tn.write(self._SETPRIORITY.format(self._priority))
        
    def _setPriority(self, priority):
        self._priority = self._checkPriority(priority)
        self._sendPriority()
        
    def _checkPriority(self, priority):
        if priority < 0:
            priority = 0
        if priority > 255:
            priority = 255
        return priority
    
    def _sendColor(self):
        for l in self._light:
            self._tn.write(self._SETLIGHTRGB.format(l.getName(), l.getColor().getRed(), l.getColor().getGreen(), l.getColor().getBlue()))
            
        self.sync()
        
    def setColor(self, red, green, blue):
        for l in self._light:
            l.getColor().setColor(red, green, blue)
            
        self._sendColor()
        
    def disconnect(self):
        self._tn.close()
        
    def _sendSpeed(self):
        for l in self._light:
            self._tn.write(self._SETLIGHTSPEED.format(l.getName(), l.getSpeed()))
        
    def setSpeed(self, speed):
        for l in self._light:
            l.setSpeed(speed)
        
        self._sendSpeed()
        
    def setInterpolation(self, interpolation):
        for l in self._light:
            l.setInterpolation(interpolation)
        
        self._sendInterpolation()
        
    def _sendInterpolation(self):
        for l in self._light:
            self._tn.write(self._SETLIGHTINTERPOLATION.format(l.getName(), l.getInterpolation()))
        
    def sync(self):
        self._tn.write(self._SYNC)
        
    def getLightsCount(self):
        return self._light.__sizeof__()
    
    def getLight(self):
        return self._light
    
    def ping(self):
        self._tn.write(self._PING)
        p = self._tn.read_until("\n")
        
        if p == "ping 1":
            return True
        else:
            return False
