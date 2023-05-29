import typing, time
from vad_logger import VAD_Logger
from transcriber import Transcriber
from screen_writer import write_to_screen
import sys
from PyQt5.QtWidgets import QApplication, QMenu, QAction, QSystemTrayIcon, QStyle
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QObject, QThread, pyqtSignal

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class Worker(QObject):
    finished = pyqtSignal(str)
    def __init__(self, transcriber, mic):
        super(Worker, self).__init__()
        self.transcriber = transcriber
        self.mic = mic
        self.running = True
        self.quit = False

    # TODO Fix janky solution. Need to quit mic.start_recording() somehow through signal
    def run(self):
        # TODO: Fixed by sending signal through begin_recording()
        if self.running:
            logger.debug('Worker running')
            response = self.mic.start_recording()
            if self.quit == False:
                transcription = self.transcriber.transcribe(response)
                # TODO This needs to be controlled by transcriber_callback
                self.running = False
                self.finished.emit(transcription)
            self.run()
        else:
            # TODO Remove this else statenment. transcriber_callback should emit and run this function again
            logger.debug('Worker sleeping')
            time.sleep(.5)
            if self.quit == False:
                self.run()
            else:
                logger.debug('Worker quit')

class Tasker(QApplication):
    def __init__(self, sys_argv):
        super(Tasker, self).__init__(sys_argv)
        self.mic = VAD_Logger()
        self.transcriber = Transcriber()
        self.screen = write_to_screen('', False, True)

        self.get_speech_action = QAction("Get Speech", self)
        self.get_speech_action.triggered.connect(self.get_speech)
        
        self.quit_action = QAction("Quit", self)
        self.quit_action.triggered.connect(self.quit_app)
        
        self.checkbox_action = QAction('Enabled', self)
        self.checkbox_action.setCheckable(True)
        self.checkbox_action.triggered.connect(self.toggle_checkbox)

        self.tray_menu = QMenu()
        self.tray_menu.addAction(self.checkbox_action)
        self.tray_menu.addAction(self.get_speech_action)
        self.tray_menu.addAction(self.quit_action)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tray_icon.setToolTip("Tasker")
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        
        self.thread = None
        self.worker = None

    def transcriber_callback(self, transcription):
        self.screen.clear()
        self.screen.write(transcription, 5)
        # TODO This shouldn't be necessary. One shot needs self.work declared.
        if self.worker:
            self.worker.running = True
        
    def get_speech(self):
        response = self.mic.start_recording()
        transcription = self.transcriber.transcribe(response)
        self.transcriber_callback(transcription)
        
    def toggle_checkbox(self):
        checked = self.checkbox_action.isChecked()
        # Perform actions based on checkbox state
        if checked:
            self.thread = QThread()
            self.worker = Worker(self.transcriber, self.mic)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.transcriber_callback)
            # self.worker.finished.connect(self.worker.deleteLater)
            # self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()
        else:
            if self.thread:
                self.worker.running = False
                self.worker.quit = True
                self.thread.quit()

    def quit_app(self):
        self.tray_icon.hide()
        self.quit()
        
if __name__ == "__main__":
    app = Tasker(sys.argv)
    sys.exit(app.exec_())
