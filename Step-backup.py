import adsk.core, adsk.fusion, adsk.cam, traceback
import copy
from . import Fusion360CommandBase

class VisualizeCommand(Fusion360CommandBase.Fusion360CommandBase):
  def onPreview(self, command, inputs):
    pass

  def onDestroy(self, command, inputs, reason_):
    pass

  def onInputChanged(self, command, inputs, changedInput):
    # product = self.app.activeProduct
    # rootComp = product.rootComponent

    # # for i in range(rootComp.bRepBodies.count):
    # body = rootComp.bRepBodies.item(0)
    # body.isLightBulbOn = True
    # body.deleteMe()

    # # materialLib = self.app.materialLibraries.itemByName("Fusion 360 Appearance Library")
    # # appearance = materialLib.appearances.itemByName("Plastic - Matte (Yellow)") # "Paint - Enamel Glossy (Yellow)"
    # # body.appearance = appearance
    # # body.name = 'hoge'

    # self.ui.messageBox('hoge')
    self.init()
    return

    # if changedInput.id == self.commandId + '_button':
    #   # sketch = self.component.sketches.item(0)
    #   # fileDialog = self.ui.createFileDialog()
    #   # fileDialog.title = "Save DXF file"
    #   # fileDialog.initialFilename = "test.dxf"
    #   # dialogResult = fileDialog.showSave()
    #   # if (dialogResult == adsk.core.DialogResults.DialogOK):
    #   #   filepath = fileDialog.filename
    #   #   sketch.saveAsDXF(filepath)

    #   for i in range(self.rootComp.bRepBodies.count):
    #     body = self.rootComp.bRepBodies.item(i)
    #     body.isLightBulbOn = False


    # if changedInput.id == "APITabBar":
    #   if command.commandInputs.itemById(self.commandId + "_step_1").isActive:
    #     for i in range(self.rootComp.bRepBodies.count):
    #       body = self.rootComp.bRepBodies.item(i)
    #       if body.name.find('structure_0') == 0:
    #         self.ui.messageBox(body.name)
    #         # body.isLightBulbOn = True
    #       else:
    #         # body.isLightBulbOn = False
    #         body

    #   if command.commandInputs.itemById(self.commandId + "_step_2").isActive:
    #     bodies = adsk.core.ObjectCollection.create()
    #     for i in range(self.rootComp.bRepBodies.count):
    #       body = self.rootComp.bRepBodies.item(i)
    #       if body.name.find('structure_0') == 0 or body.name.find('conductive_0') == 0:
    #         body.isLightBulbOn = True
    #       else:
    #         body.isLightBulbOn = False
    #       bodies.add(body)

    #     vector = adsk.core.Vector3D.create(0.0, 2.0, 0.0)
    #     transform = adsk.core.Matrix3D.create()
    #     transform.translation = vector

    #     moveFeats = self.rootComp.features.moveFeatures
    #     moveFeatureInput = moveFeats.createInput(bodies, transform)
    #     moveFeats.add(moveFeatureInput)

    #   if command.commandInputs.itemById(self.commandId + "_step_3").isActive:
    #     for i in range(self.rootComp.bRepBodies.count):
    #       body = self.rootComp.bRepBodies.item(i)
    #       if body.name.find('structure') == 0 or body.name.find('conductive') == 0:
    #         body.isLightBulbOn = True
    #       else:
    #         body.isLightBulbOn = False


  def onCreate(self, command, inputs):
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
    command.setDialogInitialSize(400, 800)


    # Step 1
    tabInput = inputs.addTabCommandInput(self.commandId + '_step_1', 'Step 1')
    tabChildren = tabInput.children
    image = tabChildren.addImageCommandInput(self.commandId + '_image', 'Image', "resources/step-1.png")
    image.isFullWidth = True
    tabChildren.addBoolValueInput(self.commandId + '_button', 'Download DXF', False)
    # tabChildren.addButtonRowCommandInput(self.commandId + '_button', 'Download DXF', False)

    # Step 2
    tabInput = inputs.addTabCommandInput(self.commandId + '_step_2', 'Step 2')
    tabChildren = tabInput.children

    # Step 3
    tabInput = inputs.addTabCommandInput(self.commandId + '_step_3', 'Step 3')
    tabChildren = tabInput.children
    tabChildren.addTextBoxCommandInput(self.commandId + '_textBox', 'Text Box', 'This is an example of Text Box. It is readonly.', 2, True)
    # self.init()


  def onExecute(self, command, inputs):
    # (objects, plane, edge, spacing) = getInputs(command, inputs)
    # visualize()
    pass

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
    rMax = 100
    extrudes = self.rootComp.features.extrudeFeatures
    basePlane = self.rootComp.xZConstructionPlane
    planes = self.rootComp.constructionPlanes
    planeInput = planes.createInput()
    val = adsk.core.ValueInput.createByReal(height)
    planeInput.setByOffset(basePlane, val)
    plane = planes.add(planeInput)

    originalBodies = copy.copy(self.targetBodies)
    sketches = self.rootComp.sketches
    circleSketch = sketches.add(plane)
    circles = circleSketch.sketchCurves.sketchCircles
    centerPoint = adsk.core.Point3D.create(0, 0, 0)
    circle = circles.addByCenterRadius(centerPoint, rMax)
    prof = circleSketch.profiles.item(0)
    distance = adsk.core.ValueInput.createByReal(offset)
    temp = extrudes.addSimple(prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    body = temp.bodies.item(0)

    combineFeatures = self.rootComp.features.combineFeatures
    combineInput = combineFeatures.createInput(body, self.targetBodies)
    combineInput.isKeepToolBodies = True
    combineInput.operation = adsk.fusion.FeatureOperations.IntersectFeatureOperation
    result = combineFeatures.add(combineInput)
    resultBodies = adsk.core.ObjectCollection.create()
    i = 0
    for body in result.bodies:
      body.name = '%s_%d_%d' % (name, index, i)
      if name.find('conductive') == 0 :
        body.appearance = self.appearance
      resultBodies.add(body)
      i = i + 1
