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
    app = adsk.core.Application.get()
    ui  = app.userInterface
    product = app.activeProduct
    rootComp = product.rootComponent
    extrudes = rootComp.features.extrudeFeatures
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent

    materialLib = app.materialLibraries.itemByName("Fusion 360 Appearance Library")
    appearance = materialLib.appearances.itemByName("Plastic - Matte (Yellow)") # "Paint - Enamel Glossy (Yellow)"

    targetBodies = adsk.core.ObjectCollection.create()
    toolBodies = adsk.core.ObjectCollection.create()

    yPos = 0
    yMax = 0

    rMax = 0

    for i in range(rootComp.bRepBodies.count):
      body = rootComp.bRepBodies.item(i)
      box = body.boundingBox
      targetBodies.add(body)

      if body.name.find("sheet") == 0:
        toolBodies.add(body)
      # else:

      if body.name.find("sheet") == 0:
        if (yPos < box.minPoint.y):
          yPos = box.minPoint.y

      if (yMax < box.maxPoint.y):
        yMax = box.maxPoint.y

      tMax = max(abs(box.maxPoint.x), abs(box.minPoint.x), abs(box.maxPoint.z), abs(box.minPoint.z))
      if rMax < tMax:
        rMax = tMax

    rMax = rMax * 2
    # ui.messageBox("%f %f %f" % (yPos, yMax, rMax))

    resultBodies = adsk.core.ObjectCollection.create()


    # 0 -- yPos

    originalBodies = copy.copy(targetBodies)
    sketches = rootComp.sketches
    sketch = sketches.add(rootComp.xZConstructionPlane)
    sketchCircles = sketch.sketchCurves.sketchCircles
    centerPoint = adsk.core.Point3D.create(0, 0, 0)
    circle = sketchCircles.addByCenterRadius(centerPoint, rMax)
    prof = sketch.profiles.item(0)
    distance = adsk.core.ValueInput.createByReal(yPos)
    temp = extrudes.addSimple(prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    body = temp.bodies.item(0)

    combineFeatures = rootComp.features.combineFeatures
    combineInput = combineFeatures.createInput(body, targetBodies)
    combineInput.isKeepToolBodies = True
    combineInput.operation = adsk.fusion.FeatureOperations.IntersectFeatureOperation
    result = combineFeatures.add(combineInput)
    resultBodies = adsk.core.ObjectCollection.create()
    for body in result.bodies:
      body.name = "structure"
      resultBodies.add(body)



    # yPos -- yPos+0.1

    basePlane = rootComp.xZConstructionPlane
    planes = rootComp.constructionPlanes
    planeInput = planes.createInput()
    offset = adsk.core.ValueInput.createByReal(yPos)
    planeInput.setByOffset(basePlane, offset)
    planeOne = planes.add(planeInput)

    sketches = rootComp.sketches
    sketch = sketches.add(planeOne)
    sketchCircles = sketch.sketchCurves.sketchCircles
    centerPoint = adsk.core.Point3D.create(0, 0, 0)
    circle = sketchCircles.addByCenterRadius(centerPoint, rMax)
    prof = sketch.profiles.item(0)
    distance = adsk.core.ValueInput.createByReal(0.1)
    temp = extrudes.addSimple(prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    body = temp.bodies.item(0)

    combineFeatures = rootComp.features.combineFeatures
    combineInput = combineFeatures.createInput(body, targetBodies)
    combineInput.isKeepToolBodies = True
    combineInput.operation = adsk.fusion.FeatureOperations.IntersectFeatureOperation
    result = combineFeatures.add(combineInput)
    resultBodies = adsk.core.ObjectCollection.create()

    for body in result.bodies:
      body.name = "conductive"
      body.appearance = appearance
      resultBodies.add(body)

    vector = adsk.core.Vector3D.create(0.0, 2.0, 0.0)
    transform = adsk.core.Matrix3D.create()
    transform.translation = vector

    moveFeats = rootComp.features.moveFeatures
    moveFeatureInput = moveFeats.createInput(resultBodies, transform)
    moveFeats.add(moveFeatureInput)

    # yPos + 0.1 -- yMax

    basePlane = rootComp.xZConstructionPlane
    planes = rootComp.constructionPlanes
    planeInput = planes.createInput()
    offset = adsk.core.ValueInput.createByReal(yPos+0.1)
    planeInput.setByOffset(basePlane, offset)
    planeOne = planes.add(planeInput)

    sketches = rootComp.sketches
    sketch = sketches.add(planeOne)
    sketchCircles = sketch.sketchCurves.sketchCircles
    centerPoint = adsk.core.Point3D.create(0, 0, 0)
    circle = sketchCircles.addByCenterRadius(centerPoint, rMax)
    prof = sketch.profiles.item(0)
    distance = adsk.core.ValueInput.createByReal(yMax - (yPos + 0.1))
    temp = extrudes.addSimple(prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    body = temp.bodies.item(0)

    combineFeatures = rootComp.features.combineFeatures
    combineInput = combineFeatures.createInput(body, originalBodies)
    # combineInput.isKeepToolBodies = True
    combineInput.operation = adsk.fusion.FeatureOperations.IntersectFeatureOperation
    result = combineFeatures.add(combineInput)
    resultBodies = adsk.core.ObjectCollection.create()
    for body in result.bodies:
      body.name = "structure"
      resultBodies.add(body)

    vector = adsk.core.Vector3D.create(0.0, 2.0*2, 0.0)
    transform = adsk.core.Matrix3D.create()
    transform.translation = vector

    moveFeats = rootComp.features.moveFeatures
    moveFeatureInput = moveFeats.createInput(resultBodies, transform)
    moveFeats.add(moveFeatureInput)


  # resultBodies = adsk.core.ObjectCollection.create()
  # for body in result.bodies:
  #   body.name = "result"
  #   body.appearance = appearance
  #   resultBodies.add(body)


  # for i in range(rootComp.bRepBodies.count):
  #   body = rootComp.bRepBodies.item(i)
  #   if body.name.find("sheet") == 0:
      # body.appearance = appearance
      # toolBodies.add(body)
