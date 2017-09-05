import adsk.core, adsk.fusion, adsk.cam, traceback
import copy
from . import Fusion360CommandBase

class VisualizeCommand(Fusion360CommandBase.Fusion360CommandBase):
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
    self.init()


  def init(self):
    self.product = self.app.activeProduct
    self.rootComp = self.product.rootComponent
    self.design = adsk.fusion.Design.cast(self.product)

    materialLib = self.app.materialLibraries.itemByName("Fusion 360 Appearance Library")
    self.appearance = materialLib.appearances.itemByName("Plastic - Matte (Yellow)") # "Paint - Enamel Glossy (Yellow)"

    self.rootComp = self.design.rootComponent
    self.component = self.design.allComponents.itemByName("function")
    sketches = self.component.sketches
    sketch = sketches.item(0)
    extrudes = self.component.features.extrudeFeatures
    plane = sketch.referencePlane
    self.yPos = plane.transform.translation.y
    self.yMax = 0

    self.targetBodies = adsk.core.ObjectCollection.create()
    self.functionBodies = adsk.core.ObjectCollection.create()

    for i in range(self.rootComp.bRepBodies.count):
      body = self.rootComp.bRepBodies.item(i)
      body.isLightBulbOn = False
      box = body.boundingBox
      if (self.yMax < box.maxPoint.y):
        self.yMax = box.maxPoint.y
      self.targetBodies.add(body)

    for i in range(sketch.profiles.count):
      prof = sketch.profiles.item(i)
      distance = adsk.core.ValueInput.createByReal(0.1)
      extrudeInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
      extrudeInput.setDistanceExtent(False, distance)
      extrude = extrudes.add(extrudeInput)

      for body in extrude.bodies:
        body.appearance = self.appearance
        body.isLightBulbOn = False
        body.name = "sheet"
        self.functionBodies.add(body)
        self.targetBodies.add(body)


    self.slice('structure', 0, 0.0, self.yPos)
    self.slice('conductive', 0, self.yPos, 0.1)
    self.slice('structure', 1, self.yPos + 0.1, self.yMax - (self.yPos + 0.1))

    # vector = adsk.core.Vector3D.create(0.0, 2.0, 0.0)
    # transform = adsk.core.Matrix3D.create()
    # transform.translation = vector

    # moveFeats = rootComp.features.moveFeatures
    # moveFeatureInput = moveFeats.createInput(resultBodies, transform)
    # moveFeats.add(moveFeatureInput)

  def slice(self, name, index, height, offset):
    originalBodies = copy.copy(self.targetBodies)
    baseBody = self.createBase(name, index, height, offset)
    combineFeatures = self.rootComp.features.combineFeatures
    combineInput = combineFeatures.createInput(baseBody, self.targetBodies)
    combineInput.isKeepToolBodies = True
    # combineInput.isNewComponent = True
    combineInput.operation = adsk.fusion.FeatureOperations.IntersectFeatureOperation
    result = combineFeatures.add(combineInput)
    resultBodies = adsk.core.ObjectCollection.create()
    i = 0
    # component = result.bodies.item(0).parentComponent
    # component.name = '%s_%d' % (name, index)
    for body in result.bodies:
      body.name = '%s_%d_%d' % (name, index, i)
      if name.find('conductive') == 0 :
        body.appearance = self.appearance
      resultBodies.add(body)
      i = i + 1

    baseBody = self.createBase(name, index, height, offset)
    baseBody.isLightBulbOn = False


  def createBase(self, name, index, height, offset):
    rMax = 100
    extrudes = self.rootComp.features.extrudeFeatures
    basePlane = self.rootComp.xZConstructionPlane
    planes = self.rootComp.constructionPlanes
    planeInput = planes.createInput()
    val = adsk.core.ValueInput.createByReal(height)
    planeInput.setByOffset(basePlane, val)
    plane = planes.add(planeInput)

    sketches = self.rootComp.sketches
    sketch = sketches.add(plane)
    lines = sketch.sketchCurves.sketchLines
    centerPoint = adsk.core.Point3D.create(0, 0, 0)
    cornerPoint = adsk.core.Point3D.create(10, 10, 0)
    rectLines = lines.addCenterPointRectangle(centerPoint, cornerPoint)
    prof = sketch.profiles.item(0)
    distance = adsk.core.ValueInput.createByReal(offset)
    temp = extrudes.addSimple(prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    baseBody = temp.bodies.item(0)
    # baseBody.isLightBulbOnBulbOn = False
    baseBody.name = 'base_%s_%d' % (name, index)
    return baseBody
