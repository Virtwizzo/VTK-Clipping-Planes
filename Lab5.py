import vtk
useDataRoot = False

from vtk.util.misc import vtkGetDataRoot
VTK_DATA_ROOT = vtkGetDataRoot() + "/"

if useDataRoot==False:
	VTK_DATA_ROOT = ""

#SLIDER CALLBACK
class sliderCallback(object):
	def __init__(self, contour):
		self.c = contour
		
		
	def slide(self, obj, event):
		sliderRep = obj.GetRepresentation()
		count = sliderRep.GetValue()
		self.c.SetValue(0, count)
		
# Start by loading some data.
v16 = vtk.vtkVolume16Reader()

#Image parameters (size and spacing) are being hardcoded, 
# but they could have been read from the header file.

# Set the size of each slice.
v16.SetDataDimensions(64, 64)
v16.SetDataByteOrderToLittleEndian()
v16.SetFilePrefix(VTK_DATA_ROOT + "headsq/quarter")

# the files are quarter.1 through quarter.93
v16.SetImageRange(1, 93)

# this is the spacing specified in the header (anisotropic voxels)
v16.SetDataSpacing(3.2, 3.2, 1.5)
v16.Update()

vtkSDDP = vtk.vtkStreamingDemandDrivenPipeline
xMin, xMax, yMin, yMax, zMin, zMax = v16.GetOutputInformation(0).Get(vtkSDDP.WHOLE_EXTENT())

spacing = v16.GetOutput().GetSpacing()
sx, sy, sz = spacing

origin = v16.GetOutput().GetOrigin()
ox, oy, oz = origin

# An outline box is shown for visual context.
outline = vtk.vtkOutlineFilter()
outline.SetInputConnection(v16.GetOutputPort())

outlineMapper = vtk.vtkPolyDataMapper()
outlineMapper.SetInputConnection(outline.GetOutputPort())

outlineActor = vtk.vtkActor()
outlineActor.SetMapper(outlineMapper)

#LAB5 additions HERE!!!!!!!!!!!!!!!!!!!!!!!
isovalues = [500, 1500]

mc_contour = [vtk.vtkMarchingCubes(), vtk.vtkMarchingCubes()]
for i in range(2):
	mc_contour[i].SetInputConnection(v16.GetOutputPort())
	mc_contour[i].SetValue(0, isovalues[i])
	mc_contour[i].Update()

planes = vtk.vtkPlanes()
clipper = [vtk.vtkClipPolyData(), vtk.vtkClipPolyData()]
for i in range(2):
	clipper[i].SetInputConnection(mc_contour[i].GetOutputPort())
	clipper[i].SetClipFunction(planes)

clipper[0].InsideOutOn()
clipper[1].InsideOutOff()
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Create the RenderWindow and Renderer
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)

# Add the outline actor to the renderer, set the background color and size
ren.AddActor(outlineActor)
renWin.SetSize(600, 600)
ren.SetBackground(0.3, 0.3, 0.4)

iact = vtk.vtkRenderWindowInteractor()
iact.SetRenderWindow(renWin)
iact.Initialize()
# mapper 
mapper = [vtk.vtkPolyDataMapper(), vtk.vtkPolyDataMapper()] 
for i in range(2):
	mapper[i].SetInputConnection(mc_contour[i].GetOutputPort())
	mapper[i].ScalarVisibilityOff()

# actor 
contourActor = [vtk.vtkActor(), vtk.vtkActor()]
for i in range(2):
	contourActor[i].SetMapper(mapper[i]) 
	contourActor[0].GetProperty().SetColor( 0.9, 0.8, 0.8)
	contourActor[1].GetProperty().SetColor( 0, 0.5, 1)
	ren.AddActor(contourActor[i])

#SLIDER ARRAY
sliderRep = [vtk.vtkSliderRepresentation2D(), vtk.vtkSliderRepresentation2D()]
for i in range(2):
	sliderRep[i].SetValue(0.0);
	sliderRep[i].SetMinimumValue(0);
	sliderRep[i].SetMaximumValue(2000);
	sliderRep[0].SetTitleText("White Head");
	sliderRep[1].SetTitleText("Blue Head");
	sliderRep[0].GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay();
	sliderRep[0].GetPoint1Coordinate().SetValue(0.2, 0.95);
	sliderRep[0].GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay();
	sliderRep[0].GetPoint2Coordinate().SetValue(0.8, 0.95);
	sliderRep[1].GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay();
	sliderRep[1].GetPoint1Coordinate().SetValue(0.2, 0.85);
	sliderRep[1].GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay();
	sliderRep[1].GetPoint2Coordinate().SetValue(0.8, 0.85);
	sliderRep[i].SetSliderLength(0.02);
	sliderRep[i].SetSliderWidth(0.03);
	sliderRep[i].SetEndCapLength(0.01);
	sliderRep[i].SetEndCapWidth(0.03);
	sliderRep[i].SetTubeWidth(0.005);
	

sliderWidget = [vtk.vtkSliderWidget(), vtk.vtkSliderWidget()]
for i in range(2):
	sliderWidget[i].SetInteractor(iact)
	sliderWidget[i].SetRepresentation(sliderRep[i])
	sliderWidget[i].SetAnimationModeToAnimate();
	sliderWidget[i].SetEnabled(True)

sc1 = sliderCallback(mc_contour[0])
sliderWidget[0].AddObserver("InteractionEvent", sc1.slide)
sc2 = sliderCallback(mc_contour[1])
sliderWidget[1].AddObserver("InteractionEvent", sc2.slide)

def textImage(text):
	buttonImage = vtk.vtkImageData()
	freeType = vtk.vtkFreeTypeStringToImage()
	textProperty = vtk.vtkTextProperty()
	textProperty.SetColor(1.0, 1.0, 1.0)
	textProperty.SetFontSize(64);
	textProperty.SetFontFamilyToTimes()
	freeType.RenderString(textProperty, text, 120, buttonImage);
	return buttonImage
#ComputeNormalsButton
#The naming is a bit counterintuitive for these text images
NormalsOn_image = textImage("Normals Off")
NormalsOff_image = textImage("Normals On")
NormalsButton = vtk.vtkTexturedButtonRepresentation2D()
NormalsButton.SetNumberOfStates(2);
NormalsButton.SetButtonTexture(0, NormalsOff_image);
NormalsButton.SetButtonTexture(1, NormalsOn_image);
NormalsButton.PlaceWidget([0, 400, 0, 50, 0, 0]);

def normals_change(obj, event):
	state = obj.GetSliderRepresentation().GetState()
	if state == 1:
		mc_contour[0].ComputeNormalsOff()
		mc_contour[1].ComputeNormalsOff()
	if state == 0:
		mc_contour[0].ComputeNormalsOn()
		mc_contour[1].ComputeNormalsOn()
		
	print state
#NormalsButtonWidgets
normalsWidget = vtk.vtkButtonWidget()
normalsWidget.SetInteractor(iact)
normalsWidget.SetRepresentation(NormalsButton)
normalsWidget.SetEnabled(True)
normalsWidget.On()
normalsWidget.AddObserver("StateChangedEvent", normals_change)

#ChangeSurfaceTypeButton
Wireframe_image = textImage("Wireframe On")
Surface_image = textImage("Surface On")
SurfaceButton = vtk.vtkTexturedButtonRepresentation2D()
SurfaceButton.SetNumberOfStates(2);
SurfaceButton.SetButtonTexture(0, Surface_image);
SurfaceButton.SetButtonTexture(1, Wireframe_image);
SurfaceButton.PlaceWidget([0, 2000, 0, 50, 0, 0]);

def surface_change(obj, event):
	state = obj.GetSliderRepresentation().GetState()
	if state == 1:
		contourActor[0].GetProperty().SetRepresentationToWireframe()
		contourActor[1].GetProperty().SetRepresentationToWireframe()
	if state == 0:
		contourActor[0].GetProperty().SetRepresentationToSurface()
		contourActor[1].GetProperty().SetRepresentationToSurface()	
	print state
#NormalsButtonWidgets
surfaceWidget = vtk.vtkButtonWidget()
surfaceWidget.SetInteractor(iact)
surfaceWidget.SetRepresentation(SurfaceButton)
surfaceWidget.SetEnabled(True)
surfaceWidget.On()
surfaceWidget.AddObserver("StateChangedEvent", surface_change)



#Box Widget for adding clipping planes!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

selectMapper = vtk.vtkPolyDataMapper()
selectMapper.SetInputConnection(clipper[0].GetOutputPort())
selectMapper.ScalarVisibilityOff()
#maceActor = vtk.vtkActor()
#maceActor.SetMapper(selectMapper)

#mapper[0].vtkPolyDataMapper()
#mapper[0].SetInputConnection(clipper.GetOutputPort())
#mapper[0].ScalarVisibilityOff()

# The SetInteractor method is how 3D widgets are associated with the
# render window interactor.  Internally, SetInteractor sets up a bunch
# of callbacks using the Command/Observer mechanism.
boxWidget = vtk.vtkBoxWidget()
boxWidget.SetInteractor(iact)
boxWidget.SetPlaceFactor(1.0)

#ren.AddActor(maceActor)

# This callback function does the actual work: updates the vtkPlanes
# implicit function.  This in turn causes the pipeline to update.
def ClipPolygons(object, event):
    # object will be the boxWidget
    object.GetPlanes(planes) #This function is called by reference, and modifies the vtkPlanes object

	

# Place the interactor initially. The input to a 3D widget is used to
# initially position and scale the widget. The "InteractionEvent" is
# observed which invokes the ClipPolygons callback.
boxWidget.SetInputConnection(mc_contour[0].GetOutputPort())
boxWidget.PlaceWidget()
boxWidget.AddObserver("InteractionEvent", ClipPolygons)
boxWidget.On()
boxWidget.GetPlanes(planes)


iact.Initialize()
renWin.Render()
iact.Start()
