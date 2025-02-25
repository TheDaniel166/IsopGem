"""
Complete test of PyQt6-3D with a rotating cube
"""
from PyQt6 import QtCore, QtGui, QtWidgets, Qt3DCore, Qt3DExtras
import sys

app = QtWidgets.QApplication(sys.argv)

# Create a basic Qt 3D window
view = Qt3DExtras.Qt3DWindow()
view.defaultFrameGraph().setClearColor(QtGui.QColor(255, 255, 255))

# Create the root entity
rootEntity = Qt3DCore.QEntity()

# Camera
camera = view.camera()
camera.lens().setPerspectiveProjection(45.0, 16/9, 0.1, 1000)
camera.setPosition(QtGui.QVector3D(0, 0, 20))
camera.setViewCenter(QtGui.QVector3D(0, 0, 0))

# For camera controls
camController = Qt3DExtras.QOrbitCameraController(rootEntity)
camController.setLinearSpeed(50.0)
camController.setLookSpeed(180.0)
camController.setCamera(camera)

# Create a simple 3D cube object
cube = Qt3DExtras.QCuboidMesh()

# Cube mesh transform
cubeTransform = Qt3DCore.QTransform()
cubeTransform.setScale(1)
cubeTransform.setRotation(QtGui.QQuaternion.fromEulerAngles(45, 45, 0))

# Cube entity
cubeEntity = Qt3DCore.QEntity(rootEntity)
cubeEntity.addComponent(cube)
cubeEntity.addComponent(Qt3DExtras.QPhongMaterial())
cubeEntity.addComponent(cubeTransform)

# Set the scene root
view.setRootEntity(rootEntity)
view.show()

app.exec()
