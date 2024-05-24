from time import sleep
from functools import partial
from pathlib import Path
import subprocess
import os

from qgis.core import (
    QgsTask, QgsMessageLog, Qgis
)

loginfo = partial(QgsMessageLog.logMessage, tag='EditPointCloudTask', level=Qgis.MessageLevel.Info)
logsucc = partial(QgsMessageLog.logMessage, tag='EditPointCloudTask', level=Qgis.MessageLevel.Success)
logcrit = partial(QgsMessageLog.logMessage, tag='EditPointCloudTask', level=Qgis.MessageLevel.Critical)
logwarn = partial(QgsMessageLog.logMessage, tag='EditPointCloudTask')

DUMMY_SLEEP_TIME_SEC = 15
EXT_PROC_WAIT_TIMEOUT_SEC = 60


class EditPointCloudTask(QgsTask):
    def __init__(self, description, point_cloud_editor, infile: Path, outfile: Path, args: dict):
        super().__init__(description, QgsTask.CanCancel)
        self.point_cloud_editor = point_cloud_editor
        self.infile = infile
        self.outfile = outfile
        self.args = args
        if 'crs' not in args:
            raise ValueError(f"'crs' not defined in args.")
        self.crs = args['crs'].split(':')[1]
        self.exception = None
        self.active_process = None
        self.vrpce = os.getenv('APPDATA') + '\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\point_cloud_editor\\VRPCE\\VRPCE.exe'

    def run(self):
        loginfo(f"Started task {self.description()}, infile: {self.infile}, outfile: {self.outfile}, crs: {self.crs}, VRPCE: {self.vrpce}")
        # Run the process...
        try:
            # TODO: Do the thing here, for now, just copy infile to outfile...
            self.active_process: subprocess.Popen = subprocess.Popen([self.vrpce, '-i', self.infile, '-o', self.outfile])
            running = True
        except Exception as e:
            self.exception = e
            return False
        # Check for process termination...
        return_code: subprocess.Popen.returncode = None
        while running:
            try:
                return_code: subprocess.Popen.returncode = self.active_process.wait(EXT_PROC_WAIT_TIMEOUT_SEC)
                if return_code is not None:
                    running = False
            except subprocess.TimeoutExpired:
                if self.isCanceled():
                    return False

        if return_code == 0:
            return True

        return False

    def finished(self, result):
        if result:
            logsucc(f"Task {self.description()} completed.")
            self.point_cloud_editor.reset_task()
            self.point_cloud_editor.add_result_layer(self.outfile)
        else:
            if self.exception is None:
                logwarn((f"Task {self.description()} not successful, but there was no exception, "
                         'so the task was probably killed by the user.'))
                self.point_cloud_editor.reset_task()
            else:
                logcrit(f"Task {self.description()} failed with exception: {self.exception}")
                self.point_cloud_editor.reset_task()
                raise self.exception

    def cancel(self):
        loginfo(f"Task {self.description()} was canceled.")
        super().cancel()
