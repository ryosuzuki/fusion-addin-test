import adsk.core, adsk.fusion, adsk.cam, traceback
import time
import copy
from . import Fusion360CommandBase

class InstructionCommand(Fusion360CommandBase.Fusion360CommandBase):
  def onPreview(self, command, inputs):
    pass

  def onDestroy(self, command, inputs, reason_):
    pass

  def onInputChanged(self, command, inputs, changedInput):
    pass

  def onCreate(self, command, inputs):
     pass

  def onExecute(self, command, inputs):
    self.project = None
    self.projects = []
    self.files = []
    self.projectNames = {}
    self.fileNames = {}
    self.commandId = command.parentCommandDefinition.id
    self.projectCommandId = self.commandId + '_project'
    self.fileCommandId = self.commandId + '_file'

    self.app = adsk.core.Application.get()
    self.ui  = self.app.userInterface

    self.product = self.app.activeProduct
    self.rootComp = self.product.rootComponent
    self.design = adsk.fusion.Design.cast(self.product)
    self.rootComp = self.design.rootComponent
    self.view = self.app.activeViewport

    self.animate()
    return


  def animate(self):
    self.show(['structure_0'])
    time.sleep(1)
    self.insert(['conductive'], 5.0)
    for i in range(10):
      self.insert(['conductive'], -0.5)
      time.sleep(0.1)
    time.sleep(1)
    self.show(['structure', 'conductive'])
    time.sleep(1)
    self.sculpt(['base_structure_1'])
    time.sleep(1)
    self.sculpt(['base_structure_1', 'base_conductive_0'])
    time.sleep(1)
    self.sculpt(['base_structure', 'base_conductive'])

  def show(self, keywords):
    for i in range(self.rootComp.bRepBodies.count):
      body = self.rootComp.bRepBodies.item(i)
      if any(x in body.name for x in keywords):
        body.isLightBulbOn = True
      else:
        body.isLightBulbOn = False
    self.view.refresh()


  def insert(self, keywords, offset):
    vector = adsk.core.Vector3D.create(0.0, 0.0, offset)
    transform = adsk.core.Matrix3D.create()
    transform.translation = vector

    bodies = adsk.core.ObjectCollection.create()
    for i in range(self.rootComp.bRepBodies.count):
      body = self.rootComp.bRepBodies.item(i)
      if any(x in body.name for x in keywords):
        body.isLightBulbOn = True
        bodies.add(body)

    moveFeats = self.rootComp.features.moveFeatures
    moveFeatureInput = moveFeats.createInput(bodies, transform)
    moveFeats.add(moveFeatureInput)
    self.view.refresh()


  def sculpt(self, keywords):
    for i in range(self.rootComp.bRepBodies.count):
      body = self.rootComp.bRepBodies.item(i)
      if any(x in body.name for x in keywords):
        body.isLightBulbOn = False
      else:
        body.isLightBulbOn = True
    self.view.refresh()


