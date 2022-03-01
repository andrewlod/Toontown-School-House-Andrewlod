from direct.directnotify import DirectNotifyGlobal
import HoodDataAI, ZoneUtil
from toontown.toonbase import ToontownGlobals
from toontown.safezone import DistributedSeatAI
from panda3d.core import *
from panda3d.toontown import *
import string
if __debug__:
    import pdb

class DRHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DRHoodDataAI')

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.Restaurant
        if zoneId == None:
            zoneId = hoodId
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
        return

    def startup(self):
        HoodDataAI.HoodDataAI.startup(self)
        self.createSeats()

    def findAndCreateSeats(self, dnaGroup, zoneId, area, overrideDNAZone = 0, type = 'restaurant_chair'):
        seats = []
        if isinstance(dnaGroup, DNAGroup) and string.find(dnaGroup.getName(), type) >= 0:
            if type == 'restaurant_chair':
                nameInfo = dnaGroup.getName().split('_')
                pos = Point3(0, 0, 0)
                hpr = Point3(0, 0, 0)
                for i in xrange(dnaGroup.getNumChildren()):
                    childDnaGroup = dnaGroup.at(i)
                    if string.find(childDnaGroup.getName(), 'restaurant_chair') >= 0:
                        pos = childDnaGroup.getPos()
                        hpr = childDnaGroup.getHpr()
                        break

                seat = DistributedSeatAI.DistributedSeatAI(self.air, nameInfo[2], pos[0], pos[1], pos[2], hpr[0], hpr[1], hpr[2])
                seat.generateWithRequired(zoneId)
                seats.append(seat)
        else:
            if isinstance(dnaGroup, DNAVisGroup) and not overrideDNAZone:
                zoneId = ZoneUtil.getTrueZoneId(int(dnaGroup.getName().split(':')[0]), zoneId)
            for i in xrange(dnaGroup.getNumChildren()):
                childSeats = self.findAndCreateSeats(dnaGroup.at(i), zoneId, area, overrideDNAZone, type)
                seats += childSeats

        return seats

    def createSeats(self):
        self.seats = []
        for zone in self.air.zoneTable[self.canonicalHoodId]:
            zoneId = ZoneUtil.getTrueZoneId(zone[0], self.zoneId)
            dnaData = self.air.dnaDataMap.get(zone[0], None)
            if isinstance(dnaData, DNAData):
                area = ZoneUtil.getCanonicalZoneId(zoneId)
                foundTables = self.findAndCreateSeats(dnaData, zoneId, area, overrideDNAZone=True)
                self.seats += foundTables

        for seat in self.seats:
            seat.start()
            self.addDistObj(seat)

        return