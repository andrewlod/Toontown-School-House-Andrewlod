from panda3d.core import *
import SafeZoneLoader
import DRPlayground
from toontown.toonbase import ToontownGlobals
from direct.fsm import ClassicFSM, State

class DRSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = DRPlayground.DRPlayground
        self.musicFile = 'phase_6/audio/bgm/DR_SZ.ogg'
        self.activityMusicFile = 'phase_6/audio/bgm/GS_KartShop.ogg'
        self.dnaFile = 'phase_8/dna/daisy_restaurant_sz.dna'
        self.safeZoneStorageDNAFile = 'phase_8/dna/storage_DR_sz.dna'
        del self.fsm
        self.fsm = ClassicFSM.ClassicFSM('SafeZoneLoader', [State.State('start', self.enterStart, self.exitStart, ['quietZone', 'playground', 'toonInterior']),
         State.State('playground', self.enterPlayground, self.exitPlayground, ['quietZone']),
         State.State('toonInterior', self.enterToonInterior, self.exitToonInterior, ['quietZone']),
         State.State('quietZone', self.enterQuietZone, self.exitQuietZone, ['playground', 'toonInterior']),
         State.State('final', self.enterFinal, self.exitFinal, ['start'])], 'start', 'final')


    def load(self):
        print 'loading DR safezone'
        SafeZoneLoader.SafeZoneLoader.load(self)

    def unload(self):
        SafeZoneLoader.SafeZoneLoader.unload(self)
