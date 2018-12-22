from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from functools import partial
import webbrowser
import sys
import psutil
from time import sleep
from datetime import datetime
import ctypes
import os


class SolveThread(QThread):
    process_status = pyqtSignal(str)
    process_kill_log = pyqtSignal(str)

    def __init__(self):
        QThread.__init__(self)
        self.start_status = False

    def __del__(self):
        self.wait()

    def run(self):
        while self.start_status:
            process = filter(lambda p: p.name() == "audiodg.exe", psutil.process_iter())
            for proc in process:
                while self.start_status:
                    try:
                        ps = psutil.Process(proc.pid)
                        process_percent = round(ps.cpu_percent(interval=1) / psutil.cpu_count(), 2)
                        status = "Name: " + proc.name() + "  " + "PID: " + str(proc.pid) + "  " + "CPU: " + str(process_percent) + "  " "Time: " + str(datetime.now())
                        self.process_status.emit(status)
                        if process_percent > 8:
                            try:
                                os.system("taskkill /f /pid %i" %proc.pid)
                                kill_log = "audiodg.exe is killed"
                                self.process_kill_log.emit(kill_log)
                            except Exception as ex:
                                error_log = "you should run this program as administrator"
                                self.process_kill_log.emit(error_log)
                            break
                        sleep(3)
                    except Exception:
                        break
            sleep(3)


form_class = uic.loadUiType("audiodg.ui")[0]


class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Audiogdg Solver")
        self.start_status = False
        self.confirm_administrator()

        self.github_url = "https://github.com/lumyjuwon/audiodgsolver"

        self.solve_thread = SolveThread()
        self.solve_thread.process_status.connect(self.add_status_to_listview)
        self.solve_thread.process_kill_log.connect(self.add_status_to_listview)

        self.solverButton.clicked.connect(self.start_solve)
        self.actionGithub.triggered.connect(partial(self.open_url, self.github_url))

    def confirm_administrator(self):
        if ctypes.windll.shell32.IsUserAnAdmin():
            self.add_status_to_listview('관리자 권한으로 실행된 프로세스입니다.')
        else:
            self.add_status_to_listview('일반 권한으로 실행된 프로세스입니다. 관리자 권한으로 실행하시기 바랍니다.')

    def start_solve(self):
        if not self.start_status:
            self.solverButton.setText("Stop Solver")
            self.start_status = True
            self.add_status_to_listview("Audiodg Solver is started")
            self.solve_thread.start_status = self.start_status
            self.solve_thread.start()
        else:
            self.solverButton.setText("Start Solver")
            self.start_status = False
            self.add_status_to_listview("Audiodg Solver is stopped")
            self.solve_thread.start_status = self.start_status
            self.solve_thread.quit()

    def add_status_to_listview(self, arg):
        self.logList.addItem(arg)
        self.logList.scrollToBottom()

    def open_url(self, url):
        webbrowser.open(url)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec_())
