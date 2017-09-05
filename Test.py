from . import TestCommand
from . import VisualizeCommand
from . import ImportCommand
from . import InstructionCommand

testCommand = TestCommand.TestCommand('Test', '', './resources', 'test', 'FusionSolidEnvironment', 'SolidScriptsAddinsPanel', False)
visualizeCommand = VisualizeCommand.VisualizeCommand('Visualize', '', './resources', 'visualize', 'FusionSolidEnvironment', 'SolidScriptsAddinsPanel', False)
importCommand = ImportCommand.ImportCommand('Import', '', './resources', 'import', 'FusionSolidEnvironment', 'SolidScriptsAddinsPanel', False)
instructionCommand = InstructionCommand.InstructionCommand('Instruction', '', './resources', 'Instruction', 'FusionSolidEnvironment', 'SolidScriptsAddinsPanel', False)


def run(context):
  importCommand.onRun()
  visualizeCommand.onRun()
  instructionCommand.onRun()

def stop(context):
  importCommand.onStop()
  visualizeCommand.onStop()
  instructionCommand.onStop()
