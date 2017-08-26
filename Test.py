from . import TestCommand
from . import VisualizeCommand

name = 'Test'
description = 'Test Command for Fusion 360'
resources = './resources'
cid = 'cmdID_Test'
workspace = 'FusionSolidEnvironment'
pid = 'SolidScriptsAddinsPanel'
debug = False

testCommand = TestCommand.TestCommand(name, description, resources, cid, workspace, pid, debug)

name = 'Visualize'
description = 'Visualize Command for Fusion 360'
resources = './resources'
cid = 'cmdID_Visualize'
workspace = 'FusionSolidEnvironment'
pid = 'SolidScriptsAddinsPanel'
debug = False

visualizeCommand = VisualizeCommand.VisualizeCommand(name, description, resources, cid, workspace, pid, debug)

def run(context):
  testCommand.onRun()
  visualizeCommand.onRun()

def stop(context):
  testCommand.onStop()
  visualizeCommand.onStop()
