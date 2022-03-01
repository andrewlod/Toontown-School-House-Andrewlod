from direct.directnotify import DirectNotifyGlobal
import HoodDataAI, ZoneUtil
from toontown.toonbase import ToontownGlobals
#from toontown.safezone import NPTreasurePlannerAI
from panda3d.core import *
from panda3d.toontown import *
import string
if __debug__:
    import pdb

class NPHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('NPHoodDataAI')

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.NewPlayground
        if zoneId == None:
            zoneId = hoodId
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
        return

    def startup(self):
        HoodDataAI.HoodDataAI.startup(self)
        #self.treasurePlanner = NPTreasurePlannerAI.NPTreasurePlannerAI(self.zoneId)
        #self.treasurePlanner.start()

