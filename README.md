# rPiBrowserPrototype

# The "browser.py" file is a simple proof-of-concept cobbled 
# together from a few online sources and trial & error.

# The purpose here is to invoke a javascript method via a
# hardware button. In this example, I'm using GPIO 17 (BCM).

# The example assumes there's a video "small.mp4" available
# in an HTML5 video tag.

# Sources:
# RPIO demo - https://learn.sparkfun.com/tutorials/raspberry-gpio
# browser - https://pawelmhm.github.io/python/pyqt/qt/webkit/2015/09/08/browser.html
# callback handling with signals - https://stackoverflow.com/questions/39870577/pyqt-wake-main-thread-from-non-qthread?rq=1
