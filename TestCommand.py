import adsk.core, adsk.fusion, adsk.cam, traceback

from . import Fusion360CommandBase

def getInputs(command, inputs):
  selectionInput = None
  for inputI in inputs:
    global commandId
    if inputI.id == command.parentCommandDefinition.id + '_selection':
      selectionInput = inputI
    elif inputI.id == command.parentCommandDefinition.id + '_plane':
      planeInput = inputI
    elif inputI.id == command.parentCommandDefinition.id + '_spacing':
      spacingInput = inputI
      spacing = spacingInput.value
    elif inputI.id == command.parentCommandDefinition.id + '_edge':
      edgeInput = inputI

  objects = getSelectedObjects(selectionInput)
  plane = getSelectedObjects(planeInput)[0]

  edge = False
  # edge = adsk.fusion.BRepEdge.cast(edgeInput.selection(0).entity)

  # if not objects or len(objects) == 0:
    # TODO this probably requires much better error handling
    # return
  # return(objects, plane, edge, spacing, subAssy)
  return plane # (objects, plane, edge, spacing)

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

def selectFile():
  return "/Users/ryosuzuki/Desktop/test.svg"

  app = adsk.core.Application.get()
  ui  = app.userInterface

  fileDialog = ui.createFileDialog()
  fileDialog.isMultiSelectEnabled = False
  fileDialog.title = "Select SVG file"
  fileDialog.filter = "*.svg"
  # fileDialog.initialDirectory = ""
  dialogResult = fileDialog.showOpen()

  if (dialogResult == adsk.core.DialogResults.DialogOK):
    filepath = fileDialog.filename
    ui.messageBox(filepath)
    return filepath


def draw(selectedPlane, selectedFile):
  try:
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
    offsetValue = adsk.core.ValueInput.createByReal(0)
    planeInput.setByOffset(selectedPlane, offsetValue)
    planeOne = planes.add(planeInput)

    sketch = sketches.add(planeOne)
    svg = sketch.importSVG(selectedFile, -30, -30, 0.01)

    materialLib = app.materialLibraries.itemByName("Fusion 360 Appearance Library")
    appearance = materialLib.appearances.itemByName("Plastic - Matte (Yellow)")
    # appearance = materialLib.itemByName("Paint - Enamel Glossy (Yellow)")

    for i in range(sketch.profiles.count):
      prof = sketch.profiles.item(i)
      distance = adsk.core.ValueInput.createByReal(0.1)
      extrude1 = extrudes.addSimple(prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
      body1 = extrude1.bodies.item(0)
      body1.name = "simple"
      body1.appearance = appearance

    # # Add construction plane by angle
    # angle = adsk.core.ValueInput.createByString('30.0 deg')
    # planeInput.setByAngle(sketchLineOne, angle, prof)
    # planes.add(planeInput)

    # # Add construction plane by two planes
    # planeInput.setByTwoPlanes(prof, planeOne)
    # planes.add(planeInput)

    # # Add construction plane by tangent
    # cylinderFace = extrude.sideFaces.item(0)
    # planeInput.setByTangent(cylinderFace, angle, rootComp.xYConstructionPlane)
    # planes.add(planeInput)

    # # Add construction plane by two edges
    # planeInput.setByTwoEdges(sketchLineOne, sketchLineTwo)
    # planes.add(planeInput)

    # # Add construction plane by three points
    # planeInput.setByThreePoints(sketchPointOne, sketchPointTwo, sketchPointThree)
    # planes.add(planeInput)

    # # Add construction plane by tangent at point
    # planeInput.setByTangentAtPoint(cylinderFace, sketchPointOne)
    # planes.add(planeInput)

    # # Add construction plane by distance on path
    # distance = adsk.core.ValueInput.createByReal(1.0)
    # planeInput.setByDistanceOnPath(sketchLineOne, distance)
    # planes.add(planeInput)

  except:
    if ui:
      ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def healthState(object):
  health = object.healthState
  if health == adsk.fusion.FeatureHealthStates.ErrorFeatureHealthState or health == adsk.fusion.FeatureHealthStates.WarningFeatureHealthState:
      message = planeOne.errorOrWarningMessage




class TestCommand(Fusion360CommandBase.Fusion360CommandBase):
  def onPreview(self, command, inputs):
    pass

  def onDestroy(self, command, inputs, reason_):
    pass

  def onInputChanged(self, command, inputs, changedInput):
    pass

  def onExecute(self, command, inputs):
    # Get Input values
    # (objects, plane, edge, spacing) = getInputs(command, inputs)
    plane = getInputs(command, inputs)
    filepath = selectFile()
    if (plane):
      draw(plane, filepath)

  def onCreate(self, command, inputs):
    selectionPlaneInput = inputs.addSelectionInput(command.parentCommandDefinition.id + '_plane', 'Select Base Face', 'Select Face to mate to')
    selectionPlaneInput.setSelectionLimits(1,1)
    selectionPlaneInput.addSelectionFilter('PlanarFaces')

    selectionInput = inputs.addSelectionInput(command.parentCommandDefinition.id + '_selection', 'Select other faces', 'Select bodies or occurrences')
    selectionInput.setSelectionLimits(1,0)
    selectionInput.addSelectionFilter('PlanarFaces')

    selectionEdgeInput = inputs.addSelectionInput(command.parentCommandDefinition.id + '_edge', 'Select Direction (edge)', 'Select an edge to define spacing direction')
    selectionEdgeInput.setSelectionLimits(1,1)
    selectionEdgeInput.addSelectionFilter('LinearEdges')

    app = adsk.core.Application.get()
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    unitsMgr = design.unitsManager
    spacingInput = inputs.addValueInput(command.parentCommandDefinition.id + '_spacing', 'Component Spacing', unitsMgr.defaultLengthUnits, adsk.core.ValueInput.createByReal(2.54))
