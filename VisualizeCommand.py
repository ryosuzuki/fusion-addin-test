import adsk.core, adsk.fusion, adsk.cam, traceback

from . import Fusion360CommandBase

def visualize():
  app = adsk.core.Application.get()
  ui  = app.userInterface
  product = app.activeProduct
  rootComp = product.rootComponent
  extrudes = rootComp.features.extrudeFeatures
  design = adsk.fusion.Design.cast(product)
  rootComp = design.rootComponent

  materialLib = app.materialLibraries.itemByName("Fusion 360 Appearance Library")
  appearance = materialLib.appearances.itemByName("Plastic - Matte (Yellow)") # "Paint - Enamel Glossy (Yellow)"

  targetBody = rootComp.bRepBodies.item(0)
  toolBodies = adsk.core.ObjectCollection.create()
  for i in range(rootComp.bRepBodies.count):
    body = rootComp.bRepBodies.item(i)
    if body.name.find("sheet") == 0:
      body.appearance = appearance
      toolBodies.add(body)

  combineCutInput = rootComp.features.combineFeatures.createInput(targetBody, toolBodies)
  combineCutInput.operation = adsk.fusion.FeatureOperations.IntersectFeatureOperation
  result = rootComp.features.combineFeatures.add(combineCutInput)

  resultBodies = adsk.core.ObjectCollection.create()
  for body in result.bodies:
    body.name = "result"
    body.appearance = appearance
    resultBodies.add(body)


class VisualizeCommand(Fusion360CommandBase.Fusion360CommandBase):
  def onPreview(self, command, inputs):
    pass

  def onDestroy(self, command, inputs, reason_):
    pass

  def onInputChanged(self, command, inputs, changedInput):
    pass

  def onExecute(self, command, inputs):
    # (objects, plane, edge, spacing) = getInputs(command, inputs)
    visualize()

  def onCreate(self, command, inputs):
    pass


def slice(targetBody, spacing, qty, basePlane, thickness):
  targetComp = targetBody.parentComponent
  # Feature Collections
  planes = targetComp.constructionPlanes
  sketches = targetComp.sketches
  thickenFeatures = targetComp.features.thickenFeatures
  slices = []
  thickness /= 2

  for i in range(qty):
    planeInput = planes.createInput()
    offset = adsk.core.ValueInput.createByReal(i * spacing)
    planeInput.setByOffset(basePlane, offset)
    plane = planes.add(planeInput)

    sketch = sketches.add(plane)
    for curve in sketch.sketchCurves:
      curve.isConstruction = True
    sketch.projectCutEdges(targetBody)

    for profile in sketch.profiles:
      surfaces = adsk.core.ObjectCollection.create()
      patches = targetComp.features.patchFeatures
      patchInput = patches.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
      patchFeature = patches.add(patchInput)

      for face in patchFeature.faces:
        point = face.pointOnFace
        containment = targetBody.pointContainment(point)
        if containment == adsk.fusion.PointContainment.PointInsidePointContainment:
          surfaces.add(face)
          thickness = adsk.core.ValueInput.createByReal((thickness/2))
          thickenInput = thickenFeatures.createInput(surfaces, thickness, True,adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
          thickenFeatures = thickenFeatures.add(thickenInput)
          newBody = thickenFeatures.bodies[0]
          ret = face.evaluator.getNormalAtPoint(face.pointOnFace)
          direction = ret[1]
          # Not currently working or used
          # end_face = find_end_face(thickenFeatures, direction)

          # slices.append((face, newBody, end_face))
          slices.append((face, newBody))

        else:
          patchFeature.deleteMe()

  return slices
