import sys

from panda3d.core import *

if __debug__:
    if len(sys.argv) == 2 and sys.argv[1] == '--dummy':
        loadPrcFile('config/general.prc')
        loadPrcFile('config/dev.prc')

        # The VirtualFileSystem, which has already initialized, doesn't see the mount
        # directives in the config(s) yet. We have to force it to load those manually:
        vfs = VirtualFileSystem.getGlobalPtr()
        mounts = ConfigVariableList('vfs-mount')
        for mount in mounts:
            mountFile, mountPoint = (mount.split(' ', 2) + [None, None, None])[:2]
            vfs.mount(Filename(mountFile), Filename(mountPoint), 0)

import __builtin__

class game:
    name = 'toontown'
    process = 'client'


__builtin__.game = game()
import time
import os
import random
import __builtin__
try:
    launcher
except:
    from toontown.launcher.TTOffDummyLauncher import TTOffDummyLauncher
    launcher = TTOffDummyLauncher()
    __builtin__.launcher = launcher

launcher.setRegistry('EXIT_PAGE', 'normal')
pollingDelay = 0.5
print 'ToontownStart: Polling for game2 to finish...'
while not launcher.getGame2Done():
    time.sleep(pollingDelay)

print 'ToontownStart: Game2 is finished.'
print 'ToontownStart: Starting the game.'
if launcher.isDummy():
    http = HTTPClient()
else:
    http = launcher.http
tempLoader = Loader()
backgroundNode = tempLoader.loadSync(Filename('phase_3/models/gui/loading-background'))
from direct.gui import DirectGuiGlobals
print 'ToontownStart: setting default font'
import ToontownGlobals
DirectGuiGlobals.setDefaultFontFunc(ToontownGlobals.getInterfaceFont)
launcher.setPandaErrorCode(7)
import ToonBase
ToonBase.ToonBase()
if base.win == None:
    print 'Unable to open window; aborting.'
    sys.exit()
launcher.setPandaErrorCode(0)
launcher.setPandaWindowOpen()
ConfigVariableDouble('decompressor-step-time').setValue(0.01)
ConfigVariableDouble('extractor-step-time').setValue(0.01)
backgroundNodePath = aspect2d.attachNewNode(backgroundNode, 0)
backgroundNodePath.setPos(0.0, 0.0, 0.0)
backgroundNodePath.setScale(aspect2d, VBase3(1.33, 1, 1))
backgroundNodePath.find('**/fg').setBin('fixed', 20)
backgroundNodePath.find('**/bg').setBin('fixed', 10)
backgroundNodePath.find('**/bg').setScale(aspect2d, VBase3(base.getAspectRatio(), 1, 1))
base.graphicsEngine.renderFrame()
DirectGuiGlobals.setDefaultRolloverSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg'))
DirectGuiGlobals.setDefaultClickSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_create_toon_fwd.ogg'))
DirectGuiGlobals.setDefaultDialogGeom(loader.loadModel('phase_3/models/gui/dialog_box_gui'))
import TTLocalizer
from otp.otpbase import OTPGlobals
OTPGlobals.setDefaultProductPrefix(TTLocalizer.ProductPrefix)
if base.musicManagerIsValid:
    music = base.musicManager.getSound('phase_3/audio/bgm/tt_theme.ogg')
    if music:
        music.setLoop(1)
        music.setVolume(0.9)
        music.play()
    print 'ToontownStart: Loading default gui sounds'
    DirectGuiGlobals.setDefaultRolloverSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg'))
    DirectGuiGlobals.setDefaultClickSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_create_toon_fwd.ogg'))
else:
    music = None
import ToontownLoader
from direct.gui.DirectGui import *
serverVersion = base.config.GetString('server-version', 'no_version_set')
print 'ToontownStart: serverVersion: ', serverVersion
version = OnscreenText(serverVersion, parent=base.a2dBottomLeft, pos=(0.033, 0.025), scale=0.06, fg=Vec4(0, 0, 1, 0.6), align=TextNode.ALeft)
loader.beginBulkLoad('init', TTLocalizer.LoaderLabel, 138, 0, TTLocalizer.TIP_NONE)
from ToonBaseGlobal import *
from direct.showbase.MessengerGlobal import *
from toontown.distributed import ToontownClientRepository
cr = ToontownClientRepository.ToontownClientRepository(serverVersion, launcher)
cr.music = music
del music
base.initNametagGlobals()
base.cr = cr
loader.endBulkLoad('init')
from otp.friends import FriendManager
from otp.distributed.OtpDoGlobals import *
cr.generateGlobalObject(OTP_DO_ID_FRIEND_MANAGER, 'FriendManager')
if not launcher.isDummy():
    base.startShow(cr, launcher.getGameServer())
else:
    base.startShow(cr)
backgroundNodePath.reparentTo(hidden)
backgroundNodePath.removeNode()
del backgroundNodePath
del backgroundNode
del tempLoader
version.cleanup()
del version
base.loader = base.loader
__builtin__.loader = base.loader
autoRun = ConfigVariableBool('toontown-auto-run', 1)


'''
"Injector"
added by freshollie
Works exactly like the conventional injector
'''

import Tkinter
import traceback
import os
import __main__

class Injector(object):
    
    def __init__(self):
        self.firstTick=True
        self.loading=None
        self.root=Tkinter.Tk()
        title='Injector'
        self.root.title(title)

        f = Tkinter.Frame(self.root)
        f.pack()

        xscrollbar = Tkinter.Scrollbar(f, orient=Tkinter.HORIZONTAL)
        xscrollbar.grid(row=1, column=0, sticky=Tkinter.N+Tkinter.S+Tkinter.E+Tkinter.W)

        yscrollbar = Tkinter.Scrollbar(f)
        yscrollbar.grid(row=0, column=1, sticky=Tkinter.N+Tkinter.S+Tkinter.E+Tkinter.W)

        self.text = Tkinter.Text(f, wrap=Tkinter.NONE,
                    xscrollcommand=xscrollbar.set,
                    yscrollcommand=yscrollbar.set)
        self.text.bind("<Control-Key-a>", self.select_all)
        self.text.bind("<Control-Key-A>", self.select_all)
        self.text.grid(row=0, column=0)

        xscrollbar.config(command=self.text.xview)
        yscrollbar.config(command=self.text.yview)

        self.button=Tkinter.Button(self.root,text='Inject',command=self.pressed)
        self.button.pack()
        
    def select_all(self,event):
        self.text.tag_add(Tkinter.SEL, "1.0", Tkinter.END)
        self.text.mark_set(Tkinter.INSERT, "1.0")
        self.text.see(Tkinter.INSERT)
        return 'break'

    def pressed(self):
        exec injection in __main__.__dict__

    def loadScripts(self):
        if not os.path.exists('mods'):
            os.makedirs('mods')
        for scriptName in os.listdir('mods'):
            split=scriptName.split('.')
            if len(split)>1:
                try:
                    execfile('mods/'+scriptName,globals())
                except Exception, err:
                    print(traceback.format_exc())
        self.firstTick=False
                    
    

    def tick(self,task):
        if self.firstTick:
            self.loadScripts()
            self.firstTick=False
        else:
            self.root.update()
        return task.cont
    
injector=Injector()

injection='''
from toontown.toonbase.ToontownStart import *
try:
    contents = injector.text.get(1.0, Tkinter.END)
    exec(contents,globals(),locals())
except Exception, err:
    print(traceback.format_exc())
'''
taskMgr.add(injector.tick,'test')

if autoRun and launcher.isDummy() and (not Thread.isTrueThreads() or __name__ == '__main__'):
    try:
        base.run()
    except SystemExit:
        raise
    except:
        from otp.otpbase import PythonUtil
        print PythonUtil.describeException()
        raise
