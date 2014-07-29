import os
import unittest
from __main__ import vtk, qt, ctk, slicer

#
# tipiXExporter
#

class tipiXExporter:
  def __init__(self, parent):
    parent.title = "tipiXExporter" # TODO make this more human readable by adding spaces
    parent.categories = ["Converters"]
    parent.dependencies = []
    parent.contributors = ["Steve Pieper, (Isomics, Inc.)"] # replace with "Firstname Lastname (Organization)"
    parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    """
    parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.
    self.parent = parent

    # Add this test to the SelfTest module's list for discovery when the module
    # is created.  Since this module may be discovered before SelfTests itself,
    # create the list if it doesn't already exist.
    try:
      slicer.selfTests
    except AttributeError:
      slicer.selfTests = {}
    slicer.selfTests['tipiXExporter'] = self.runTest

  def runTest(self):
    tester = tipiXExporterTest()
    tester.runTest()

#
# tipiXExporterWidget
#

class tipiXExporterWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    # Instantiate and connect widgets ...

    #
    # Reload and Test area
    #
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.text = "Reload && Test"
    self.layout.addWidget(reloadCollapsibleButton)
    reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "tipiXExporter Reload"
    reloadFormLayout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)

    # reload and test button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadAndTestButton = qt.QPushButton("Reload and Test")
    self.reloadAndTestButton.toolTip = "Reload this module and then run the self tests."
    reloadFormLayout.addWidget(self.reloadAndTestButton)
    self.reloadAndTestButton.connect('clicked()', self.onReloadAndTest)

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # source directory button
    #
    self.sourceButton = ctk.ctkDirectoryButton()
    self.sourceButton.setToolTip( "Select the directory containing the source image volumes to load." )
    parametersFormLayout.addRow("Source Image Files: ", self.sourceButton)

    #
    # destination directory button
    #
    self.destinationButton = ctk.ctkDirectoryButton()
    self.destinationButton.setToolTip( "Select the destination for rendered images." )
    parametersFormLayout.addRow("Destination Files: ", self.destinationButton)

    if False:
        #
        # check box to trigger taking screen shots for later use in tutorials
        #
        self.enableScreenshotsFlagCheckBox = qt.QCheckBox()
        self.enableScreenshotsFlagCheckBox.checked = 0
        self.enableScreenshotsFlagCheckBox.setToolTip("If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
        parametersFormLayout.addRow("Enable Screenshots", self.enableScreenshotsFlagCheckBox)

        #
        # scale factor for screen shots
        #
        self.screenshotScaleFactorSliderWidget = ctk.ctkSliderWidget()
        self.screenshotScaleFactorSliderWidget.singleStep = 1.0
        self.screenshotScaleFactorSliderWidget.minimum = 1.0
        self.screenshotScaleFactorSliderWidget.maximum = 50.0
        self.screenshotScaleFactorSliderWidget.value = 1.0
        self.screenshotScaleFactorSliderWidget.setToolTip("Set scale factor for the screen shots.")
        parametersFormLayout.addRow("Screenshot scale factor", self.screenshotScaleFactorSliderWidget)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Render the images."
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

  def onApplyButton(self):
    logic = tipiXExporterLogic()
    sourceDirectory = self.sourceButton.directory
    destinationDirectory = self.destinationButton.directory
    logic.run(sourceDirectory, destinationDirectory)

  def onReload(self,moduleName="tipiXExporter"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    globals()[moduleName] = slicer.util.reloadScriptedModule(moduleName)

  def onReloadAndTest(self,moduleName="tipiXExporter"):
    try:
      self.onReload()
      evalString = 'globals()["%s"].%sTest()' % (moduleName, moduleName)
      tester = eval(evalString)
      tester.runTest()
    except Exception, e:
      import traceback
      traceback.print_exc()
      qt.QMessageBox.warning(slicer.util.mainWindow(),
          "Reload and Test", 'Exception!\n\n' + str(e) + "\n\nSee Python Console for Stack Trace")


#
# tipiXExporterLogic
#

class tipiXExporterLogic:
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    pass

  def delayDisplay(self,message,msec=1000):
    #
    # logic version of delay display
    #
    print(message)
    self.info = qt.QDialog()
    self.infoLayout = qt.QVBoxLayout()
    self.info.setLayout(self.infoLayout)
    self.label = qt.QLabel(message,self.info)
    self.infoLayout.addWidget(self.label)
    qt.QTimer.singleShot(msec, self.info.close)
    self.info.exec_()

  def loadFileList(self,fileList):
    for filePath in fileList:
      slicer.util.loadVolume(filePath)

  def directoryFileList(self,directory):
    """Return full path to each file in directory
    """
    import os
    fileList = []
    for fileName in os.listdir(directory):
      filePath = os.path.join(directory, fileName)
      fileList.append(filePath)
    return fileList

  def renderToDirectory(self,volume,windowLevel,offsets,pathPattern):
    """For each specified offset, render the volume
    into a file determined by the pathPattern and index
    into the offset list"""
    lm = slicer.app.layoutManager()
    redLogic = lm.sliceWidget('Red').sliceLogic()
    redView = lm.sliceWidget('Red').sliceView()
    compositeNode = redLogic.GetSliceCompositeNode()
    compositeNode.SetBackgroundVolumeID(volume.GetID())
    redLogic.SetBackgroundWindowLevel(*windowLevel)
    offsetIndex = 0
    for offset in offsets:
      redLogic.SetSliceOffset(offset)
      redView.forceRender()
      pixmap = qt.QPixmap().grabWidget(redView)
      pixmap.save(pathPattern % offsetIndex)
      offsetIndex += 1
    

  def run(self,sourceDirectory, destinationDirectory):
    """
    Load all image volumes in sourceDirectory and render images
    into destination Directory
    """
    fileList = self.directoryFileList(sourceDirectory)
    self.loadFileList(fileList)

class tipiXExporterTest(unittest.TestCase):
  """
  This is the test case for your scripted module.
  """

  def delayDisplay(self,message,msec=1000):
    """This utility method displays a small dialog and waits.
    This does two things: 1) it lets the event loop catch up
    to the state of the test so that rendering and widget updates
    have all taken place before the test continues and 2) it
    shows the user/developer/tester the state of the test
    so that we'll know when it breaks.
    """
    print(message)
    self.info = qt.QDialog()
    self.infoLayout = qt.QVBoxLayout()
    self.info.setLayout(self.infoLayout)
    self.label = qt.QLabel(message,self.info)
    self.infoLayout.addWidget(self.label)
    qt.QTimer.singleShot(msec, self.info.close)
    self.info.exec_()

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_tipiXExporter1()

  def test_tipiXExporter1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests sould exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")

    sourceDirectory = "/Users/pieper/data/babybrain/atlas/ADC/timeseries"
    destinationDirectory = "/tmp/tipiX"

    """ Yangming's list of time ranges

        neonate (week 0, 1)
        quarter 0 excluding week 0, 1
        quarter 1
        quarter 2
        quarter 3
        year 1-2
        year 2-3
        year 3-4 
        year 4-5
        year 5-6
    """

    logic = tipiXExporterLogic()

    fileList = [logic.directoryFileList(sourceDirectory)[0],]
    fileList = logic.directoryFileList(sourceDirectory)

    names = [
      "atlas_week0-1_rigidtoyear1-2",
      "atlas_quarter0_excludingweek0-1_rigidtoyear1-2",
      "atlas_quarter1_rigidtoyear1-2",
      "atlas_quarter2_rigidtoyear1-2",
      "atlas_quarter3_rigidtoyear1-2",
      "atlas_year1-2_rigidtoyear1-2",
      "atlas_year2-3_rigidtoyear1-2",
      "atlas_year3-4_rigidtoyear1-2",
      "atlas_year4-5_rigidtoyear1-2",
      "atlas_year5-6_rigidtoyear1-2",
    ]
    fileList = []
    for name in names:
      fileName = name + ".nii.gz"
      fileList.append(os.path.join(sourceDirectory, fileName))

    self.delayDisplay("Loading: %s" % fileList)

    logic.loadFileList(fileList)

    offsets = range(75,-50,-1)
    windowLevel = (1000,1200)

    volumes = slicer.util.getNodes('*VolumeNode*')
    row = 0
    targetDirectory = '/tmp/tipiX'
    for name in names:
      volumeNode = volumes[name]
      pattern = targetDirectory + "/baby_%d" + "_%d.jpg" % row 
      logic.renderToDirectory(volumeNode, windowLevel, offsets, pattern)
      row += 1

    self.delayDisplay('Test passed!')
