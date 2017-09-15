from . import TestCommand
from . import ImportCommand
from . import GenerateCommand
from . import VisualizeCommand
from . import InstructionCommand

testCommand = TestCommand.TestCommand('Test', '', './resources', 'test', 'FusionSolidEnvironment', 'SolidScriptsAddinsPanel', False)
generateCommand = GenerateCommand.GenerateCommand('Generate', '', './resources', 'generate', 'FusionSolidEnvironment', 'SolidScriptsAddinsPanel', False)
importCommand = ImportCommand.ImportCommand('Import', '', './resources', 'import', 'FusionSolidEnvironment', 'SolidScriptsAddinsPanel', False)
visualizeCommand = GenerateCommand.VisualizeCommand('Visualize', '', './resources', 'visualize', 'FusionSolidEnvironment', 'SolidScriptsAddinsPanel', False)
instructionCommand = InstructionCommand.InstructionCommand('Download', '', './resources', 'instruction', 'FusionSolidEnvironment', 'SolidScriptsAddinsPanel', False)


def run(context):
  importCommand.onRun()
  generateCommand.onRun()
  visualizeCommand.onRun()
  instructionCommand.onRun()

def stop(context):
  importCommand.onStop()
  generateCommand.onStop()
  visualizeCommand.onStop()
  instructionCommand.onStop()
