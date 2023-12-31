from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
                            QRect, QSize, QUrl, Qt, Signal, QEvent)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
                           QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
                           QRadialGradient, QWindow, QKeyEvent)
from PySide2.QtWidgets import *
import pyaudio
import keyboard
import pyautogui
import aubio
import numpy as np
import threading
import os
import sys

# initializations
audio = pyaudio.PyAudio()
script_dir = None
if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(sys.executable)
elif __file__:
    script_dir = os.path.dirname(__file__)
script_dir = script_dir+"/assets"



class Ui_MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # instances
        self.audio_thread = None
        self.stream = None

        # audio settings
        self.buffer_size = 1024
        self.pyaudio_format = pyaudio.paFloat32
        self.n_channels = 1
        self.samplerate = 48000
        self.lowest_pitch = 5
        self.testing = False

        # action instance
        self.action_handler = ActionHandler()
        
        # get the image path
        self.background_image = os.path.join(script_dir, "background.jpg")
        self.background_image = self.background_image.replace("\\", "/")

        self.green_signal = os.path.join(script_dir, "signal.png")
        self.green_signal = self.green_signal.replace("\\", "/")

        self.grey_signal = os.path.join(script_dir, "no_signal.png")
        self.grey_signal = self.grey_signal.replace("\\", "/")

        self.test_image = os.path.join(script_dir, "tune.png")
        self.test_image = self.test_image.replace("\\", "/")

        self.logo = os.path.join(script_dir, "logo.png")
        self.logo = self.logo.replace("\\", "/")

    
    def setupUi(self, MainWindow):

        if MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1225, 825)
        MainWindow.setMinimumSize(QSize(1225, 825))
        MainWindow.setMaximumSize(QSize(1225, 825))

        # close event
        MainWindow.closeEvent = self.closeEvent
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        # set tool window flag to hide it from taskbar
        MainWindow.setWindowFlags(Qt.Tool)


        ###############################
        # COMBO BOX FOR DRIVERS
        ###############################


        self.comboBox = QComboBox(self.centralwidget)

        # get all devices and add them to the combo box
        devices_list = []
        for i in range(audio.get_device_count()):
            # if the device is of type "Line In" and matches samplerate and channels
            self.comboBox.addItem(str(i) +". "+audio.get_device_info_by_index(i)['name'])
        
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setGeometry(QRect(40, 760, 521, 41))
        self.comboBox.setStyleSheet(u"background-color: black;\n"
                                    "color: white;\n"
                                    "selection-background-color: black;")
        self.comboBox.setMaxCount(2147483645)
        self.comboBox.setIconSize(QSize(16, 16))

        # when the driver is changed in the combo box we call the changeDriver function
        self.comboBox.currentIndexChanged.connect(self.changeDriver)



        ###############################
        # BUTTON FOR TESTING
        ###############################

        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(620, 760, 61, 41))
        self.pushButton.setStyleSheet(u"background-color: rgba(225, 233, 245, 1);")
        icon = QIcon()
        iconThemeName = u"Dark"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(self.test_image, QSize(), QIcon.Normal, QIcon.Off)

        self.pushButton.setIcon(icon)
        self.pushButton.setIconSize(QSize(32, 30))
        self.pushButton.clicked.connect(self.on_pushButton_clicked)


        ###############################
        # BUTTON FOR SIGNAL STATUS
        ###############################


        self.pushButton_2 = QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(570, 760, 41, 41))
        self.pushButton_2.setStyleSheet(u"background-color: black;")
        icon1 = QIcon()
        icon1.addFile(u"no_signal.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_2.setIcon(icon1)
        self.pushButton_2.setIconSize(QSize(32, 20))


        ###############################
        # TABLE WIDGET FOR NOTES
        ###############################

        self.tableWidget = QTableWidget(self.centralwidget)
        if (self.tableWidget.columnCount() < 2):
            self.tableWidget.setColumnCount(2)
        font = QFont()
        font.setKerning(True)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setTextAlignment(Qt.AlignCenter)
        __qtablewidgetitem.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        if (self.tableWidget.rowCount() < 12):
            self.tableWidget.setRowCount(12)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(1, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(2, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(3, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(4, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(5, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(6, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(7, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(8, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(9, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(10, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(11, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        __qtablewidgetitem14.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(0, 0, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        __qtablewidgetitem15.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(0, 1, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        __qtablewidgetitem16.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(1, 0, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        __qtablewidgetitem17.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(1, 1, __qtablewidgetitem17)
        __qtablewidgetitem18 = QTableWidgetItem()
        __qtablewidgetitem18.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(2, 0, __qtablewidgetitem18)
        __qtablewidgetitem19 = QTableWidgetItem()
        __qtablewidgetitem19.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(2, 1, __qtablewidgetitem19)
        __qtablewidgetitem20 = QTableWidgetItem()
        __qtablewidgetitem20.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(3, 0, __qtablewidgetitem20)
        __qtablewidgetitem21 = QTableWidgetItem()
        __qtablewidgetitem21.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(3, 1, __qtablewidgetitem21)
        __qtablewidgetitem22 = QTableWidgetItem()
        __qtablewidgetitem22.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(4, 0, __qtablewidgetitem22)
        __qtablewidgetitem23 = QTableWidgetItem()
        __qtablewidgetitem23.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(4, 1, __qtablewidgetitem23)
        __qtablewidgetitem24 = QTableWidgetItem()
        __qtablewidgetitem24.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(5, 0, __qtablewidgetitem24)
        __qtablewidgetitem25 = QTableWidgetItem()
        __qtablewidgetitem25.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(5, 1, __qtablewidgetitem25)
        __qtablewidgetitem26 = QTableWidgetItem()
        __qtablewidgetitem26.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(6, 0, __qtablewidgetitem26)
        __qtablewidgetitem27 = QTableWidgetItem()
        __qtablewidgetitem27.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(6, 1, __qtablewidgetitem27)
        __qtablewidgetitem28 = QTableWidgetItem()
        __qtablewidgetitem28.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(7, 0, __qtablewidgetitem28)
        __qtablewidgetitem29 = QTableWidgetItem()
        __qtablewidgetitem29.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(7, 1, __qtablewidgetitem29)
        __qtablewidgetitem30 = QTableWidgetItem()
        __qtablewidgetitem30.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(8, 0, __qtablewidgetitem30)
        __qtablewidgetitem31 = QTableWidgetItem()
        __qtablewidgetitem31.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(8, 1, __qtablewidgetitem31)
        __qtablewidgetitem32 = QTableWidgetItem()
        __qtablewidgetitem32.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(9, 0, __qtablewidgetitem32)
        __qtablewidgetitem33 = QTableWidgetItem()
        __qtablewidgetitem33.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(9, 1, __qtablewidgetitem33)
        __qtablewidgetitem34 = QTableWidgetItem()
        __qtablewidgetitem34.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(10, 0, __qtablewidgetitem34)
        __qtablewidgetitem35 = QTableWidgetItem()
        __qtablewidgetitem35.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(10, 1, __qtablewidgetitem35)
        __qtablewidgetitem36 = QTableWidgetItem()
        __qtablewidgetitem36.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(11, 0, __qtablewidgetitem36)
        __qtablewidgetitem37 = QTableWidgetItem()
        __qtablewidgetitem37.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(11, 1, __qtablewidgetitem37)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setGeometry(QRect(40, 170, 1001, 561))


        font1 = QFont()
        font1.setFamily(u"Montserrat")
        font1.setPointSize(16)
        font1.setBold(False)
        font1.setItalic(True)
        font1.setWeight(50)
        self.tableWidget.setFont(font1)
        self.tableWidget.setStyleSheet(u"background-color: rgba(0, 0, 0, 0.6);\n"
                                       "color: red;\n"
                                       "")
        self.tableWidget.setShowGrid(True)
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget.horizontalHeader().setMinimumSectionSize(48)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(499)
        self.tableWidget.horizontalHeader().setHighlightSections(True)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setMinimumSectionSize(32)
        self.tableWidget.verticalHeader().setDefaultSectionSize(44)

        # make the table fixed size
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        # make the table not editable
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(0, 0, 1231, 831))
        self.label.setMinimumSize(QSize(0, 0))
        self.label.setStyleSheet(f"background-image: url(" + self.background_image + ");\n"
                               "background-position: center;\n")
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(690, 760, 81, 41))
        font3 = QFont()
        font3.setFamily(u"Montserrat")
        self.label_3.setFont(font3)
        self.label_3.setAlignment(Qt.AlignCenter)

        # make text larger and white
        self.label_3.setStyleSheet(u"color: white;\n"
                                    "font-size: 24px;")

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(40, 20, 711, 121))
        font2 = QFont()
        font2.setFamily(u"Vladimir Script")
        font2.setPointSize(72)
        font2.setBold(True)
        font2.setItalic(True)
        font2.setWeight(75)
        self.label_2.setFont(font2)
        self.label_2.setStyleSheet(u"color: red;")
        MainWindow.setCentralWidget(self.centralwidget)
        self.label.raise_()
        self.comboBox.raise_()
        self.pushButton.raise_()
        self.pushButton_2.raise_()
        self.tableWidget.raise_()
        self.label_3.raise_()
        self.label_2.raise_()

        
        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    # retranslateUi

    # don't know what happens here. but it is important.
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate(
            "MainWindow", u"SOWS", None))
        MainWindow.setWindowFlags(Qt.WindowStaysOnTopHint)

        # mainwindow icon
        icon = QIcon()
        icon.addFile(self.logo, QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)

        # set taskbar icon



        self.comboBox.setCurrentText(
            QCoreApplication.translate("MainWindow", u"Select Driver", None))
        self.pushButton.setText("")
        self.pushButton_2.setText("")
        ___qtablewidgetitem = self.tableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(
            QCoreApplication.translate("MainWindow", u"Notes", None))
        ___qtablewidgetitem1 = self.tableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(
            QCoreApplication.translate("MainWindow", u"Actions", None))
        ___qtablewidgetitem2 = self.tableWidget.verticalHeaderItem(0)
        ___qtablewidgetitem2.setText(
            QCoreApplication.translate("MainWindow", u"1", None))
        ___qtablewidgetitem3 = self.tableWidget.verticalHeaderItem(1)
        ___qtablewidgetitem3.setText(
            QCoreApplication.translate("MainWindow", u"2", None))
        ___qtablewidgetitem4 = self.tableWidget.verticalHeaderItem(2)
        ___qtablewidgetitem4.setText(
            QCoreApplication.translate("MainWindow", u"3", None))
        ___qtablewidgetitem5 = self.tableWidget.verticalHeaderItem(3)
        ___qtablewidgetitem5.setText(
            QCoreApplication.translate("MainWindow", u"4", None))
        ___qtablewidgetitem6 = self.tableWidget.verticalHeaderItem(4)
        ___qtablewidgetitem6.setText(
            QCoreApplication.translate("MainWindow", u"5", None))
        ___qtablewidgetitem7 = self.tableWidget.verticalHeaderItem(5)
        ___qtablewidgetitem7.setText(
            QCoreApplication.translate("MainWindow", u"6", None))
        ___qtablewidgetitem8 = self.tableWidget.verticalHeaderItem(6)
        ___qtablewidgetitem8.setText(
            QCoreApplication.translate("MainWindow", u"7", None))
        ___qtablewidgetitem9 = self.tableWidget.verticalHeaderItem(7)
        ___qtablewidgetitem9.setText(
            QCoreApplication.translate("MainWindow", u"8", None))
        ___qtablewidgetitem10 = self.tableWidget.verticalHeaderItem(8)
        ___qtablewidgetitem10.setText(
            QCoreApplication.translate("MainWindow", u"9", None))
        ___qtablewidgetitem11 = self.tableWidget.verticalHeaderItem(9)
        ___qtablewidgetitem11.setText(
            QCoreApplication.translate("MainWindow", u"10", None))
        ___qtablewidgetitem12 = self.tableWidget.verticalHeaderItem(10)
        ___qtablewidgetitem12.setText(
            QCoreApplication.translate("MainWindow", u"11", None))
        ___qtablewidgetitem13 = self.tableWidget.verticalHeaderItem(11)
        ___qtablewidgetitem13.setText(
            QCoreApplication.translate("MainWindow", u"12", None))

        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setSortingEnabled(False)
        ___qtablewidgetitem14 = self.tableWidget.item(0, 0)
        ___qtablewidgetitem14.setText(
            QCoreApplication.translate("MainWindow", u"C", None))
        ___qtablewidgetitem15 = self.tableWidget.item(0, 1)
        ___qtablewidgetitem15.setText(QCoreApplication.translate(
            "MainWindow", u"Move Forwards", None))
        ___qtablewidgetitem16 = self.tableWidget.item(1, 0)
        ___qtablewidgetitem16.setText(
            QCoreApplication.translate("MainWindow", u"C#", None))
        ___qtablewidgetitem17 = self.tableWidget.item(1, 1)
        ___qtablewidgetitem17.setText(
            QCoreApplication.translate("MainWindow", u"Move Left", None))
        ___qtablewidgetitem18 = self.tableWidget.item(2, 0)
        ___qtablewidgetitem18.setText(
            QCoreApplication.translate("MainWindow", u"D", None))
        ___qtablewidgetitem19 = self.tableWidget.item(2, 1)
        ___qtablewidgetitem19.setText(QCoreApplication.translate(
            "MainWindow", u"Move Backwards", None))
        ___qtablewidgetitem20 = self.tableWidget.item(3, 0)
        ___qtablewidgetitem20.setText(
            QCoreApplication.translate("MainWindow", u"D#", None))
        ___qtablewidgetitem21 = self.tableWidget.item(3, 1)
        ___qtablewidgetitem21.setText(
            QCoreApplication.translate("MainWindow", u"Move Right", None))
        ___qtablewidgetitem22 = self.tableWidget.item(4, 0)
        ___qtablewidgetitem22.setText(
            QCoreApplication.translate("MainWindow", u"E", None))
        ___qtablewidgetitem23 = self.tableWidget.item(4, 1)
        ___qtablewidgetitem23.setText(QCoreApplication.translate(
            "MainWindow", u"Turn 45\u00b0 left", None))
        ___qtablewidgetitem24 = self.tableWidget.item(5, 0)
        ___qtablewidgetitem24.setText(
            QCoreApplication.translate("MainWindow", u"F", None))
        ___qtablewidgetitem25 = self.tableWidget.item(5, 1)
        ___qtablewidgetitem25.setText(QCoreApplication.translate(
            "MainWindow", u"Turn 45\u00b0 right", None))
        ___qtablewidgetitem26 = self.tableWidget.item(6, 0)
        ___qtablewidgetitem26.setText(
            QCoreApplication.translate("MainWindow", u"F#", None))
        ___qtablewidgetitem27 = self.tableWidget.item(6, 1)
        ___qtablewidgetitem27.setText(QCoreApplication.translate(
            "MainWindow", u"Turn 90\u00b0 left", None))
        ___qtablewidgetitem28 = self.tableWidget.item(7, 0)
        ___qtablewidgetitem28.setText(
            QCoreApplication.translate("MainWindow", u"G", None))
        ___qtablewidgetitem29 = self.tableWidget.item(7, 1)
        ___qtablewidgetitem29.setText(QCoreApplication.translate(
            "MainWindow", u"Turn 90\u00b0 right", None))
        ___qtablewidgetitem30 = self.tableWidget.item(8, 0)
        ___qtablewidgetitem30.setText(
            QCoreApplication.translate("MainWindow", u"G#", None))
        ___qtablewidgetitem31 = self.tableWidget.item(8, 1)
        ___qtablewidgetitem31.setText(
            QCoreApplication.translate("MainWindow", u"Jump", None))
        ___qtablewidgetitem32 = self.tableWidget.item(9, 0)
        ___qtablewidgetitem32.setText(
            QCoreApplication.translate("MainWindow", u"A", None))
        ___qtablewidgetitem33 = self.tableWidget.item(9, 1)
        ___qtablewidgetitem33.setText(
            QCoreApplication.translate("MainWindow", u"Crouch", None))
        ___qtablewidgetitem34 = self.tableWidget.item(10, 0)
        ___qtablewidgetitem34.setText(
            QCoreApplication.translate("MainWindow", u"A#", None))
        ___qtablewidgetitem35 = self.tableWidget.item(10, 1)
        ___qtablewidgetitem35.setText(
            QCoreApplication.translate("MainWindow", u"Shoot", None))
        ___qtablewidgetitem36 = self.tableWidget.item(11, 0)
        ___qtablewidgetitem36.setText(
            QCoreApplication.translate("MainWindow", u"B", None))
        ___qtablewidgetitem37 = self.tableWidget.item(11, 1)
        ___qtablewidgetitem37.setText(
            QCoreApplication.translate("MainWindow", u"Reload", None))
        self.tableWidget.setSortingEnabled(__sortingEnabled)

        self.label.setText(QCoreApplication.translate(
            "MainWindow", u"TextLabel", None))
        self.label_2.setText(QCoreApplication.translate(
            "MainWindow", u"SOWS", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"---", None))

        # System Tray icon image
        icon_image = os.path.join(script_dir, "signal.png")
        icon1 = QIcon(icon_image)

        # System Tray Icon
        self.tray_icon = QSystemTrayIcon(MainWindow)
        self.tray_icon.setIcon(icon1)
        self.tray_icon.activated.connect(self.tray_activated)
        self.tray_icon.show()

        # add context menu to tray icon
        self.tray_icon_menu = QMenu(MainWindow)

        # Add actions to the menu
        quit_action = QAction("Quit", MainWindow)
        quit_action.triggered.connect(self.quit_application)
        self.tray_icon_menu.addAction(quit_action)

        # restore
        restore_action = QAction("Restore", MainWindow)
        restore_action.triggered.connect(self.show_window)
        self.tray_icon_menu.addAction(restore_action)

        # Add menu to tray icon
        self.tray_icon.setContextMenu(self.tray_icon_menu)
    
    
    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            MainWindow.showNormal()


    def show_window(self):
        # make window visible from tray icon
        MainWindow.showNormal()


    def quit_application(self):
        self.tray_icon.hide()
        # quit the application
        QApplication.quit()
    
    # function to handle the test button click
    def on_pushButton_clicked(self):
        if self.testing:
            # delete the thread
            self.audio_thread.stop()
            self.audio_thread.join()
            self.audio_thread = None
            self.testing = False
            self.label_3.setText("---")
            self.updateSignalStatus(False)

            # restart the audio thread
            self.audio_thread = AudioProcessingThread(self.buffer_size, self.samplerate, self.stream)
            self.audio_thread.signal_detected.connect(self.handleAudioSignal)
            self.audio_thread.start()
            self.updateSignalStatus(True)

            # make button color back to original
            self.pushButton.setStyleSheet(u"background-color: rgba(225, 233, 245, 1);")

        else:

            # release all keys
            self.action_handler.releaseAll()

            #check if any thread is running
            if self.audio_thread:
                self.audio_thread.stop()
                self.audio_thread.join()
                self.audio_thread = None

            # start audio thread
            self.audio_thread = AudioProcessingThread(self.buffer_size, self.samplerate, self.stream)
            self.audio_thread.signal_detected.connect(self.handleAudioSignal)
            self.audio_thread.start()
            self.testing = True

            # change button color
            self.pushButton.setStyleSheet(u"background-color: rgba(151, 153, 156, 1);")

    # function to change the driver    
    def changeDriver(self):
        if self.audio_thread:
            print("Stopping thread")
            self.audio_thread.stop()
            self.audio_thread.join()
            self.audio_thread = None
        
        # get the index of the driver
        selectedDriver = self.comboBox.currentText()
        selectedDriverIndex = selectedDriver.split(".")[0]

        try:

            if self.stream:
                self.stream.stop_stream()
                self.stream.close()

            self.stream = audio.open(format=self.pyaudio_format,
                                channels=self.n_channels,
                                rate=self.samplerate,
                                input=True,
                                frames_per_buffer=self.buffer_size,
                                input_device_index=int(selectedDriverIndex))

            # start audio thread
            self.audio_thread = AudioProcessingThread(self.buffer_size, self.samplerate, self.stream)
            #connect the signal to the handleAudioSignal function
            self.audio_thread.signal_detected.connect(self.handleAudioSignal)
            self.audio_thread.start()

            # update the signal status icon
            self.updateSignalStatus(True)

        except Exception as e:
            print("Error changing driver")
            self.updateSignalStatus(False)
            print(e)
    
    # function to handle the audio signal
    def handleAudioSignal(self, note):
        # update the label_3 text
        if self.testing:
            self.label_3.setText(note)
        else:
            # the entire action programming based on note is done here
            self.action_handler.handleAction(note)
    
    # function to update the signal status icon
    def updateSignalStatus(self, live):
        #change the signal status icon to signal.png instead of no_signal.png
        icon = QIcon()
        if live == True:
            icon.addFile(self.green_signal, QSize(), QIcon.Normal, QIcon.Off)
            self.pushButton_2.setIcon(icon)
        else:
            icon.addFile(self.grey_signal, QSize(), QIcon.Normal, QIcon.Off)
            self.pushButton_2.setIcon(icon)
        
    # close all threads when main window is closed
    def closeEvent(self, event):
        if self.audio_thread:
            self.audio_thread.stop()
            self.audio_thread.join()
            self.audio_thread = None
        event.accept()

# Filter class to prevent keyboard inputs interacting with the application
class CustomEventFilter(QObject, ):
    def eventFilter(self, obj, event):
        # if the event is a key press event then we return true
        prevent_list = ["PySide2.QtCore.QEvent.Type.KeyPress", "PySide2.QtCore.QEvent.Type.KeyRelease", "PySide2.QtCore.QEvent.Type.ShortcutOverride"]

        event_type = str(event.type())
        if event_type in prevent_list:
            return True
        else:
            return False

# class to handle all the actions.
class ActionHandler(QObject):
    
        def __init__(self):
            super().__init__()
            self.action_mapping = {
                "C": self.moveForward,
                "C#": self.moveLeft,
                "D": self.moveBackwards,
                "D#": self.moveRight,
                "E": self.turn45Left,
                "F": self.turn45Right,
                "F#": self.turn90Left,
                "G": self.turn90Right,
                "G#": self.jump,
                "A": self.crouch,
                "A#": self.shoot,
                "B": self.reload
            }

            # handle front-back and left-right navigation
            # Forward +1 and Backwards -1
            # Left +1 and Right -1
            self.navigation_mapping = [None, None]

            # toggle for crouch
            self.crouch_toggle = False
        
        def releaseAll(self):
            keyboard.release('w')
            keyboard.release('a')
            keyboard.release('s')
            keyboard.release('d')
            keyboard.release('ctrl')
        
        def handleAction(self, note):
            self.action_mapping[note]()

        # function to move forward or stop moving backwards
        def moveForward(self):
            if self.navigation_mapping[0] == None:
                self.navigation_mapping[0] = 1
                keyboard.press('w')
            elif self.navigation_mapping[0] == -1:
                self.navigation_mapping[0] = None
                keyboard.release('s')
        
        # function to move backwards or stop moving forward
        def moveBackwards(self):
            if self.navigation_mapping[0] == None:
                self.navigation_mapping[0] = -1
                keyboard.press('s')
            elif self.navigation_mapping[0] == 1:
                self.navigation_mapping[0] = None
                keyboard.release('w')
        
        # function to move left or stop moving right
        def moveLeft(self):
            if self.navigation_mapping[1] == None:
                self.navigation_mapping[1] = 1
                keyboard.press('a')
            elif self.navigation_mapping[1] == -1:
                self.navigation_mapping[1] = None
                keyboard.release('d')
        
        # function to move right or stop moving left
        def moveRight(self):
            if self.navigation_mapping[1] == None:
                self.navigation_mapping[1] = -1
                keyboard.press('d')
            elif self.navigation_mapping[1] == 1:
                self.navigation_mapping[1] = None
                keyboard.release('a')
        
        def turn45Left(self):
            # turn 45 degrees left using pyautogui
            pyautogui.moveRel(-100, 0, 0.5)
        
        def turn45Right(self):
            # turn 45 degrees right using pyautogui
            pyautogui.moveRel(100, 0, 0.5)
        
        def turn90Left(self):
            # turn 90 degrees left using pyautogui
            pyautogui.moveRel(-200, 0, 0.5)
        
        def turn90Right(self):
            # turn 90 degrees right using pyautogui
            pyautogui.moveRel(200, 0, 0.5)
        
        def jump(self):
            keyboard.press_and_release('space')
        
        # function to toggle crouch
        def crouch(self):
            if self.crouch_toggle == False:
                self.crouch_toggle = True
                keyboard.press('ctrl')
            else:
                self.crouch_toggle = False
                keyboard.release('ctrl')
        
        def shoot(self):
            # press and release left mouse button
            pyautogui.click()
        
        def reload(self):
            # press and release r
            keyboard.press_and_release('r')

# class to handle all the audio processing
class AudioProcessingThread(threading.Thread, QObject):

    # signal to emit when a note is detected
    signal_detected = Signal(str)

    def __init__(self, buffer_size, samplerate, stream):
        threading.Thread.__init__(self)
        QObject.__init__(self)
        self.listening = True
        self.buffer_size = buffer_size
        self.samplerate = samplerate
        self.stream = stream

    # function to stop the thread
    def stop(self):
        self.listening = False

    def run(self):

        # parameters for pitch detection
        tolerance = 0.9
        win_s = 8192  # fft size
        hop_s = self.buffer_size  # hop size
        pitch_o = aubio.pitch("default", win_s, hop_s, self.samplerate)
        pitch_o.set_unit("midi")
        pitch_o.set_tolerance(tolerance)
        
        # prevent sustain effect
        last_note = None

        # main loop
        while self.listening:
            try:
                aubiobuffer = self.stream.read(self.buffer_size)
                signal = np.fromstring(aubiobuffer, dtype=np.float32)

                if len(signal) == 0:
                    break
                
                pitch = pitch_o(signal)[0]

                if pitch >0:
                    pitch = int(round(pitch))
                    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

                    # Calculate the octave and note relative to the tuning factor
                    octave = int((pitch) / 12) - 1
                    note = notes[(pitch) % 12]

                    if last_note != note:
                        # Emit the signal
                        self.signal_detected.emit(note)
                        last_note = note
                else:
                    last_note = None


            except Exception as e:
                print("Error getting pitch")
                print(e)
    

if __name__ == "__main__":

    # import the necessary packages
    import sys

    # start the app
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    # install the event filter on the main window
    CustomEventFilter = CustomEventFilter()
    MainWindow.installEventFilter(CustomEventFilter)

    # add event filter to all the widgets
    for widget in MainWindow.findChildren(QWidget):
        widget.installEventFilter(CustomEventFilter)

    sys.exit(app.exec_())
    # run cleanup when the app is closed
    MainWindow.closeEvent()