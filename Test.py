from . import TestCommand
from . import VisualizeCommand
from . import ImportCommand

testCommand = TestCommand.TestCommand('Test', '', './resources', 'test', 'FusionSolidEnvironment', 'SolidScriptsAddinsPanel', False)
visualizeCommand = VisualizeCommand.VisualizeCommand('Visualize', '', './resources', 'visualize', 'FusionSolidEnvironment', 'SolidScriptsAddinsPanel', False)
importCommand = ImportCommand.ImportCommand('Import', '', './resources', 'import', 'FusionSolidEnvironment', 'SolidScriptsAddinsPanel', False)


def run(context):
  importCommand.onRun()
  testCommand.onRun()
  visualizeCommand.onRun()

def stop(context):
  importCommand.onStop()
  testCommand.onStop()
  visualizeCommand.onStop()
