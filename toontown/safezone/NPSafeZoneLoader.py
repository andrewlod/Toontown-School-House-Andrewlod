from panda3d.core import *
import SafeZoneLoader
import NPPlayground
from toontown.toonbase import ToontownGlobals

class NPSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = NPPlayground.NPPlayground
        self.musicFile = 'phase_6/audio/bgm/OZ_SZ.ogg'
        self.activityMusicFile = 'phase_6/audio/bgm/GS_KartShop.ogg'
        self.dnaFile = 'phase_6/dna/new_playground_sz.dna'
        self.safeZoneStorageDNAFile = 'phase_6/dna/storage_NP_sz.dna'
        self.fences = []
        self.box = None

    def load(self):
        print 'loading NP safezone'
        SafeZoneLoader.SafeZoneLoader.load(self)
        self.box = CollisionNode("fences")
        col = CollisionPolygon(Point3(35.8,49.2,15), Point3(35.8,49.2,0), Point3(788.5,34.6,0), Point3(788.5,34.6,15))
        self.box.addSolid(col)
        self.geom.attachNewNode(self.box)
        dock = loader.loadModel("phase_6/models/neighborhoods/donalds_dock")
        fence = dock.find("**/o210")
        fenceCopy = render.attachNewNode("fence")
        fence.copyTo(fenceCopy)
        fenceCopy.setHpr(67,0,0)
        fenceCopy.setPos(-40,150,6)
        for i in range(15):
            newFence = render.attachNewNode("fence" + str(i+2))
            fenceCopy.copyTo(newFence)
            newFence.setPos(47*(i+1), -i-1,0)
            self.fences.append(newFence)
        self.fences.append(fenceCopy)

    def unload(self):
        SafeZoneLoader.SafeZoneLoader.unload(self)
        for node in self.fences:
            node.removeNode()
        self.fences = []
        del self.box
        self.box = None
