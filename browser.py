
import datetime
import sys
import threading
import os
import json

from PyQt4.QtGui import QTableWidget, QTableWidgetItem
from PyQt4.QtWebKit import QWebView, QWebPage
from PyQt4.QtGui import QGridLayout, QLineEdit, QWidget, QHeaderView
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt4.Qt import QPushButton
from PyQt4.Qt import QThread
from PyQt4 import QtCore, QtGui

GPIO_AVAILABLE=0
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = 1
except ImportError:
    print "No GPIO available, running in soft GUI mode."

Tmp = datetime.datetime(2000,12,14) 
Start = Tmp.today()
print str(Start)
print "hello"


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

class toddleCfgParser():
    
    _myJsonString = ""
    
    def __init__(self, jsonString):
        self._myJsonString = jsonString
        
    def parseToddleCfg(self):
        toddleCfg = json.loads(self._myJsonString)
        #print toddleCfg
        #print toddleCfg['actions']
        for mappedFunction in  toddleCfg['actions']:
            print "GPIO: %s, logicalButton: %s, js function: %s" % (mappedFunction['GPIO'], mappedFunction['logicalButton'], mappedFunction['invokeScript'])
        return toddleCfg

class MyApp(QtGui.QMainWindow):
    # create a member of the object to act as a signal
    dataReceived = QtCore.pyqtSignal(str)

    def _setBrowser(self, browser=None):
        self._browser = browser

    def _getBrowser(self):
        return self._browser

    browser = property(_getBrowser, _setBrowser)
    
    logicalActionMap = {}

    # this is the callback that runs from the GPIO thread
    def signalStyleCallback(self,data):
        print('callback: %s [%s]' % (data, threading.current_thread().name))
        self.dataReceived.emit(data)
        
    # this is the callback that is activated when the main
    # GUI thread is signalled by the emit statement above.
    def receive(self, data):
        print('received: %s [%s]' % (data, threading.current_thread().name))
        self.run_video() 
    
    # Interact with the HTML page by calling the completeAndReturnName
    # function; print its return value to the console
    def run_video(self):
        print ('Entered run_video')
        frame = self._getBrowser().page().mainFrame()
        print frame.evaluateJavaScript('playPause();')
    
    def pageLoadComplete(self):
        self.parseToddleJson()
        
    def setupMappings(self):
        GPIO.cleanup()
        for mappedFunction in self._currentCfg['actions']:
            # associate a channel with a javascript function to invoke in the callback
            self.logicalActionMap[mappedFunction['GPIO']] = mappedFunction['invokeScript']
            # need to also figure out how to associate the soft buttons here
            # setup the basic callback channel for the GPIO thread
            GPIO.add_event_detect(mappedFunction['GPIO'], GPIO.BOTH, callback=window.signalStyleCallback, bouncetime=100)
    
    def parseToddleJson(self):
        print "page load complete"
        elements = self.browser.page().mainFrame().findAllElements("#toddleConfig")
        #for index in range(elements.count()):
        #    print(elements.at(index).toPlainText())
        parser = toddleCfgParser(str(elements.at(0).toPlainText()))
        self._currentCfg = parser.parseToddleCfg()
        self.setupMappings()
    
    def setupLogicalButtonActions(self, toddleCfg):
        print "boof"
        
    def initializeGui(self):
        grid = QGridLayout()
        self._setBrowser(QWebView())
        url_input = UrlInput(self.browser)
        url_input.setText("file:/home/pi/rPiBrowserPrototype/testHtml5.html")
        requests_table = RequestsTable()
        #loadButton = QPushButton()
        #loadButton.setText("Load Video")
        #loadButton.clicked.connect(url_input._return_pressed)

        playButton = QPushButton()
        playButton.setText("Play Video")
        playButton.clicked.connect(self.run_video)

        # this stuff shouldn't be here - need to
        # move this to a functionally cohesive place 
        # in the code
        manager = Manager(requests_table)
        page = QWebPage()
        page.setNetworkAccessManager(manager)
        
        
        self.browser.setPage(page)
        self.browser.loadFinished.connect(self.pageLoadComplete)

        js_eval = JavaScriptEvaluator(page)
        action_box = ActionInputBox(page)

        #grid.addWidget(url_input, 1, 0)
        grid.addWidget(action_box, 2, 0)
        grid.addWidget(self.browser, 3, 0)
        grid.addWidget(requests_table, 4, 0)
        grid.addWidget(js_eval, 5, 0)
        #grid.addWidget(loadButton, 6,0)
        grid.addWidget(playButton, 6,0)

        main_frame = QWidget()
        main_frame.setLayout(grid)
        return main_frame

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        # this sets up the signal receive capability and
        # and associates the signal identifier with the
        # method to call.
        self.dataReceived.connect(self.receive)
        
        main_frame = self.initializeGui()
        self.setCentralWidget(main_frame)
        
        
    def closeEvent(self, event):
        print("event")
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Want to quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            if GPIO_AVAILABLE == 1:
                GPIO.cleanup()       # clean up GPIO on CTRL+C exit
            event.accept()
        else:
            event.ignore()

 
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    if (GPIO_AVAILABLE == 1):
        GPIO.cleanup()       # clean up GPIO on start
        # set numbering to the BCM scheme instead of physical pins
        GPIO.setmode(GPIO.BCM)
        # set the initial states for input and voltage
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # detect up and down edges on the pin with a bounce
        # window to avoid double triggers. Associate the
        # callback the GPIO thread runs.
        GPIO.add_event_detect(17, GPIO.BOTH, callback=window.signalStyleCallback, bouncetime=100)
    # start the GUI
    window.show()
    url = os.environ.get('TODDLE_CONTENT')
    #print os.environ
    #print url
    window.browser.load(QtCore.QUrl(url))
    sys.exit(app.exec_())
    print "exit"
