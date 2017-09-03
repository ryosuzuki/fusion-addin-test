import adsk.core, adsk.fusion, adsk.cam, traceback
from . import Fusion360CommandBase

projectFiles = {}
projects = None

def getFile(projectName, fileName):
  project = getProject(projectName)
  if project:
    dataFiles = project.rootFolder.dataFiles
    for file in dataFiles:
      if file.name == fileName:
        return file
  return None

def getProject(projectName):
  for project in projects:
    if project.name == projectName:
      return project
  return None

# returns first project's name
def fillProjectsDictionary():
  firstProject = None
  for project in projects:
    if not firstProject:
      firstProject = project

    global projectFiles
    projectFiles[project.name] = None

  return firstProject.name

def fillFilesDictionary(projectName):
  files = projectFiles[projectName]
  if not files:
    project = getProject(projectName)
    dataFiles = project.rootFolder.dataFiles
    files = {}
    for file in dataFiles:
      files[file.name] = file

    projectFiles[projectName] = files

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


def getInputs(command, inputs):
  selectionInput = None
  for inputI in inputs:
    global commandId
    if inputI.id == command.parentCommandDefinition.id + '_project':
      projectInput = inputI
    elif inputI.id == command.parentCommandDefinition.id + 'file':
      fileInput = inputI

  projectName = command.commandInputs.itemById(command.parentCommandDefinition.id + '_project').selectedItem.name
  fileName = command.commandInputs.itemById(command.parentCommandDefinition.id + '_file').selectedItem.name
  file = getFile(projectName, fileName)



  app = adsk.core.Application.get()
  ui  = app.userInterface
  ui.messageBox(projectInput)

  projectName = projectInput
  fileName = fileInput
  file = getFile(projectName, fileName)
  return file


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


class ImportCommand(Fusion360CommandBase.Fusion360CommandBase):
  def onPreview(self, command, inputs):
    pass

  def onDestroy(self, command, inputs, reason_):
    pass

  def onInputChanged(self, command, inputs, changedInput):
    if command.commandInput.id == command.parentCommandDefinition.id + '_project':

      projectName = command.commandInputs.itemById(command.parentCommandDefinition.id + '_project').selectedItem.name
      fillFilesDictionary(projectName)
      currentProject = projectFiles[projectName]
      fileInput = command.commandInputs.itemById(command.parentCommandDefinition.id + '_file')
      addItemsToDropdown(currentProject, fileInput)

  def onCreate(self, command, inputs):
    app = adsk.core.Application.get()
    ui  = app.userInterface
    global projects
    projects = app.data.dataProjects

    fillProjectsDictionary()
    dropdownInput = inputs.addDropDownCommandInput(command.parentCommandDefinition.id + '_project', 'Project', adsk.core.DropDownStyles.TextListDropDownStyle)
    projectItem = addItemsToDropdown(projectFiles, dropdownInput)

    fillFilesDictionary(projectItem.name)
    dropdownInput = inputs.addDropDownCommandInput(command.parentCommandDefinition.id + '_file', 'File', adsk.core.DropDownStyles.TextListDropDownStyle)
    project = projectFiles[projectItem.name]
    addItemsToDropdown(project, dropdownInput)


  def onExecute(self, command, inputs):
    projectName = command.commandInputs.itemById(command.parentCommandDefinition.id + '_project').selectedItem.name
    fileName = command.commandInputs.itemById(command.parentCommandDefinition.id + '_file').selectedItem.name
    file = getFile(projectName, fileName)

    app = adsk.core.Application.get()
    design = app.activeProduct
    rootComp = design.rootComponent
    occs = rootComp.occurrences
    component = occs.addByInsert(file, adsk.core.Matrix3D.create(), True)

    materialLib = app.materialLibraries.itemByName("Fusion 360 Appearance Library")
    appearance = materialLib.appearances.itemByName("Plastic - Matte (Yellow)") # "Paint - Enamel Glossy (Yellow)"


    component.appearance = appearance

    return


    # plane = getInputs(command, inputs)
    # filepath = selectFile()
    # if (plane):
    #   draw(plane, filepath)

    # # return


    # app = adsk.core.Application.get()
    # ui  = app.userInterface
    # product = app.activeProduct
    # design = adsk.fusion.Design.cast(product)
    # rootComp = design.rootComponent

    # targetBody = rootComp.bRepBodies.item(0)
    # spacing = 10
    # quantity = 10
    # plane = targetBody.parentComponent.xZConstructionPlane
    # thickness = 1

    # results = slice(targetBody, spacing, quantity, plane, thickness)

    # components = componentsFromBodies(results)

    # # futil.combine_feature(point[1], tool_bodies, adsk.fusion.FeatureOperations.CutFeatureOperation)

    # combineFeatures = targetBody.parentComponent.features.combineFeatures

    # combineTools = adsk.core.ObjectCollection.create()
    # for tool in tool_bodies:
    #   combineTools.add(tool)

    # # Create Combine Feature
    # combine_input = combine_features.createInput(target_body, combine_tools)
    # combine_input.operation = operation
    # combine_features.add(combine_input)

