from vad_logger import VAD_Logger
from transcriber import Transcriber
from screen_writer import write_to_screen
import sys
from PyQt5.QtWidgets import QApplication, QMenu, QAction, QSystemTrayIcon, QStyle

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

        self.tray_menu = QMenu()
        self.tray_menu.addAction(self.get_speech_action)
        self.tray_menu.addAction(self.quit_action)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tray_icon.setToolTip("Tasker")
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()

    def get_speech(self):
        response = self.mic.start_recording()
        transcription = self.transcriber.transcribe(response)
        transcription_words = transcription.split(" ")
        self.screen.write(transcription)

    def quit_app(self):
        self.tray_icon.hide()
        self.quit()

if __name__ == "__main__":
    app = Tasker(sys.argv)
    sys.exit(app.exec_())
