# rPiBrowserPrototype

The "browser.py" file is a simple proof-of-concept cobbled together from a few online sources and trial & error.

The purpose here is to invoke a javascript method via a hardware button. In this example, I'm using GPIO 17 (BCM).

The example assumes there's a video "small.mp4" available in an HTML5 video tag.

# Sources:
* GPIO demo - 
* browser - https://pawelmhm.github.io/python/pyqt/qt/webkit/2015/09/08/browser.html
* callback handling with signals - https://stackoverflow.com/questions/39870577/pyqt-wake-main-thread-from-non-qthread?rq=1
* html5 video - https://www.w3schools.com/tags/tag_video.asp
* PyQt threading and code organization - https://nikolak.com/pyqt-threading-tutorial/

# GPIO button list
Assuming the GPIO buttons we will use will be limited to an initial number of 8, by convention, I recommend the following standard approach to button identification:
0. 17
1. 27
2. 22
3. 23
4. 24
5. 25
6. 16
7. 26

I've skipped buttons that might be used for other purposes besides standard GPIO, but since this is just a convention, it can be ignored.