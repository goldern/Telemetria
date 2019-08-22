#!/usr/bin/env python
# encoding: utf-8


##Pré-requisitos:
#
#Dronekit: pip install dronekit
#OpenCV: pip install opencv-python
#Serial: pip install pyserial
#
##NODE.JS
# npm install socket.io
# npm install express
# npm install express-handlebars
#
#Opcional:
#Dronekit SITL(simulador): pip install dronekit-sitl

from kivy.app import App
#kivy.require("1.10.1")

from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.behaviors import DragBehavior
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.lang import Builder
from functools import partial
from kivy.clock import Clock
from io import BytesIO
import json
from json import dumps, loads, JSONEncoder, JSONDecoder
import random

# Import Flask and Flask-SocketIO
import socket
import socketio
import logging
logging.basicConfig()
autopilot_logger = logging.getLogger('autopilot')
dronekit_logger = logging.getLogger('dronekit')
autopilot_logger.setLevel(logging.DEBUG)
dronekit_logger.setLevel(logging.DEBUG)
# Import OpenCV
import cv2
# Import DroneKit-Python
from dronekit import connect, VehicleMode
# Import Serial Port searcher
import serial.tools.list_ports

# Define app as current app
app = App.get_running_app()
# Define globals
vehicle = None
servidor = None
# Define global dictionary
global dictValues
dictValues = {}

class DragLabel(DragBehavior, Label):
    drag_id = StringProperty('')
    pass

class LabeledCheckbox(BoxLayout):
    text = StringProperty('')
    active = BooleanProperty(False)
    pass

class MainScreen(Screen):
    def on_enter(self):
        #for x in dictValues:
        #    print(dictValues[x])
        #print("ABRIU MAIN")
        pass
    
class CameraScreen(Screen):
    addedWidgets = []
    #Definir variáveis temporárias
    oldVelocity = None
    oldAtitude = None
    oldBattery = None
    oldGPS = None
    oldHeartbeat = None
    
    def on_enter(self):
        self.addChildWidgets()                   
        event = Clock.schedule_interval(self.update, 1)
        self.cam = cv2.VideoCapture(0)
        event2 = Clock.schedule_interval(self.update2, 1.0 / 30)
        #print("ABRIU CAMERA")
    def on_leave(self):
        event = Clock.unschedule(self.update)
        event2 = Clock.unschedule(self.update2)
        #without this, app will not exit even if the window is closed
        self.cam.release()
    def update(self, dt):
        app = App.get_running_app()

        for x in self.addedWidgets:
            #print(x.text)
            if(x.text == "Velocidade" or x.text == self.oldVelocity):
                x.text = app.getVelocity(vehicle)
                self.oldVelocity = x.text
                x.size = x.texture_size
            if(x.text == "Atitude" or x.text == self.oldAtitude):
                x.text = app.getAttitude(vehicle)
                self.oldAtitude = x.text
                x.size = x.texture_size
            if(x.text == "Bateria" or x.text == self.oldBattery):
                x.text = app.getBattery(vehicle)
                self.oldBattery = x.text
                x.size = x.texture_size
            if(x.text == "Heartbeat" or x.text == self.oldHeartbeat):
                x.text = app.getLastHeartbeat(vehicle)[:16]
                self.oldHeartbeat = x.text
                x.size = x.texture_size
            if(x.text == "GPS" or x.text == self.oldGPS):
                x.text = app.getGPS(vehicle)
                self.oldGPS = x.text
                x.size = x.texture_size

        # Se estiver conectado, enviar bytes ao servidor
        if(servidor != None):
            coreImage = self.ids.cameraId.export_as_image()
            png = BytesIO()
            coreImage.save(png, fmt='png')
            png.seek(0)
            byte = png.read()
            servidor.emit('message', byte)

    def update2(self, dt):
        try:
            ret, frame = self.cam.read()
            if ret:
                # convert it to texture
                buf1 = cv2.flip(frame, 0)
                buf = buf1.tostring()
                texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.ids.videos.texture = texture1
        except:
            pass
            
    def addChildWidgets(self):
        #print("addChildWidgets")
        repetido = [False, False, False, False, False]
        app = App.get_running_app()
        with open("varstatus.txt") as f:
            bufferDict = json.load(f, encoding='utf-8')
        for idx, x in enumerate(bufferDict):
            if(bufferDict[x] == True):
                if x not in self.addedWidgets:
                    for y in self.addedWidgets:
                        if(y.drag_id == x):
                            repetido[idx] = True
                            break
                    if(repetido[idx] == False):
                        app = App.get_running_app()
                        w = DragLabel(text= x, drag_id= x)
                        #print("texto: " + x)
                        w.x = 20
                        w.y = 500 + 20 * idx
                        w.opacity = 0
                        #print("Reset")
                        app.root.ids.camerascreen.ids.videos.add_widget(w)
                        self.addedWidgets.append(w)
        for x in bufferDict:
            if(bufferDict[x] == False):
                for y in self.addedWidgets:
                    if(y.drag_id == x):
                        #print(y)
                        #y.remove_widget(self)
                        y.opacity = 0
            if(bufferDict[x] == True):
                for y in self.addedWidgets:
                    if(y.drag_id == x):
                        y.opacity = 1


class ConfigScreen(Screen):
    def on_enter(self):
        #for x in dictValues:
        #    print(x, dictValues[x])
        #print("ABRIU CONFIGS")
        pass
            
class MyBoxLayout(BoxLayout):
    def changeOpacity(self, new_opacity):
        self.opacity = new_opacity
    def changeHeight(self, new_height):
        self.height = new_height    

class ScreenManagement(ScreenManager):
    pass



#Carregar arquivo KV com o layout do app
presentation = Builder.load_file("main2.kv")

class MainApp(App):
    global dictValues
    def build(self):
        return presentation
    def conectarSITL(self):
        global vehicle
        # Iniciar Simulador
        print ("Start simulator (SITL)")
        import dronekit_sitl
        sitl = dronekit_sitl.start_default()
        connection_string = sitl.connection_string()
        # Conectar ao veículo
        print("Connecting to vehicle on: %s" % (connection_string,))
        vehicle = connect(connection_string, wait_ready=True)

        #Adicionar os LabeledCheckbox:
        self.addLabeledCheckbox("Velocidade")
        self.addLabeledCheckbox("Atitude")
        self.addLabeledCheckbox("GPS")
        self.addLabeledCheckbox("Bateria")
        self.addLabeledCheckbox("Heartbeat")
        dictValues={"Velocidade": False,
                    "Atitude":    False,
                    "GPS":        False,
                    "Bateria":    False,
                    "Heartbeat":  False}
        with open('varstatus.txt', 'w') as f:
            f.write(json.dumps(dictValues))
    def conectarUSB(self, comPort):
        global vehicle
        print("Start USB serial port search (COM)")

        #Procurar a porta serial aqui
        connection_string = "com" + comPort
        
        print("Connecting to vehicle on: %s" % (connection_string,))
        try:
            vehicle = connect(connection_string, wait_ready=True)
            self.addLabeledCheckbox("Velocidade")
            self.addLabeledCheckbox("Atitude")
            self.addLabeledCheckbox("GPS")
            self.addLabeledCheckbox("Bateria")
            self.addLabeledCheckbox("Heartbeat")
            dictValues={"Velocidade": False,
                        "Atitude":    False,
                        "GPS":        False,
                        "Bateria":    False,
                        "Heartbeat":  False}
            with open('varstatus.txt', 'w') as f:
                f.write(json.dumps(dictValues))
        except:
            pass
    def addLabeledCheckbox(self, texto):
        app = App.get_running_app()
        app.root.ids.configscreen.ids.container.add_widget(LabeledCheckbox(text= texto, active= False))
    def connect_server(self, sip, sport): # O QUE ACONTECE AO PRESSIONAR 'CONECTAR' NO MENU DO SERVIDOR
        global servidor
        try:
            servidor = socketio.Client(binary=True)
            servidor.connect('http://'+sip.text+':'+sport.text)

            httpd = SocketServer.ThreadingTCPServer(('', int(sport.text)), my_handler)
            httpd.serve_forever()
            
            print("Connection success")
        except:
            print("Connection failed")
        
    def on_stop(self): # O QUE ACONTECE AO SAIR DO APP
        try:
            # Close vehicle object before exiting script
            vehicle.close()
        except:
            pass
        try:
            # Shut down simulator
            sitl.stop()
            #print("SITL is not running")
        except:
            pass
        print("Completed")
        
    def getVelocity(self, vehicle):
        try:
            resultado = "Velocidade: '{0}'".format(vehicle.velocity)
        except:
            resultado = ""
        return resultado
    def getAttitude(self, vehicle):
        try:
            resultado = "Atitude: '{0}'".format(vehicle.attitude)
        except:
            resultado = ""
        return resultado
    def getBattery(self, vehicle):
        try:
            resultado = "Bateria: '{0}'".format(vehicle.battery)
        except:
            resultado = ""
        return resultado
    def getGPS(self, vehicle):
        try:
            resultado = "GPS: '{0}'".format(vehicle.location.global_frame)
        except:
            resultado = ""
        return resultado
    def getLastHeartbeat(self, vehicle):
        try:
            resultado = "Heartbeat: {0}".format(vehicle.last_heartbeat)
        except:
            resultado = ""
        return resultado
    def setActive(self, text, ativo):
        with open("varstatus.txt") as f:
            bufferDict = json.load(f, encoding='utf-8')
        for x in bufferDict:
            if(x == text):
                if(bufferDict[x] == False):
                    bufferDict[x] = True
                elif(bufferDict[x] == True):
                    bufferDict[x] = False
        with open('varstatus.txt', 'w') as json_file:
            json.dump(bufferDict, json_file)
        
    
if __name__ == "__main__":
    MainApp().run()
