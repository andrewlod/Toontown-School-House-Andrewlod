from panda3d.core import *
from direct.distributed.ClockDelta import *
from direct.task.Task import Task
from direct.interval.IntervalGlobal import *
from TrolleyConstants import *
from toontown.golf import GolfGlobals
from toontown.toonbase import ToontownGlobals
from direct.distributed import DistributedObject
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import ClassicFSM, State
from direct.fsm import State
from toontown.distributed import DelayDelete
from toontown.toonbase.ToontownTimer import ToontownTimer
from direct.task.Task import Task
from direct.showbase import PythonUtil
from toontown.toon import ToonDNA
from direct.showbase import RandomNumGen
from toontown.battle.BattleSounds import *

class DistributedSeat(DistributedObject.DistributedObject):
    seatState = Enum('Empty, Full')
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSeat')

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.localToonOnBoard = 0
        self.random = None
        self.fsm = ClassicFSM.ClassicFSM('DistributedTrolley', [State.State('off', self.enterOff, self.exitOff, ['waitEmpty', 'waitCountdown']), State.State('waitEmpty', self.enterWaitEmpty, self.exitWaitEmpty, ['waitCountdown']), State.State('waitCountdown', self.enterWaitCountdown, self.exitWaitCountdown, ['waitEmpty'])], 'off', 'off')
        self.fsm.enterInitialState()
        self.__toonTracks = {}
        self.loader = self.cr.playGame.hood.loader
        self.fullSeat = []
        self.fullSeat.append(self.seatState.Empty)
        return

    def announceGenerate(self):
        self.seat = self.loader.geom.find('**/*restaurant_chair_' + str(self.tableNumber))
        self.seatSphereNodes = []
        self.numSeats = 1
        self.seats = []
        self.jumpOffsets = []
        self.pivot = self.seat.find('**/seat1')
        self.basket = None
        for i in xrange(self.numSeats):
            self.seats.append(self.seat.find('**/*seat%d' % (i + 1)))
            self.jumpOffsets.append(self.seat.find('**/*jumpOut%d' % (i + 1)))

        DistributedObject.DistributedObject.announceGenerate(self)
        for i in xrange(self.numSeats):
            self.seatSphereNodes.append(self.seats[i].attachNewNode(CollisionNode('seat_sphere_%d_%d' % (self.getDoId(), i))))
            self.seatSphereNodes[i].node().addSolid(CollisionSphere(-15, 0, 0, 25))

        self.seatNumber = 0
        return

    def disable(self):
        DistributedObject.DistributedObject.disable(self)
        self.fsm.request('off')
        self.clearToonTracks()
        for i in xrange(self.numSeats):
            del self.seatSphereNodes[0]

        del self.seatSphereNodes
        self.notify.debug('Deleted self loader ' + str(self.getDoId()))
        self.seat.removeNode()
        return

    def delete(self):
        self.notify.debug('Golf kart getting deleted: %s' % self.getDoId())
        DistributedObject.DistributedObject.delete(self)
        del self.fsm

    def setState(self, state, seed, timestamp):
        self.seed = seed
        if not self.random:
            self.random = RandomNumGen.RandomNumGen(seed)
        self.fsm.request(state, [globalClockDelta.localElapsedTime(timestamp)])

    def handleEnterSeatSphere(self, i, collEntry):
        self.seatNumber = i
        self.notify.debug('Entering Seat Sphere.... %s' % self.getDoId())
        self.loader.place.detectedSeatSphereCollision(self)

    def handleEnterSeat(self, i):
        toon = base.localAvatar
        self.sendUpdate('requestBoard', [i])

    def fillSlot0(self, avId):
        self.fillSlot(0, avId)

    def fillSlot(self, index, avId):
        self.notify.debug('fill Slot: %d for %d' % (index, avId))
        if avId == 0:
            pass
        else:
            self.fullSeat[index] = self.seatState.Full
            if avId == base.localAvatar.getDoId():
                side = 1
                if hasattr(self.loader.place, 'trolley'):
                    self.loader.place.trolley.fsm.request('boarding', [self.pivot, side])
                else:
                    self.notify.warning('fillSlot no trolley in place')
                self.localToonOnBoard = 1
            if avId == base.localAvatar.getDoId():
                if hasattr(self.loader.place, 'trolley'):
                    self.loader.place.trolley.fsm.request('boarded')
                    self.loader.place.trolley.exitButton.hide()
            if avId in self.cr.doId2do:
                toon = self.cr.doId2do[avId]
                toon.stopSmooth()
                toon.wrtReparentTo(self.pivot)
                sitStartDuration = toon.getDuration('sit-start')
                jumpTrack = self.generateToonJumpTrack(toon, index)
                track = Sequence(jumpTrack, Func(toon.setAnimState, 'Sit', 1.0))
                self.notify.debug('### fillSlot: fullSeat = %s' % self.fullSeat)
                if self.fullSeat.count(0) == 3:
                    self.notify.debug('### fillSlot: adding basketAppear')
                track.append(Sequence(Func(self.clearToonTrack, avId), name=toon.uniqueName('fillTrolley'), autoPause=1))
                if avId == base.localAvatar.getDoId():
                    if hasattr(self.loader.place, 'trolley'):
                        track.append(Func(self.loader.place.trolley.exitButton.show))
                track.delayDelete = DelayDelete.DelayDelete(toon, 'Seat.fillSlot')
                self.storeToonTrack(avId, track)
                track.start()

    def emptySlot0(self, avId, timestamp):
        self.emptySlot(0, avId, timestamp)

    def notifyToonOffTrolley(self, toon):
        toon.setAnimState('neutral', 1.0)
        if hasattr(base, 'localAvatar') and toon == base.localAvatar:
            if hasattr(self.loader.place, 'trolley'):
                self.loader.place.trolley.handleOffTrolley()
            self.localToonOnBoard = 0
        else:
            toon.startSmooth()

    def emptySlot(self, index, avId, timestamp):

        def emptySeat(index):
            self.notify.debug('### seat %s now empty' % index)
            self.fullSeat[index] = self.seatState.Empty

        if avId == 0:
            pass
        elif avId == 1:
            self.fullSeat[index] = self.seatState.Empty
            self.notify.debug('### empty slot - unexpetected: fullSeat = %s' % self.fullSeat)
        else:
            self.fullSeat[index] = self.seatState.Empty
            if avId in self.cr.doId2do:
                toon = self.cr.doId2do[avId]
                toon.stopSmooth()
                sitStartDuration = toon.getDuration('sit-start')
                jumpOutTrack = self.generateToonReverseJumpTrack(toon, index)
                track = Sequence(jumpOutTrack)
                self.notify.debug('### empty slot: fullSeat = %s' % self.fullSeat)
                track.append(Sequence(Func(self.notifyToonOffTrolley, toon), Func(self.clearToonTrack, avId), Func(self.doneExit, avId), Func(emptySeat, index), name=toon.uniqueName('emptyTrolley'), autoPause=1))
                track.delayDelete = DelayDelete.DelayDelete(toon, 'Seat.emptySlot')
                self.storeToonTrack(avId, track)
                track.start()

    def rejectBoard(self, avId):
        self.loader.place.trolley.handleRejectBoard()

    def __enableCollisions(self):
        for i in xrange(self.numSeats):
            self.accept('enterseat_sphere_%d_%d' % (self.getDoId(), i), self.handleEnterSeatSphere, [i])
            self.accept('enterseatOK_%d_%d' % (self.getDoId(), i), self.handleEnterSeat, [i])
            self.seatSphereNodes[i].setCollideMask(ToontownGlobals.WallBitmask)

    def __disableCollisions(self):
        for i in xrange(self.numSeats):
            self.ignore('enterseat_sphere_%d_%d' % (self.getDoId(), i))
            self.ignore('enterseatOK_%d_%d' % (self.getDoId(), i))

        for i in xrange(self.numSeats):
            self.seatSphereNodes[i].setCollideMask(BitMask32(0))

    def enterOff(self):
        return None

    def exitOff(self):
        return None

    def enterWaitEmpty(self, ts):
        self.__enableCollisions()

    def exitWaitEmpty(self):
        self.__disableCollisions()

    def enterWaitCountdown(self, ts):
        self.__enableCollisions()
        self.accept('trolleyExitButton', self.handleExitButton)

    def handleExitButton(self):
        self.sendUpdate('requestExit')

    def exitWaitCountdown(self):
        self.__disableCollisions()
        self.ignore('trolleyExitButton')

    def getStareAtNodeAndOffset(self):
        return (self.pivot, Point3(0, 0, 4))

    def storeToonTrack(self, avId, track):
        self.clearToonTrack(avId)
        self.__toonTracks[avId] = track

    def clearToonTrack(self, avId):
        oldTrack = self.__toonTracks.get(avId)
        if oldTrack:
            oldTrack.pause()
            DelayDelete.cleanupDelayDeletes(oldTrack)
            del self.__toonTracks[avId]

    def clearToonTracks(self):
        keyList = []
        for key in self.__toonTracks:
            keyList.append(key)

        for key in keyList:
            if key in self.__toonTracks:
                self.clearToonTrack(key)

    def doneExit(self, avId):
        if avId == base.localAvatar.getDoId():
            self.sendUpdate('doneExit')

    def setPosHpr(self, x, y, z, h, p, r):
        self.startingPos = Vec3(x, y, z)
        self.enteringPos = Vec3(x, y, z - 10)
        self.startingHpr = Vec3(h, 0, 0)

    def setTableNumber(self, tn):
        self.tableNumber = tn

    def generateToonJumpTrack(self, av, seatIndex):
        av.pose('sit', 47)
        hipOffset = av.getHipsParts()[2].getPos(av)

        def getToonJumpTrack(av, seatIndex):

            def getJumpDest(av = av, node = self.pivot):
                dest = Vec3(self.pivot.getPos(av.getParent()))
                seatNode = self.seat.find('**/seat' + str(seatIndex + 1))
                dest += seatNode.getPos(self.pivot)
                dna = av.getStyle()
                dest -= hipOffset
                if seatIndex == 2 or seatIndex == 3:
                    dest.setY(dest.getY() + 2 * hipOffset.getY())
                dest.setZ(dest.getZ() + 0.2)
                return dest

            def getJumpHpr(av = av, node = self.pivot):
                hpr = self.seats[seatIndex].getHpr(av.getParent())
                angle = PythonUtil.fitDestAngle2Src(av.getH(), hpr.getX())
                hpr.setX(angle)
                return hpr

            toonJumpTrack = Parallel(ActorInterval(av, 'jump'), Sequence(Wait(0.43), Parallel(LerpHprInterval(av, hpr=getJumpHpr, duration=0.9), ProjectileInterval(av, endPos=getJumpDest, duration=0.9))))
            return toonJumpTrack

        def getToonSitTrack(av):
            toonSitTrack = Sequence(ActorInterval(av, 'sit-start'), Func(av.loop, 'sit'))
            return toonSitTrack

        toonJumpTrack = getToonJumpTrack(av, seatIndex)
        toonSitTrack = getToonSitTrack(av)
        jumpTrack = Sequence(Parallel(toonJumpTrack, Sequence(Wait(1), toonSitTrack)), Func(av.wrtReparentTo, self.pivot))
        return jumpTrack

    def generateToonReverseJumpTrack(self, av, seatIndex):
        self.notify.debug('av.getH() = %s' % av.getH())

        def getToonJumpTrack(av, destNode):

            def getJumpDest(av = av, node = destNode):
                dest = node.getPos(self.pivot)
                dest += self.jumpOffsets[seatIndex].getPos(self.pivot)
                return dest

            def getJumpHpr(av = av, node = destNode):
                hpr = node.getHpr(av.getParent())
                hpr.setX(hpr.getX() + 180)
                angle = PythonUtil.fitDestAngle2Src(av.getH(), hpr.getX())
                hpr.setX(angle)
                return hpr

            toonJumpTrack = Parallel(ActorInterval(av, 'jump'), Sequence(Wait(0.1), Parallel(ProjectileInterval(av, endPos=getJumpDest, duration=0.9))))
            return toonJumpTrack

        toonJumpTrack = getToonJumpTrack(av, self.pivot)
        jumpTrack = Sequence(toonJumpTrack, Func(av.loop, 'neutral'), Func(av.wrtReparentTo, render))
        return jumpTrack

    def destroy(self, node):
        node.removeNode()
        node = None
        return

    def setSeatDone(self):
        if self.localToonOnBoard:
            if hasattr(self.loader.place, 'trolley'):
                self.loader.place.trolley.fsm.request('final')
                self.loader.place.trolley.fsm.request('start')
            self.localToonOnBoard = 0
            messenger.send('seatDone')
