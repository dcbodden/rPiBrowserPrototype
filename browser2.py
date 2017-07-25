import sys

from PyQt4.QtGui import QApplication, QTableWidget, QTableWidgetItem
from PyQt4 import QtCore 
from PyQt4.QtWebKit import QWebView, QWebPage
from PyQt4.QtGui import QGridLayout, QLineEdit, QWidget, QHeaderView
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt4.Qt import QPushButton

# GPIO stuff
import RPi.GPIO as GPIO
import time

butPin = 17 # Broadcom pin 17 (P1 pin 11)
# Pin Setup:
GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(butPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Button pin set as input w/ pull-up
# add rising edge detection on a channel, ignoring further edges for 200ms for switch bounce handling
channel = butPin

def my_callback(channel):
    print('This is a edge event callback function!')
    print('Edge detected on channel %s'%channel)
    print('This is run in a different thread to your main program')
    run_video()
    

GPIO.add_event_detect(channel, GPIO.RISING, callback=my_callback, bouncetime=100)

# end GPIO stuff


class UrlInput(QLineEdit):
    def __init__(self, browser):
        super(UrlInput, self).__init__()
        self.browser = browser
        self.returnPressed.connect(self._return_pressed)

    def _return_pressed(self):
        url = QtCore.QUrl(self.text())
        browser.load(url)


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

# Interact with the HTML page by calling the completeAndReturnName
# function; print its return value to the console
def run_video():
    print ('Enetered run_vudeo')
    frame = browser.page().mainFrame()
    print frame.evaluateJavaScript('playPause();')
 
if __name__ == "__main__":
    app = QApplication(sys.argv)

    grid = QGridLayout()
    browser = QWebView()
    url_input = UrlInput(browser)
    url_input.setText("file:/home/pi/rPiBrowserPrototype/testHtml5.html")
    requests_table = RequestsTable()
    loadButton = QPushButton()
    loadButton.setText("Load Video")
    loadButton.clicked.connect(url_input._return_pressed)
    
    playButton = QPushButton()
    playButton.setText("Play Video")
    playButton.clicked.connect(run_video)

    manager = Manager(requests_table)
    page = QWebPage()
    page.setNetworkAccessManager(manager)
    browser.setPage(page)

    js_eval = JavaScriptEvaluator(page)
    action_box = ActionInputBox(page)

    grid.addWidget(url_input, 1, 0)
    grid.addWidget(action_box, 2, 0)
    grid.addWidget(browser, 3, 0)
    grid.addWidget(requests_table, 4, 0)
    grid.addWidget(js_eval, 5, 0)
    grid.addWidget(loadButton, 6,0)
    grid.addWidget(playButton, 6,1)
    


    #GPIO.add_event_detect(channel, GPIO.RISING, callback=my_callback, bouncetime=200)


    main_frame = QWidget()
    main_frame.setLayout(grid)
    main_frame.show()

    sys.exit(app.exec_())
