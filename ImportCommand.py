import adsk.core, adsk.fusion, adsk.cam, traceback
from . import Fusion360CommandBase

from . import GenerateCommand
from . import TestCommand


componentIndex = 1

class ImportCommand(Fusion360CommandBase.Fusion360CommandBase):
  def onPreview(self, command, inputs):
    pass

  def onDestroy(self, command, inputs, reason_):
    pass

  def onInputChanged(self, command, inputs, changedInput):
    if changedInput.id == self.fileCommandId:
      name = command.commandInputs.itemById(self.fileCommandId).selectedItem.name
      self.file = self.fileNames[name]

    if changedInput.id == self.planeCommandId:
      selection = changedInput.selection(0)
      self.plane = selection.entity

  def onCreate(self, command, inputs):
    self.project = None
    self.projects = []
    self.files = []
    self.projectNames = {}
    self.fileNames = {}

    self.planeCommandId = command.parentCommandDefinition.id + '_plane'
    self.projectCommandId = command.parentCommandDefinition.id + '_project'
    self.fileCommandId = command.parentCommandDefinition.id + '_file'

    self.app = adsk.core.Application.get()
    self.ui  = self.app.userInterface

    selectionPlaneInput = inputs.addSelectionInput(self.planeCommandId, 'Select Base Face', 'Select Face to mate to')
    selectionPlaneInput.setSelectionLimits(1,1)
    selectionPlaneInput.addSelectionFilter('PlanarFaces')

    self.projects = self.app.data.dataProjects
    self.project = self.projects[1]
    self.files = self.project.rootFolder.dataFiles

    self.projectNames[self.project.name] = self.project
    dropdownInput = inputs.addDropDownCommandInput(self.projectCommandId, 'Project', adsk.core.DropDownStyles.TextListDropDownStyle)
    addItemsToDropdown(self.projectNames, dropdownInput)

    self.fileNames = {}
    # self.file = self.files[4]
    # self.fileNames[self.file.name] = self.file
    for file in self.files:
      self.fileNames[file.name] = file

    dropdownInput = inputs.addDropDownCommandInput(self.fileCommandId, 'File', adsk.core.DropDownStyles.TextListDropDownStyle)
    addItemsToDropdown(self.fileNames , dropdownInput)


  def onExecute(self, command, inputs):
    design = self.app.activeProduct
    rootComp = design.rootComponent
    occs = rootComp.occurrences

    planes = rootComp.constructionPlanes
    planeInput = planes.createInput()
    offset = adsk.core.ValueInput.createByReal(0)
    planeInput.setByOffset(self.plane, offset)
    plane = planes.add(planeInput)
    plane.isLightBulbOn = False
    translate = plane.transform.translation

    matrix = adsk.core.Matrix3D.create()
    matrix.translation = adsk.core.Vector3D.create(0, translate.y, 0)

    occ = occs.addByInsert(self.file, matrix, False)
    materialLib = self.app.materialLibraries.itemByName("Fusion 360 Appearance Library")
    appearance = materialLib.appearances.itemByName("Plastic - Matte (Yellow)")
    occ.appearance = appearance

    component = occ.component
    global componentIndex
    component.name = "function-%d" % componentIndex
    componentIndex = componentIndex + 1

    # self.onCreate(command, inputs)
    # testCommand = TestCommand.TestCommand('Visualize', '', './resources', 'visualize', 'FusionSolidEnvironment', 'SolidScriptsAddinsPanel', False)
    # rootComp.occurrences
    # testCommand.onCreate(command, inputs)



    # component = occ.component

    # transform = adsk.core.Matrix3D.create()
    # transform.translation = adsk.core.Vector3D.create(0, 0, 0)


    # collections = adsk.core.ObjectCollection.create()
    # collections.add(component)

    # features = rootComp.features
    # moveFeats = features.moveFeatures
    # moveFeatureInput = moveFeats.createInput(collections, transform)
    # moveFeats.add(moveFeatureInput)


    # sketches = rootComp.sketches


    # component = occ.component
    # face = component.xZConstructionPlane
    # # body = component.bRepBodies.item(0)
    # # face = body.faces[0]


    # geo0 = adsk.fusion.JointGeometry.createByPlanarFace(self.plane, None, adsk.fusion.JointKeyPointTypes.CenterKeyPoint)
    # geo1 = adsk.fusion.JointGeometry.createByPlanarFace(face, None, adsk.fusion.JointKeyPointTypes.CenterKeyPoint)

    # joints = occ.component.joints
    # jointInput = joints.createInput(geo0, geo1)
    # jointInput.setAsPlanarJointMotion(adsk.fusion.JointDirections.YAxisJointDirection)
    # joint = joints.add(jointInput)

    # sketchInOcc = sketches.add(plane)
    # curve = sketchInOcc.sketchCurves.item(0)

    # sketch = sketches.add(planeOne)
    # sketchPts = sketch.sketchPoints
    # point = adsk.core.Point3D.create(1, 0, 1)
    # sketchPt = sketchPts.add(point)
    # sketchCircles = sketch.sketchCurves.sketchCircles
    # centerPoint = adsk.core.Point3D.create(0, 0, 0)
    # circle = sketchCircles.addByCenterRadius(centerPoint, 5.0)

    # # Get the profile defined by the circle
    # prof = sketch.profiles.item(0)

    # # Create an extrusion input and make sure it's in a new component
    # extrudes = rootComp.features.extrudeFeatures
    # extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewComponentFeatureOperation)

    # # Set the extrusion input
    # distance = adsk.core.ValueInput.createByReal(5)
    # extInput.setDistanceExtent(True, distance)
    # extInput.isSolid = True

    # # Create the extrusion
    # ext = extrudes.add(extInput)

    # # Get the end face of the created extrusion body
    # endFace = ext.endFaces.item(0)

    # sketchInOcc = sketches.add(endFace, occ)
    # curve = sketchInOcc.sketchCurves.item(0)

    # geo0 = adsk.fusion.JointGeometry.createByCurve(curve, adsk.fusion.JointKeyPointTypes.CenterKeyPoint)

    # # Create the second joint geometry with sketch point
    # geo1 = adsk.fusion.JointGeometry.createByPoint(sketchPt)


    # joints = occ.component.joints
    # jointInput = joints.createInput(geo0, geo1)
    # jointInput.setAsPlanarJointMotion(adsk.fusion.JointDirections.YAxisJointDirection)
    # joint = joints.add(jointInput)

    # planarMotion = joint.jointMotion
    # limits = planarMotion.rotationLimits
    # limits.isRestValueEnabled = True
    # limits.restValue = 1.0

    return


def addItemsToDropdown(items, dropdownInput):
  dropdownItems = dropdownInput.listItems
  itemsToDelete = []
  for dropdownItem in dropdownItems:
    itemsToDelete.append(dropdownItem)
  firstNewItem = None
  for item in items:
    newItem = dropdownItems.add(item, False, '')
    if not firstNewItem:
      firstNewItem = newItem
      firstNewItem.isSelected = True
  for dropdownItem in itemsToDelete:
    dropdownItem.deleteMe()
  return firstNewItem


def draw(selectedPlane, selectedFile):
  app = adsk.core.Application.get()
  ui  = app.userInterface
  product = app.activeProduct
  rootComp = product.rootComponent
  extrudes = rootComp.features.extrudeFeatures
  design = adsk.fusion.Design.cast(product)

  rootComp = design.rootComponent
  extrudes = rootComp.features.extrudeFeatures
  sketches = rootComp.sketches

  planes = rootComp.constructionPlanes
  planeInput = planes.createInput()
  offset = adsk.core.ValueInput.createByReal(0)
  planeInput.setByOffset(selectedPlane, offset)
  # planeInput.setByOffset(basePlane, offsetValue)
  planeOne = planes.add(planeInput)

  sketch = sketches.add(planeOne)
  svg = sketch.importSVG(selectedFile, -30, -30, 0.01)

  materialLib = app.materialLibraries.itemByName("Fusion 360 Appearance Library")
  appearance = materialLib.appearances.itemByName("Plastic - Matte (Yellow)") # "Paint - Enamel Glossy (Yellow)"

  toolBodies = adsk.core.ObjectCollection.create()
  for i in range(sketch.profiles.count):
    prof = sketch.profiles.item(i)
    distance = adsk.core.ValueInput.createByReal(0.1)
    extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    extInput.setDistanceExtent(False, distance)
    extrude1 = extrudes.add(extInput)
    for body in extrude1.bodies:
      body.appearance = appearance
      body.name = "sheet"
      toolBodies.add(body)

def componentsFromBodies(items):
  components = []
  for item in items:
    originalBody = item[1]
    copiedBody = originalBody.copyToComponent(originalBody.parentComponent)
    outputBody = originalBody.createComponent()

    component = {
      'output_body': outputBody,
      'copied_body': copiedBody,
      'mid_face': item[0],
      'end_face': item[2]
    }
    components.append(component)
  return components


  # def onInputChanged(self, command, inputs, changedInput):
  #   return
  #   for inputI in inputs:
  #     if inputI.id == command.parentCommandDefinition.id + '_project':
  #       projectInput = inputI
  #       projectName = command.commandInputs.itemById(command.parentCommandDefinition.id + '_project').selectedItem.name
  #       fillFilesDictionary(projectName)
  #       currentProject = projectFiles[projectName]
  #       fileInput = command.commandInputs.itemById(command.parentCommandDefinition.id + '_file')
  #       addItemsToDropdown(currentProject, fileInput)
  #     elif inputI.id == command.parentCommandDefinition.id + 'file':
  #       fileInput = inputI