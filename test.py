import RPi.GPIO as GPIO
import time
import os
import random
import datetime
import sys
from threading import Thread


from PyQt4.QtGui import QApplication, QTableWidget, QTableWidgetItem
from PyQt4 import QtCore
from PyQt4.QtWebKit import QWebView, QWebPage
from PyQt4.QtGui import QGridLayout, QLineEdit, QWidget, QHeaderView
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt4.Qt import QPushButton


from PyQt4 import QtCore, QtGui, uic

Tmp = datetime.datetime(2000,12,14) 
Start = Tmp.today()
print str(Start)
print "houla"


class UrlInput(QLineEdit):
    def __init__(self, browser):
        super(UrlInput, self).__init__()
        self.browser = browser
        self.returnPressed.connect(self._return_pressed)

    def _return_pressed(self):
        url = QtCore.QUrl(self.text())
        self.browser.load(url)


class JavaScriptEvaluator(QLineEdit):
    def __init__(self, page):
        super(JavaScriptEvaluator, self).__init__()
        self.page = page
        self.returnPressed.connect(self._return_pressed)

    def _return_pressed(self):
        frame = self.page.currentFrame()
        result = frame.evaluateJavaScript(self.text())

class ActionInputBox(QLineEdit):
    def __init__(self, page):
        super(ActionInputBox, self).__init__()
        self.page = page
        self.returnPressed.connect(self._return_pressed)

    def _return_pressed(self):
        frame = self.page.currentFrame()
        action_string = str(self.text()).lower()
        if action_string == "b":
            self.page.triggerAction(QWebPage.Back)
        elif action_string == "f":
            self.page.triggerAction(QWebPage.Forward)
        elif action_string == "s":
            self.page.triggerAction(QWebPage.Stop)
        elif action_string == "r":
            self.page.triggerAction(QWebPage.Reload)

class RequestsTable(QTableWidget):
    header = ["url", "status", "content-type"]

    def __init__(self):
        super(RequestsTable, self).__init__()
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(self.header)
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setResizeMode(QHeaderView.ResizeToContents)

    def update(self, data):
        last_row = self.rowCount()
        next_row = last_row + 1
        self.setRowCount(next_row)
        for col, dat in enumerate(data, 0):
            if not dat:
                continue
            self.setItem(last_row, col, QTableWidgetItem(dat))

class Manager(QNetworkAccessManager):
    def __init__(self, table):
        QNetworkAccessManager.__init__(self)
        self.finished.connect(self._finished)
        self.table = table

    def _finished(self, reply):
        headers = reply.rawHeaderPairs()
        headers = {str(k):str(v) for k,v in headers}
        content_type = headers.get("Content-Type")
        url = reply.url().toString()
        status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)





class MyApp(QtGui.QMainWindow):

    def _setBrowser(self, browser=None):
        self._browser = browser

    def _getBrowser(self):
        return self._browser

    browser = property(_getBrowser, _setBrowser)

    # Interact with the HTML page by calling the completeAndReturnName
    # function; print its return value to the console
    def run_video(self):
        print ('Enetered run_vudeo')
        frame = self._getBrowser().page().mainFrame()
        print frame.evaluateJavaScript('playPause();')


    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        #Ui_MainWindow.__init__(self)
        #self.setupUi(self)
        #self.lcdNumber.display(10.1)
        #self.label.setText("Essai de texte")

        grid = QGridLayout()
        self._setBrowser(QWebView())
        url_input = UrlInput(self.browser)
        url_input.setText("file:/home/pi/rPiBrowserPrototype/testHtml5.html")
        requests_table = RequestsTable()
        loadButton = QPushButton()
        loadButton.setText("Load Video")
        loadButton.clicked.connect(url_input._return_pressed)

        playButton = QPushButton()
        playButton.setText("Play Video")
        playButton.clicked.connect(self.run_video)

        manager = Manager(requests_table)
        page = QWebPage()
        page.setNetworkAccessManager(manager)
        self.browser.setPage(page)

        js_eval = JavaScriptEvaluator(page)
        action_box = ActionInputBox(page)

        grid.addWidget(url_input, 1, 0)
        grid.addWidget(action_box, 2, 0)
        grid.addWidget(self.browser, 3, 0)
        grid.addWidget(requests_table, 4, 0)
        grid.addWidget(js_eval, 5, 0)
        grid.addWidget(loadButton, 6,0)
        grid.addWidget(playButton, 6,1)

        main_frame = QWidget()
        main_frame.setLayout(grid)
        self.setCentralWidget(main_frame)
        
    def closeEvent(self, event):
        print("event")
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Want to quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            GPIO.cleanup()       # clean up GPIO on CTRL+C exit
            GPIO.cleanup()           # clean up GPIO on normal exit
            event.accept()
        else:
            event.ignore()

    def my_Start(self, channel): #Interrupt 18
        self.run_video()
        print "start"

 
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(17, GPIO.BOTH, callback=window.my_Start, bouncetime=100)
    #GPIO.add_event_detect(17, GPIO.RISING, callback=window.my_Stop, bouncetime=2000)
    window.show()
    sys.exit(app.exec_())
    print "houla2"
