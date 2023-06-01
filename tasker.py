import typing, time
from vad_logger import VAD_Logger # type: ignore
from transcriber import Transcriber
from screen_writer import write_to_screen
import sys
from PyQt5.QtWidgets import QApplication, QMenu, QAction, QSystemTrayIcon
from PyQt5.QtGui import QIcon

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
    def __init__(self, transcriber, mic, checkbox_action):
        super(Worker, self).__init__()
        self.checkbox_action = checkbox_action
        self.transcriber = transcriber
        self.mic = mic

    def run(self):
        while True:
            response = self.mic.start_recording()
            if response:
                transcription = self.transcriber.transcribe(response)
                self.finished.emit(transcription)
                if not self.checkbox_action.isChecked():
                    break
            else:
                break
                

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
        # self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tray_icon.setIcon(QIcon('tasker_systray.png'))
        self.tray_icon.setToolTip("Tasker")
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        
        # TODO This shouldn't be necessary. isRunning() called before first thread
        self.thread = QThread()
        self.worker = None

    def transcriber_callback(self, transcription):
        self.screen.clear()
        self.screen.write(transcription, 5)
        
    def get_speech(self):
        self.start_worker()
        
    def start_worker(self):
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        self.mic.stop_condition = False
        self.thread = QThread()
        self.worker = Worker(self.transcriber, self.mic, self.checkbox_action)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.transcriber_callback)
        # self.worker.finished.connect(self.worker.deleteLater)
        # self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        
    def stop_worker(self):
        self.mic.stop_condition = True
        self.thread.quit()
        self.thread.wait()
           
    def toggle_checkbox(self):
        checked = self.checkbox_action.isChecked()
        # Perform actions based on checkbox state
        if checked:
            self.get_speech_action.setEnabled(False)
            self.start_worker()
        else:
            self.get_speech_action.setEnabled(True)
            if self.thread:
                self.stop_worker()

    def quit_app(self):
        self.tray_icon.hide()
        self.quit()
        
if __name__ == "__main__":
    app = Tasker(sys.argv)
    sys.exit(app.exec_())
