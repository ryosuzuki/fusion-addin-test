from . import TestCommand

commandName = 'Test'
commandDescription = 'Test Command for Fusion 360'
commandResources = './resources'
cmdId = 'cmdID_Test'
myWorkspace = 'FusionSolidEnvironment'
myToolbarPanelID = 'SolidScriptsAddinsPanel'

debug = False

newCommand = TestCommand.TestCommand(commandName, commandDescription, commandResources, cmdId, myWorkspace, myToolbarPanelID, debug)


def run(context):
  newCommand.onRun()

def stop(context):
  newCommand.onStop()
