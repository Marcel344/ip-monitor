from PyQt5.QtCore import QThread
from PyQt5 import uic, Qt, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QWidget
import os
import sys
import json
import time
import platform    
import subprocess  

class Driver (Qt.QWidget):
    def __init__ (self):
        super(Driver, self).__init__()
        uic.loadUi('ui/main.ui', self)
        self.show()
        self.setWindowTitle('IP Monitor')
        self.addBtn.clicked.connect(self.addDevice)
        self.removeBtn.clicked.connect(self.removeDevice)
        self.infoBox.setVisible(False)
        self.connections = []
        self.listWidget.currentRowChanged.connect(self.showDeviceInfo)
        if (not os.path.isdir('devices')):
            os.mkdir('devices')
        else :
            self.populateList()

    def addDevice(self):
        self.addDeviceWindow = AddDeviceWindow()
        self.addDeviceWindow.addNameSignal.connect(self.addName)
        self.addDeviceWindow.showWindow()

    def addName(self, name):
        item = QtWidgets.QListWidgetItem(name)
        self.listWidget.addItem(item)
        jsonFile = open(f'devices/{name}', 'r')
        data = json.load(jsonFile)
        connection = connectionThread(data['Address'], data['Name'])
        connection.connectedSignal.connect(self.updateConnected)
        connection.disconnectedSignal.connect(self.updateDisconnected)
        self.connections.append(connection)

    def showDeviceInfo(self, index):
        device = self.listWidget.currentItem().text()
        jsonFile = open(f'devices/{device}.json', 'r')
        data = json.load(jsonFile)
        self.nameLabel.setText(data['Name'])
        self.ipLabel.setText(data['Address'])
        self.infoBox.setVisible(True)

    def removeDevice(self):
        pass

    def populateList(self):
        self.listWidget.clear()
        devices = os.listdir('devices')
        for device in devices :
            if device != '.DS_Store':
                jsonFile = open(f'devices/{device}', 'r')
                data = json.load(jsonFile)
                item = QtWidgets.QListWidgetItem(data['Name'])
                self.listWidget.addItem(item)
                connection = connectionThread(data['Address'], data['Name'])
                connection.connectedSignal.connect(self.updateConnected)
                connection.disconnectedSignal.connect(self.updateDisconnected)
                connection.start()
                self.connections.append(connection)

    def updateConnected(self, device):
        listElement = self.listWidget.findItems(device, QtCore.Qt.MatchExactly) 
        if len(listElement) > 0: 
            color = Qt.QColor() 
            color.setRgb(195,236,192)
            listElement[0].setBackground(color)

    def updateDisconnected(self, device):
        listElement = self.listWidget.findItems(device, QtCore.Qt.MatchExactly) 
        if len(listElement) > 0: 
            color = Qt.QColor() 
            color.setRgb(236,192,192)
            listElement[0].setBackground(color)

class connectionThread (QThread): # this is a Thread class responsible for checking internet connection

    connectedSignal = QtCore.pyqtSignal(str, name="strSignal") # this is a signal that will trigger the connected function in the main file
    disconnectedSignal = QtCore.pyqtSignal(str, name="strSignal") # this is a signal that will trigger the connected function in the main file

    def __init__(self, address, name):
        super(connectionThread, self).__init__()
        self.address = address
        self.name = name

    def run(self):
        while True : # run forever 
            param = '-n' if platform.system().lower()=='windows' else '-c'
            command = ['ping', param, '1', self.address]
            if (subprocess.call(command) == 0):  
                self.connectedSignal.emit(self.name)
            else :
                self.disconnectedSignal.emit(self.name)
            time.sleep(2) # Check for connection every 2 seconds

class AddDeviceWindow (QThread) :

    addNameSignal = QtCore.pyqtSignal(str, name="strSignal")

    def __init__(self):
        QThread.__init__(self)
        self.Window = Qt.QWidget()
        uic.loadUi('ui/addDevice.ui', self.Window)
        self.Window.addBtn.clicked.connect(self.run)

    def run(self):
        if not (self.Window.name == "" or self.Window.ipAddress.toPlainText() == ""):
            jsonFile = open(f'devices/{self.Window.name.toPlainText()}.json', 'w+')
            jsonData = {
                "Name": self.Window.name.toPlainText(),
                "Address": self.Window.ipAddress.toPlainText(),
            }
            json.dump(jsonData, jsonFile)
            jsonFile.close()
            self.addNameSignal.emit(self.Window.name.toPlainText())
            self.Window.close()

    def showWindow (self):
        self.Window.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Driver()
    app.exec_() # execute application 

