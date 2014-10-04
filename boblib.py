from telnetlib import Telnet
from string import split

class Color:
    def __init__(self, red=0, green=0, blue=0):
        self.setColor(red, green, blue)
        
    def setColor(self, red=0, green=0, blue=0):
        self.red = red
        self.green = green
        self.blue = blue
        
    def getRed(self):
        return self.red
    
    def getGreen(self):
        return self.green
    
    def getBlue(self):
        return self.blue


class Light(object):
    def __init__(self, name, vSanFrom=0, vScanTo=0, hScanFrom=0, hScanTo=0, setManually=False, color=Color(), speed=0, interpolation=False):
        self.name = name
        self.vScanFrom = vSanFrom
        self.vScanTo = vSanFrom
        self.hScanFrom = hScanFrom
        self.hScanTo = hScanTo
        self.setManually = setManually
        self.color = color
        self.speed = speed
        self.interpolation = interpolation
    
    def setInterpolation(self, interpolation):
        self.interpolation = interpolation
            
    def setSetManually(self, setManually):
        self.setManually = setManually
        
    def setSpeed(self, speed):
        self.speed = speed
        
    def getName(self):
        return self.name
    
    def getSpeed(self):
        return self.speed
    
    def getColor(self):
        return self.color
    
    def getHScanFrom(self):
        return self.hScanFrom
    
    def getHScanTo(self):
        return self.hScanTo
    
    def getVScanFrom(self):
        return self.vScanFrom
    
    def getVScanTo(self):
        return self.vScanTo
    
    def getInterpolation(self):
        return self.interpolation


class Boblight:
    HELLO = "hello\n"
    GETLIGHTS = "get lights\n"
    SETPRIORITY = "set priority {0}\n"
    SETLIGHTRGB = "set light {0} rgb {1} {2} {3}\n"
    SETLIGHTSPEED = "set light {0} speed {1}\n"
    SETLIGHTINTERPOLATION = "set light {0} interpolation {1}\n"
    SYNC = "sync\n"
    PING = "ping\n"
    SPLITTER = " "
    
    def __init__(self, host, port, priority=254):
        self.connect(host, port)
        self.setPriority(priority)
        
    def connect(self, host, port):
        self.tn = Telnet(host, port)
        
        self.tn.write(self.HELLO)
        """
        print "Hello:"
        print self.tn.read_until("\n")
        print "END"
        """
        
        self.getLightsFromServer()
    
    def getLightsFromServer(self):
        self.tn.write(self.GETLIGHTS)
        self.light = []
        lights = self.tn.read_until("\n")
        """
        print "Lights:"
        print lights
        print "END"
        """

        size = int(lights.split(self.SPLITTER)[1])
        """
        print "Size:"
        print size
        print "END"
        """
        
        for i in range(0, size):
            light = self.tn.read_until("\n", 10)
            """
            print "Light:"
            print light
            print "END"
            """
            
            light_split = split(light, self.SPLITTER)
            """
            print "Light splitted:"
            print light_split
            print "END"
            """

            self.light.append(Light(light_split[1], light_split[3], light_split[4], light_split[5], light_split[6]))

    def sendPriority(self):
        self.tn.write(self.SETPRIORITY.format(self.priority))
        
    def setPriority(self, priority):
        self.priority = self.checkPriority(priority)
        self.sendPriority()
        
    def checkPriority(self, priority):
        if priority < 0:
            priority = 0
        if priority > 255:
            priority = 255
        return priority
    
    def sendColor(self):
        for l in self.light:
            self.tn.write(self.SETLIGHTRGB.format(l.getName(), l.getColor().getRed(), l.getColor().getGreen(), l.getColor().getBlue()))
            
        self.sync()
        
    def setColor(self, red, green, blue):
        for l in self.light:
            l.getColor().setColor(red, green, blue)
            
        self.sendColor()
        
    def disconnect(self):
        self.tn.close()
        
    def sendSpeed(self):
        for l in self.light:
            self.tn.write(self.SETLIGHTSPEED.format(l.getName(), l.getSpeed()))
        
    def setSpeed(self, speed):
        for l in self.light:
            l.setSpeed(speed)
        
        self.sendSpeed()
        
    def setInterpolation(self, interpolation):
        for l in self.light:
            l.setInterpolation(interpolation)
        
        self.sendInterpolation()
        
    def sendInterpolation(self):
        for l in self.light:
            self.tn.write(self.SETLIGHTINTERPOLATION.format(l.getName(), l.getInterpolation()))
        
    def sync(self):
        self.tn.write(self.SYNC)
        
    def getLightsCount(self):
        return self.light.__sizeof__()
    
    def getLight(self):
        return self.light
    
    def ping(self):
        self.tn.write(self.PING)
        p = self.tn.read_until("\n")
        
        if p == "ping 1":
            return True
        else:
            return False
