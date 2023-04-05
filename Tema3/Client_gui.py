import psutil as psutil
from PyQt5 import QtCore, QtGui, QtWidgets, QtTest
import socket
import rsa_library
import _pickle as cPickle
import os
import threading
import sys, time

HOST = 'localhost'
PORT = 12346
airbag_on = '0xfe01'
corrupted_low = '0x5732'
corrupted_high = '0x5701'


class Ui_MainWindow(object):
    se = 0
    priv_k = 0
    pub_k = 0
    modul = 0
    ok1 = False
    ok_airbag = False
    ok_low = False
    ok_high = False

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(600, 500)
        MainWindow.setWindowTitle('Client')
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        MainWindow.setCentralWidget(self.centralwidget)

        self.centralwidget.setStyleSheet("background-color:white;")

        # Start client button
        self.client_start = QtWidgets.QPushButton(MainWindow)
        self.client_start.setText("Connect client")
        self.client_start.setStyleSheet("font: bold; font-size: 15px;")
        self.client_start.setGeometry(QtCore.QRect(200, 170, 200, 40))
        self.client_start.clicked.connect(self.start_client)

        self.client_label = QtWidgets.QLabel(self.centralwidget)
        self.client_label.setGeometry(QtCore.QRect(320, 170, 205, 41))
        self.client_label.setStyleSheet("font:bold;font-size: 15px;")

        # Connected label
        self.connected_label = QtWidgets.QLabel(self.centralwidget)
        self.connected_label.setGeometry(QtCore.QRect(200, 210, 200, 40))
        self.connected_label.setStyleSheet("font-size:15px;font:bold;qproperty-alignment: AlignCenter;")

        # Airbag on
        self.airbag = QtWidgets.QPushButton(MainWindow)
        self.airbag.setText("Airbag on")
        self.airbag.setStyleSheet("font: bold; font-size: 15px;")
        self.airbag.setGeometry(QtCore.QRect(70, 260, 211, 41))
        self.airbag.clicked.connect(self.send_on_data)
        self.airbag.setEnabled(False)

        # Airbag on label
        self.airbag_on_label = QtWidgets.QLabel(self.centralwidget)
        self.airbag_on_label.setGeometry(QtCore.QRect(300, 260, 200, 40))
        self.airbag_on_label.setStyleSheet("font-size:15px;font:bold;qproperty-alignment: AlignCenter;")

        # Corrupted low
        self.corrupted_low = QtWidgets.QPushButton(MainWindow)
        self.corrupted_low.setText("Corrupted low")
        self.corrupted_low.setStyleSheet("font: bold; font-size: 15px;")
        self.corrupted_low.setGeometry(QtCore.QRect(70, 330, 211, 41))
        self.corrupted_low.clicked.connect(self.send_corrupted_low)
        self.corrupted_low.setEnabled(False)

        # Corrupted low label
        self.corrupted_low_label = QtWidgets.QLabel(self.centralwidget)
        self.corrupted_low_label.setGeometry(QtCore.QRect(300, 330, 200, 40))
        self.corrupted_low_label.setStyleSheet("font-size:15px;font:bold;qproperty-alignment: AlignCenter;")

        # Corrupted high
        self.corrupted_high = QtWidgets.QPushButton(MainWindow)
        self.corrupted_high.setText("Corrupted high")
        self.corrupted_high.setStyleSheet("font: bold; font-size: 15px;")
        self.corrupted_high.setGeometry(QtCore.QRect(70, 400, 211, 41))
        self.corrupted_high.clicked.connect(self.send_corrupted_high)
        self.corrupted_high.setEnabled(False)

        # Corrupted high label
        self.corrupted_high_label = QtWidgets.QLabel(self.centralwidget)
        self.corrupted_high_label.setGeometry(QtCore.QRect(300, 400, 200, 40))
        self.corrupted_high_label.setStyleSheet("font-size:15px;font:bold;qproperty-alignment: AlignCenter;")

        # Continental image
        self.conti_label = QtWidgets.QLabel(self.centralwidget)
        self.conti_label.setGeometry(QtCore.QRect(110, 30, 400, 100))
        continental = QtGui.QImage(QtGui.QImageReader('./rsz_conti.png').read())
        self.conti_label.setPixmap(QtGui.QPixmap(continental))

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")

        MainWindow.setStatusBar(self.statusbar)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.show()

    ############################### EXERCISE 5 ###############################
    def start_client(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        self.se = client

        self.corrupted_low_label.clear()
        self.airbag_on_label.clear()
        self.corrupted_high_label.clear()
        self.airbag.setEnabled(False)
        self.corrupted_high.setEnabled(False)
        self.corrupted_low.setEnabled(False)
        print("Client connected")

        self.pub_k = int(client.recv(1024).decode())
        self.priv_k = int(client.recv(1024).decode())
        self.modul = int(client.recv(1024).decode())
        print("Received:", self.pub_k, self.priv_k, self.modul)

        self.recv_messages()

    ############################### EXERCISE 8 ###############################
    def recv_messages(self):
        self.stop_event = threading.Event()
        self.c_thread = threading.Thread(name='messages', target=self.recv_handler, args=(self.stop_event,))
        self.c_thread.start()

    def recv_handler(self, stop_event):
        print("The client received the messages")
        while stop_event:
            msg = self.se.recv(1024).decode()
            print("The message received by the client:", msg)
            private_key = (self.priv_k, self.modul)
            msg = rsa_library.decrypt(private_key, msg)
            print(msg)
            if msg == '0xfd02':
                print("Unlocking car")
                self.airbag.setEnabled(True)
                self.corrupted_low.setEnabled(True)
                self.corrupted_high.setEnabled(True)
            if self.ok_airbag:
                self.corrupted_low_label.setEnabled(False)
                self.corrupted_high_label.setEnabled(False)
                if msg.strip() == '0x0':
                    self.airbag_on_label.setText('Error')
                    self.airbag.setDisabled(True)
                    self.airbag.clearMask()
                elif msg.strip() == '0x1':
                    self.airbag_on_label.setText('Success')
            elif self.ok_low:
                self.airbag_on_label.setEnabled(False)
                self.corrupted_low_label.setEnabled(False)
                if msg.strip() == '0x1':
                    self.corrupted_low_label.setText('Success')
                elif msg.strip() == '0x0':
                    self.corrupted_low_label.setText('Error')
                    self.corrupted_low.setDisabled(True)
                    self.corrupted_low.clearMask()
            elif self.ok_high:
                self.corrupted_low_label.setEnabled(False)
                self.airbag_on_label.setEnabled(False)
                if msg.strip() == '0x1':
                    self.corrupted_high_label.setText('Success')
                elif msg.strip() == '0x0':
                    self.corrupted_high_label.setText('Error')
                    self.corrupted_high.setDisabled(True)
                    self.corrupted_high.clearMask()

    ############################### EXERCISE 9 ###############################
    def send_on_data(self):
        public_key = (self.pub_k, self.modul)
        msg = rsa_library.encrypt(public_key, airbag_on)
        self.se.send(str(msg).encode())
        self.ok_airbag = True
        self.ok_low = False
        self.ok_high = False
        print("Airbag on")

    ############################### EXERCISE 10 ###############################
    def send_corrupted_low(self):
        public_key = (self.pub_k, self.modul)
        msg = rsa_library.encrypt(public_key, corrupted_low)
        self.se.send(str(msg).encode())
        self.ok_airbag = False
        self.ok_low = True
        self.ok_high = False
        print("Corrupted low ")

    ############################### EXERCISE 11 ###############################
    def send_corrupted_high(self):
        public_key = (self.pub_k, self.modul)
        msg = rsa_library.encrypt(public_key, corrupted_high)
        self.se.send(str(msg).encode())
        self.ok_airbag = False
        self.ok_low = False
        self.ok_high = True
        print("Corrupted high")

    def kill_proc_tree(self, pid, including_parent=True):
        parent = psutil.Process(pid)
        if including_parent:
            parent.kill()


class MyWindow(QtWidgets.QMainWindow):
    def closeEvent(self, event):
        result = QtGui.QMessageBox.question(self,
                                            "Confirm Exit",
                                            "Are you sure you want to exit ?",
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

        if result == QtGui.QMessageBox.Yes:
            event.accept()
        elif result == QtGui.QMessageBox.No:
            event.ignore()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MyWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.center()
    sys.exit(app.exec_())

me = os.getpid()
# kill_proc_tree(me)
