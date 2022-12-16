import sys
from PyQt5 import uic, QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QColor, QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QCheckBox, QComboBox, QFileDialog, QMainWindow, QLabel, QPushButton, QSlider,QDialog
from PyQt5.uic import loadUi
import cv2 as cv
import threading
from threading import Event
import variables
import numpy as np
import os

power = True
locker = Event()

class Main(QDialog):
    def __init__(self):
        super(Main, self).__init__()
        print("sa")
        loadUi("ui.ui",self)

        self.selected_lower_hue = 0
        self.selected_lower_sat = 0
        self.selected_lower_value = 0

        self.selected_upper_hue = 179
        self.selected_upper_sat = 255
        self.selected_upper_value = 255

        self.lowerHSV = (0, 0, 0)
        self.upperHSV = (179, 255, 255)
        self.imgRaw = None
        self.imgMask = None
        self.imgMasked = None
        self.imgHsvSpace = cv.imread("./assets/hsv2.png")
        self.img = None
        self.imgcv = None
        self.img = None
        self.flag = False
        self.erotion_value = 0
        self.dial_value = 0

        self.Open.clicked.connect(self.openimage)
        self.open2.clicked.connect(self.openimage)

        self.lower_print.clicked.connect(self.print_hsv_to_console)
        self.upper_print.clicked.connect(self.print_hsv_to_console)

        self.slider_lower_hue.valueChanged.connect(self.hsv_changed)
        self.slider_lower_sat.valueChanged.connect(self.hsv_changed)
        self.slider_lower_value.valueChanged.connect(self.hsv_changed)

        self.slider_upper_hue.valueChanged.connect(self.hsv_changed)
        self.slider_upper_sat.valueChanged.connect(self.hsv_changed)
        self.slider_upper_val.valueChanged.connect(self.hsv_changed)

        self.slider_lower_erode.valueChanged.connect(self.erode_dialate_value_change_lower)
        self.slider_lower_dial.valueChanged.connect(self.erode_dialate_value_change_lower)
        self.slider_upper_erode.valueChanged.connect(self.erode_dialate_value_change_upper)
        self.slider_upper_dial.valueChanged.connect(self.erode_dialate_value_change_upper)

        self.checkbox_upper_erode.stateChanged.connect(self.erode_dialate_value_change_upper)
        self.checkbox_upper_dial.stateChanged.connect(self.erode_dialate_value_change_upper)
        self.checkbox_lower_erode.stateChanged.connect(self.erode_dialate_value_change_lower)
        self.checkbox_lower_dial.stateChanged.connect(self.erode_dialate_value_change_lower)

    def openimage(self):
        global power
        power = False
        options = QFileDialog.Options()
        filename = QFileDialog.getOpenFileName(
            self, "QFileDialog.getOpenFileName()", "", "All Files (*);;Jpeg (*.jpeg);;BMP (*.bmp)", options=options)
        if filename is None:
            return
        self.img = QPixmap(filename[0])
        self.imgcv = cv.imread(filename[0])
        print(self.img)
        self.previewRaw_2.setPixmap(self.img.scaled(self.previewRaw_2.size()))
        t1 = threading.Thread(target=self.thread2)
        t1.start()

    def hsv_changed(self):
        x = self.selected_lower_hue = self.slider_lower_hue.value()
        self.label_lower_hue.setText(str(f"QT5 ({x}) | cv2 ({x//2})"))
        x = self.selected_lower_sat = self.slider_lower_sat.value()
        self.label_lower_sat.setText(str(x))
        x = self.selected_lower_value = self.slider_lower_value.value()
        self.label_lower_value.setText(str(x))

        x = self.selected_upper_hue = self.slider_upper_hue.value()
        self.label_upper_hue.setText(str(f"QT5 ({x}) | cv2 ({x // 2})"))
        x = self.selected_upper_sat = self.slider_upper_sat.value()
        self.label_upper_sat.setText(str(x))
        x = self.selected_upper_value = self.slider_upper_val.value()
        self.label_lower_value.setText(str(x))

        self.flag = True
        locker.set()

    def print_hsv_to_console(self):
        print("Upper HSV: ", self.upperHSV)
        print("Lower HSV: ", self.lowerHSV)

    def erode_dialate_value_change_lower(self):
        self.checkbox_lower_erode.setText(f"Erode {self.slider_lower_erode.value()}")
        self.checkbox_lower_dial.setText(f"Dilate {self.slider_lower_dial.value()}")
        self.erotion_value = self.slider_lower_erode.value()
        self.dial_value = self.slider_lower_dial.value()

        self.slider_upper_erode.setValue(self.erotion_value)
        self.slider_upper_dial.setValue(self.dial_value)
        self.checkbox_upper_erode.setText(f"Erode {self.erotion_value}")
        self.checkbox_upper_dial.setText(f"Dilate {self.dial_value}")

        check = self.checkbox_lower_erode.isChecked()
        self.checkbox_upper_erode.setChecked(check)
        check = self.checkbox_lower_dial.isChecked()
        self.checkbox_upper_dial.setChecked(check)

        self.flag = True
        locker.set()

    def erode_dialate_value_change_upper(self):
        self.checkbox_upper_erode.setText(f"Erode {self.slider_upper_erode.value()}")
        self.checkbox_upper_dial.setText(f"Dilate {self.slider_upper_dial.value()}")
        self.erotion_value = self.slider_upper_erode.value()
        self.dial_value = self.slider_upper_dial.value()

        self.slider_lower_erode.setValue(self.erotion_value)
        self.slider_lower_dial.setValue(self.dial_value)
        self.checkbox_lower_erode.setText(f"Erode {self.erotion_value}")
        self.checkbox_lower_dial.setText(f"Dilate {self.dial_value}")

        check = self.checkbox_upper_erode.isChecked()
        self.checkbox_lower_erode.setChecked(check)
        check = self.checkbox_upper_dial.isChecked()
        self.checkbox_lower_dial.setChecked(check)

        self.flag = True
        locker.set()

    def thread2(self):
        global power
        power = True
        while power is True:
            if self.flag is True:
                self.flag = False
                self.updatemask()
                self.updatehsvpalette()
                locker.clear()
                print("1")
            else:
                print("2")
                locker.wait()

    def updatemask(self):
        if self.img is None:
            return

        self.lowerHSV = (self.selected_lower_hue // 2, self.selected_lower_sat, self.selected_lower_value)
        self.upperHSV = (self.selected_upper_hue // 2, self.selected_upper_sat, self.selected_upper_value)

        self.lower_lower_label.setText(f"H {self.lowerHSV[0]}; S {self.lowerHSV[1]}; V {self.lowerHSV[2]}")
        self.lower_upper_label.setText(f"H {self.upperHSV[0]}; S {self.upperHSV[1]}; V {self.upperHSV[2]}")
        self.upper_lower_label.setText(f"H {self.lowerHSV[0]}; S {self.lowerHSV[1]}; V {self.lowerHSV[2]}")
        self.upper_upper_label.setText(f"H {self.upperHSV[0]}; S {self.upperHSV[1]}; V {self.upperHSV[2]}")


        frame_HSV = cv.cvtColor(self.imgcv, cv.COLOR_BGR2HSV)
        lower_orange = np.array(self.lowerHSV)
        upper_orange = np.array(self.upperHSV)

        threshold = cv.inRange(frame_HSV, lower_orange, upper_orange)

        if self.checkbox_lower_erode.isChecked():
            threshold = cv.erode(threshold, np.ones((self.erotion_value, self.erotion_value), dtype=np.uint8))
        elif self.checkbox_upper_erode.isChecked():
            threshold = cv.erode(threshold, np.ones((self.erotion_value, self.erotion_value), dtype=np.uint8))

        if self.checkbox_lower_dial.isChecked():
            threshold = cv.dilate(threshold, np.ones((self.dial_value, self.dial_value), dtype=np.uint8))
        elif self.checkbox_upper_dial.isChecked():
            threshold = cv.dilate(threshold, np.ones((self.dial_value, self.dial_value), dtype=np.uint8))

        self.updatemaskraw(threshold)
        threshold = cv.cvtColor(threshold, cv.COLOR_GRAY2RGB)

        asQImage = QImage(threshold.data, threshold.shape[1],
                          threshold.shape[0], threshold.shape[1] * 3,QtGui.QImage.Format_RGB888)
        asQImage = asQImage.rgbSwapped()
        self.previewMask.setPixmap(QPixmap.fromImage(asQImage).scaledToHeight(self.previewMask.size().height()))

    def updatemaskraw(self, masking):
        if self.imgcv is None:
            return

        threshold = cv.bitwise_and(self.imgcv, self.imgcv, mask=masking)
        asQImage = QImage(
            threshold.data, threshold.shape[1], threshold.shape[0], threshold.shape[1] * 3,
            QtGui.QImage.Format_RGB888)
        asQImage = asQImage.rgbSwapped()
        self.previewMaskedRaw.setPixmap(QPixmap.fromImage(asQImage).scaledToHeight(self.previewMaskedRaw.size().height()))

    def updatehsvpalette(self):
        if self.imgHsvSpace is None:
            return
        frame_HSV = cv.cvtColor(self.imgHsvSpace, cv.COLOR_BGR2HSV)
        lower_orange = np.array(self.lowerHSV)
        upper_orange = np.array(self.upperHSV)
        masking = cv.inRange(frame_HSV, lower_orange, upper_orange)

        threshold = cv.bitwise_and(self.imgHsvSpace, self.imgHsvSpace, mask=masking)
        asQImage = QImage(
            threshold.data, threshold.shape[1], threshold.shape[0], threshold.shape[1] * 3,
            QtGui.QImage.Format_RGB888)
        asQImage = asQImage.rgbSwapped()
        self.previewHsvSpace.setPixmap(QPixmap.fromImage(asQImage).scaledToWidth(self.previewHsvSpace.size().width()))


def keep_alive():
    global power
    power = False
    locker.set()
    exit("Exit")


if __name__ == "__main__":
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)  # enable highdpi scaling
    app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)  # use highdpi icons
    app.lastWindowClosed.connect(keep_alive)
    mainwindow = Main()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(mainwindow)
    app.lastWindowClosed.connect(keep_alive)
    widget.setFixedWidth(1595)
    widget.setFixedHeight(900)
    widget.setWindowTitle("Hsv Range Tool")
    #widget.setWindowIcon(QtGui.QIcon('logo.png'))
    widget.show()
    app.exec_()
    sys.exit(app.exec_())