from panda3d.core import *
import Playground
import random


class NPPlayground(Playground.Playground):

    def __init__(self, loader, parentFSM, doneEvent):
        Playground.Playground.__init__(self, loader, parentFSM, doneEvent)
        self.light = None
        self.dlnp = None

    def load(self):
        Playground.Playground.load(self)
        self.light = AmbientLight("nplight")
        self.light.setColor((1,1,1,1))
        self.dlnp = render.attachNewNode(self.light)
        render.setLight(self.dlnp)

    def unload(self):
        render.clearLight(self.dlnp)
        del self.light
        del self.dlnp
        Playground.Playground.unload(self)