from panda3d.core import *
import Playground
import random
from direct.fsm import State
from toontown.safezone import Seat
from toontown.launcher import DownloadForceAcknowledge
from toontown.toonbase import ToontownGlobals


class DRPlayground(Playground.Playground):

    def __init__(self, loader, parentFSM, doneEvent):
        Playground.Playground.__init__(self, loader, parentFSM, doneEvent)
        self.light = None
        self.dldr = None
        self.parentFSM = parentFSM
        self.seatBlockDoneEvent = 'seatBlockDone'
        self.fsm.addState(State.State('seatBlock', self.enterSeatBlock, self.exitSeatBlock, ['walk']))
        state = self.fsm.getStateNamed('walk')
        self.loader = base.cr.playGame.hood.loader
        state.addTransition('seatBlock')
        self.seatDoneEvent = 'seatFinalDone'

    def load(self):
        Playground.Playground.load(self)
        self.light = AmbientLight("drlight")
        self.light.setColor((1,1,1,1))
        self.dldr = render.attachNewNode(self.light)
        render.setLight(self.dldr)
        self.mainTable = self.loader.geom.find('**/*dinner_table')
        colNode = self.mainTable.attachNewNode(CollisionNode('collision_mainTable'))
        colNode.node().addSolid(CollisionPolygon(LPoint3(-3,71,2.6), LPoint3(3,71,2.6), LPoint3(3,81,2.6), LPoint3(-3,81,2.6)))
        colNode.node().addSolid(CollisionPolygon(LPoint3(-3,71,0), LPoint3(3,71,0), LPoint3(3,71,2.6), LPoint3(-3,71,2.6)))
        colNode.node().addSolid(CollisionPolygon(LPoint3(-3,81,0), LPoint3(-3,71,0), LPoint3(-3,71,2.6), LPoint3(-3,81,2.6)))
        colNode.node().addSolid(CollisionPolygon(LPoint3(3,81,0), LPoint3(-3,81,0), LPoint3(-3,81,2.6), LPoint3(3,81,2.6)))
        colNode.node().addSolid(CollisionPolygon(LPoint3(3,71,0), LPoint3(3,81,0), LPoint3(3,81,2.6), LPoint3(3,71,2.6)))


    def unload(self):
        render.clearLight(self.dldr)
        del self.light
        del self.dldr
        del self.mainTable
        Playground.Playground.unload(self)

    def doRequestLeave(self, requestStatus):
        self.fsm.request('trialerFA', [requestStatus])

    def enterDFA(self, requestStatus):
        doneEvent = 'dfaDoneEvent'
        self.accept(doneEvent, self.enterDFACallback, [requestStatus])
        self.dfa = DownloadForceAcknowledge.DownloadForceAcknowledge(doneEvent)
        if requestStatus['hoodId'] == ToontownGlobals.MyEstate:
            self.dfa.enter(base.cr.hoodMgr.getPhaseFromHood(ToontownGlobals.MyEstate))
        else:
            self.dfa.enter(5)
    
    def enterSeatBlock(self, seat):
        base.localAvatar.laffMeter.start()
        base.localAvatar.b_setAnimState('off', 1)
        base.localAvatar.cantLeaveGame = 1
        self.accept(self.seatDoneEvent, self.handleSeatDone)
        self.trolley = Seat.Seat(self, self.fsm, self.seatDoneEvent, seat.getDoId(), seat.seatNumber)
        self.trolley.load()
        self.trolley.enter()

    def exitSeatBlock(self):
        base.localAvatar.laffMeter.stop()
        base.localAvatar.cantLeaveGame = 0
        self.ignore(self.trolleyDoneEvent)
        self.trolley.unload()
        self.trolley.exit()
        del self.trolley

    def detectedSeatSphereCollision(self, seat):
        self.fsm.request('seatBlock', [seat])

    def handleStartingBlockDone(self, doneStatus):
        self.notify.debug('handling StartingBlock done event')
        where = doneStatus['where']
        if where == 'reject':
            self.fsm.request('walk')
        elif where == 'exit':
            self.fsm.request('walk')
        elif where == 'racetrack':
            self.doneStatus = doneStatus
            messenger.send(self.doneEvent)
        else:
            self.notify.error('Unknown mode: ' + where + ' in handleStartingBlockDone')

    def handleSeatDone(self, doneStatus):
        self.notify.debug('handling seat done event')
        mode = doneStatus['mode']
        if mode == 'reject':
            self.fsm.request('walk')
        elif mode == 'exit':
            self.fsm.request('walk')
        else:
            self.notify.error('Unknown mode: ' + mode + ' in handleSeatDone')