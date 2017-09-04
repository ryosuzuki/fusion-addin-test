import adsk.core, adsk.fusion, adsk.cam, traceback
from . import Fusion360CommandBase

def getSelectedObjects(selectionInput):
  objects = []
  for i in range(0, selectionInput.selectionCount):
    selection = selectionInput.selection(i)
    selectedObj = selection.entity
    if adsk.fusion.BRepBody.cast(selectedObj) or \
      adsk.fusion.BRepFace.cast(selectedObj) or \
      adsk.fusion.Occurrence.cast(selectedObj):
      objects.append(selectedObj)
  return objects


class ImportCommand(Fusion360CommandBase.Fusion360CommandBase):
  def onPreview(self, command, inputs):
    return
    self.ui.messageBox("preview")
    self.project = self.projects[2]
    self.projectFiles[self.project.name] = None
    dropdownInput = inputs.addDropDownCommandInput(command.parentCommandDefinition.id + '_project', 'Project', adsk.core.DropDownStyles.TextListDropDownStyle)
    addItemsToDropdown(self.projectFiles, dropdownInput)

    self.files = self.projectFiles[self.project.name]
    if not self.files:
      self.dataFiles = self.project.rootFolder.dataFiles
      self.files = {}
      for file in self.dataFiles:
        self.files[file.name] = file

    dropdownInput = inputs.addDropDownCommandInput(command.parentCommandDefinition.id + '_file', 'File', adsk.core.DropDownStyles.TextListDropDownStyle)
    addItemsToDropdown(self.files, dropdownInput)

  def onDestroy(self, command, inputs, reason_):
    pass

  def onInputChanged(self, command, inputs, changedInput):
    targetId = command.parentCommandDefinition.id + '_file'
    if changedInput.id == targetId:
      name = command.commandInputs.itemById(targetId).selectedItem.name
      self.file = self.files[name]

  def onCreate(self, command, inputs):
    self.project = None
    self.projects = []
    self.files = []
    self.projectNames = {}
    self.fileNames = {}

    self.app = adsk.core.Application.get()
    self.ui  = self.app.userInterface
    self.projects = self.app.data.dataProjects
    self.project = self.projects[2]
    self.files = self.project.rootFolder.dataFiles

    self.projectNames[self.project.name] = self.project
    dropdownInput = inputs.addDropDownCommandInput(command.parentCommandDefinition.id + '_project', 'Project', adsk.core.DropDownStyles.TextListDropDownStyle)
    addItemsToDropdown(self.projectNames, dropdownInput)

    self.fileNames = {}
    self.file = self.files[2]
    self.fileNames[self.file.name] = self.file
    # for file in self.files:
      # self.fileNames[file.name] = None

    dropdownInput = inputs.addDropDownCommandInput(command.parentCommandDefinition.id + '_file', 'File', adsk.core.DropDownStyles.TextListDropDownStyle)
    addItemsToDropdown(self.fileNames , dropdownInput)

  def onExecute(self, command, inputs):
    design = self.app.activeProduct
    rootComp = design.rootComponent
    occs = rootComp.occurrences

    matrix = adsk.core.Matrix3D.create()
    occ = occs.addByInsert(self.file, matrix, False)
    materialLib = app.materialLibraries.itemByName("Fusion 360 Appearance Library")
    appearance = materialLib.appearances.itemByName("Plastic - Matte (Yellow)")
    occ.appearance = appearance

    sketches = rootComp.sketches
    sketch = sketches.add(rootComp.xZConstructionPlane)
    sketchPts = sketch.sketchPoints
    point = adsk.core.Point3D.create(1, 0, 1)
    sketchPt = sketchPts.add(point)
    sketchCircles = sketch.sketchCurves.sketchCircles
    centerPoint = adsk.core.Point3D.create(0, 0, 0)
    circle = sketchCircles.addByCenterRadius(centerPoint, 5.0)

    # Get the profile defined by the circle
    prof = sketch.profiles.item(0)

    # Create an extrusion input and make sure it's in a new component
    extrudes = rootComp.features.extrudeFeatures
    extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewComponentFeatureOperation)

    # Set the extrusion input
    distance = adsk.core.ValueInput.createByReal(5)
    extInput.setDistanceExtent(True, distance)
    extInput.isSolid = True

    # Create the extrusion
    ext = extrudes.add(extInput)

    # Get the end face of the created extrusion body
    endFace = ext.endFaces.item(0)

    sketchInOcc = sketches.add(endFace, occ)
    curve = sketchInOcc.sketchCurves.item(0)

    geo0 = adsk.fusion.JointGeometry.createByCurve(curve, adsk.fusion.JointKeyPointTypes.CenterKeyPoint)

    # Create the second joint geometry with sketch point
    geo1 = adsk.fusion.JointGeometry.createByPoint(sketchPt)


    joints = occ.component.joints
    jointInput = joints.createInput(geo0, geo1)
    jointInput.setAsPlanarJointMotion(adsk.fusion.JointDirections.YAxisJointDirection)
    joint = joints.add(jointInput)

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