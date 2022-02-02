from typing_extensions import Self
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtGui import *

from PyQt5 import QtCore
import os
import sys
import time

import time
import paho.mqtt.client as paho
from paho import mqtt
  
# Main window class

class MqttClient(QtCore.QObject):
    Disconnected = 0
    Connecting = 1
    Connected = 2

    MQTT_3_1 = paho.MQTTv5
    MQTT_3_1_1 = paho.MQTTv311

    connected = QtCore.pyqtSignal()
    disconnected = QtCore.pyqtSignal()

    stateChanged = QtCore.pyqtSignal(int)
    hostnameChanged = QtCore.pyqtSignal(str)
    portChanged = QtCore.pyqtSignal(int)
    keepAliveChanged = QtCore.pyqtSignal(int)
    cleanSessionChanged = QtCore.pyqtSignal(bool)
    protocolVersionChanged = QtCore.pyqtSignal(int)

    messageSignal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(MqttClient, self).__init__(parent)

        self.m_hostname = ""
        self.m_port = 8883
        self.m_keepAlive = 60
        self.m_cleanSession = True
        self.m_protocolVersion = paho.MQTTv5

        self.m_state = MqttClient.Disconnected

        #self.m_client =  mqtt.client(clean_session=self.m_cleanSession,
        #   protocol=self.protocolVersion)
        self.m_client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        self.m_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        

        self.m_client.username_pw_set("testing", "Testing1234")
        # connect to HiveMQ Cloud on port 8883 (default for MQTT)
        
        self.m_client.on_connect = self.on_connect
        self.m_client.on_message = self.on_message
        self.m_client.on_disconnect = self.on_disconnect


    @QtCore.pyqtProperty(int, notify=stateChanged)
    def state(self):
        return self.m_state

    @state.setter
    def state(self, state):
        if self.m_state == state: return
        self.m_state = state
        self.stateChanged.emit(state) 

    @QtCore.pyqtProperty(str, notify=hostnameChanged)
    def hostname(self):
        return self.m_hostname

    @hostname.setter
    def hostname(self, hostname):
        if self.m_hostname == hostname: return
        self.m_hostname = hostname
        self.hostnameChanged.emit(hostname)

    @QtCore.pyqtProperty(int, notify=portChanged)
    def port(self):
        return self.m_port

    @port.setter
    def port(self, port):
        if self.m_port == port: return
        self.m_port = port
        self.portChanged.emit(port)

    @QtCore.pyqtProperty(int, notify=keepAliveChanged)
    def keepAlive(self):
        return self.m_keepAlive

    @keepAlive.setter
    def keepAlive(self, keepAlive):
        if self.m_keepAlive == keepAlive: return
        self.m_keepAlive = keepAlive
        self.keepAliveChanged.emit(keepAlive)

    @QtCore.pyqtProperty(bool, notify=cleanSessionChanged)
    def cleanSession(self):
        return self.m_cleanSession

    @cleanSession.setter
    def cleanSession(self, cleanSession):
        if self.m_cleanSession == cleanSession: return
        self.m_cleanSession = cleanSession
        self.cleanSessionChanged.emit(cleanSession)

    @QtCore.pyqtProperty(int, notify=protocolVersionChanged)
    def protocolVersion(self):
        return self.m_protocolVersion

    @protocolVersion.setter
    def protocolVersion(self, protocolVersion):
        if self.m_protocolVersion == protocolVersion: return
        if protocolVersion in (MqttClient.MQTT_3_1,MqttClient.MQTT_3_1_1):
            self.m_protocolVersion = protocolVersion
            self.protocolVersionChanged.emit(protocolVersion)

    #################################################################
    @QtCore.pyqtSlot()
    def connectToHost(self):
        if self.m_hostname:
            self.m_client.connect(self.m_hostname, 
                port=self.port)

            self.state = MqttClient.Connecting
            self.m_client.loop_start()

    @QtCore.pyqtSlot()
    def disconnectFromHost(self):
        self.m_client.disconnect()

    def subscribe(self, path):
        if self.state == MqttClient.Connected:
            self.m_client.subscribe(path)

    #################################################################
    # callbacks
    def on_message(self, mqttc, obj, msg):
        mstr = msg.payload.decode("ascii")
        # print("on_message", mstr, obj, mqttc)
        self.messageSignal.emit(mstr)

    def on_connect(self, *args):
        # print("on_connect", args)
        self.state = MqttClient.Connected
        self.connected.emit()

    def on_disconnect(self, *args):
        # print("on_disconnect", args)
        self.state = MqttClient.Disconnected
        self.disconnected.emit()

class MainWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.neededCodes=[]
        self.rightCodes=[]
        self.wrongCodes=[]
        self.setWindowTitle("Camera gate")
        self.resize(1000,300)
        self.nedded = ["1234","5678","9087","https://www.kwch.com/"]
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        tabs=QTabWidget()

        tabs.addTab(self.getDatabases(),"Databases")
        
        tabs.addTab(self.getCameraView(),"Cameras")
        
        layout.addWidget(tabs)

        self.client = MqttClient(self)
        self.client.stateChanged.connect(self.on_stateChanged)
        self.client.messageSignal.connect(self.on_messageSignal)

        self.client.hostname = "85e5f62c47ba413e8fa64e36d2ab5a34.s1.eu.hivemq.cloud"
        self.client.connectToHost()

    @QtCore.pyqtSlot(int)
    def on_stateChanged(self, state):
        print("Subscibed")
        self.client.subscribe("id_kamion/naklad")

    @QtCore.pyqtSlot(str)
    def on_messageSignal(self, msg):
       
        print("Message on buffer")

        if str(msg) in self.nedded:
            if str(msg) not in self.rightCodes:
                
                self.rightField.appendPlainText(str(msg) + '\n')
                self.rightCodes.append(str(msg))
        else:
            if str(msg) not in self.wrongCodes:
                self.wrongField.appendPlainText(str(msg) + '\n')
                self.wrongCodes.append(str(msg))
                
        

       
    def getDatabases(self):
        generalTab = QWidget()

        layout = QHBoxLayout()
        generalTab.setLayout(layout)
        flo = QFormLayout()
        commentLable = QLabel('Right detected codes')
        self.rightField = QPlainTextEdit()
        for text in self.rightCodes:
            self.rightField.appendPlainText(text + '\n')
        
        flo.addRow(commentLable,self.rightField)


        commentLable = QLabel('False detected codes')
        self.wrongField = QPlainTextEdit()
        flo.addRow(commentLable, self.wrongField)
        layout.addLayout(flo)


        flo = QFormLayout()
        commentLable = QLabel('Need to be loaded')
        self.neddedField = QPlainTextEdit()
        flo.addRow(commentLable, self.neddedField)
        layout.addLayout(flo)
        for text in self.nedded:
            self.neddedField.appendPlainText(text + '\n')

       



        return generalTab
    def onUpdateText(self, text):
        #self.outputWidget.clear()
        self.rightCodes.insertPlainText(text)
        #self.outputWidget.ensureCursorVisible()

    def textChanged(self,newstr):
        print(newstr)

    def getCameraView(self):
        generalTab = QMainWindow()

        
        

        return generalTab