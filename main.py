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
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setStyleSheet('background : #444444;')
        self.listWidget.setStyleSheet('background : #878683')
        self.infoBox.setStyleSheet('background : #bebebe; padding : 10px; border 1px solid black; border-radius : 10px')
        self.removeBtn.setStyleSheet("QPushButton {background-color : #9b9a92; border : 1px solid #8d989f; color white; border-radius : 10px}")
        self.addBtn.setStyleSheet("QPushButton {background-color : #9b9a92; border : 1px solid #8d989f; color white; border-radius : 10px}")
        self.show()
        self.setWindowTitle('IP Monitor')
        self.addBtn.clicked.connect(self.addDevice)
        self.removeBtn.clicked.connect(self.removeDevice)
        self.infoBox.setVisible(False)
        self.connections = []
        self.connectionMap = {}
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
        color = Qt.QColor()
        color.setRgb(236,192,192)
        item.setBackground(color)
        self.listWidget.addItem(item)
        jsonFile = open(f'devices/{name}.json', 'r')
        data = json.load(jsonFile)
        connection = connectionThread(data['Address'], data['Name'])
        connection.connectionSignal.connect(self.updateConnetion)
        self.populateList()

    def showDeviceInfo(self, index):
        if self.listWidget.currentItem():
            device = self.listWidget.currentItem().text()
            jsonFile = open(f'devices/{device}.json', 'r')
            data = json.load(jsonFile)
            self.nameLabel.setText(data['Name'])
            self.ipLabel.setText(data['Address'])
            if self.connectionMap.get(data['Name']):
                self.statusLbl.setText('Connected')
            else :
                self.statusLbl.setText('Disconnected')
            self.infoBox.setVisible(True)

    def removeDevice(self):
        fileName = self.listWidget.currentItem().text()
        os.remove(f'devices/{fileName}.json')
        self.listWidget.currentItem().setHidden(True)
        self.infoBox.setVisible(False)

    def populateList(self):
        self.connections = []
        self.listWidget.clear()
        devices = os.listdir('devices')
        for device in devices :
            if device != '.DS_Store':
                jsonFile = open(f'devices/{device}', 'r')
                data = json.load(jsonFile)
                item = QtWidgets.QListWidgetItem(data['Name'])
                color = Qt.QColor()
                color.setRgb(236,192,192)
                item.setBackground(color)
                self.listWidget.addItem(item)
                connection = connectionThread(data['Address'], data['Name'])
                connection.connectionSignal.connect(self.updateConnetion)
                connection.start()
                self.connections.append(connection)
    
    def updateConnetion(self, params):
        listElement = self.listWidget.findItems(params[0], QtCore.Qt.MatchExactly)
        if len(listElement) > 0 and params[1]:
            color = Qt.QColor()
            color.setRgb(195,236,192)
            listElement[0].setBackground(color)
            self.connectionMap[params[0]] = 1
        
        if len(listElement) > 0 and not params[1]:
            color = Qt.QColor()
            color.setRgb(236,192,192)
            listElement[0].setBackground(color)
            self.connectionMap[params[0]] = 0


class connectionThread (QThread): # this is a Thread class responsible for checking ping connection

    connectionSignal = QtCore.pyqtSignal(list) 
    def __init__(self, address, name):
        super(connectionThread, self).__init__()
        self.address = address
        self.name = name

    def run(self):
        while True : # run forever
            param = '-n' if platform.system().lower()=='windows' else '-c'
            command = ['ping', param, '1', self.address]
            connected = (subprocess.call(command) == 0)
            params = [self.name, connected]
            self.connectionSignal.emit(params)
            time.sleep(2) # Check for connection every 2 seconds

class AddDeviceWindow (QThread) :

    addNameSignal = QtCore.pyqtSignal(str, name="strSignal")

    def __init__(self):
        QThread.__init__(self)
        self.Window = Qt.QWidget()
        uic.loadUi('ui/addDevice.ui', self.Window)
        self.Window.setStyleSheet('background : #444444;')
        self.Window.addBtn.setStyleSheet("QPushButton {background-color : #9b9a92; border : 1px solid #8d989f; color white; border-radius : 10px}")
        self.Window.name.setStyleSheet('background-color: #bfbfba')
        self.Window.ipAddress.setStyleSheet('background-color: #bfbfba')
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

