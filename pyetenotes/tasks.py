import abc
import schedule
import logging
import os
import time

from typing import List
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal

from .__version__ import __title__
from .etesync import EtesyncNotes, Note, Notebook
from .settings import Settings
from .utils import get_clean_string


logger = logging.getLogger("logger")
settings = Settings(__title__)


class TasksThread(QtCore.QThread):
    new_updates_signal = pyqtSignal(dict)

    def __init__(self, api: EtesyncNotes):
        super(TasksThread, self).__init__()
        self.running = False
        self.api = api
        self.interval = settings.value("tasks/interval", type=int)
        self.set_schedule()

    def set_schedule(self):
        schedule.clear("update_notebooks")
        # set a large interval such that the task is ran once at the start (schedule.ran_all())
        schedule.every(settings.value("tasks/update_notebooks/interval", type=int) or 5256000).minutes.do(self.update_notebooks).tag("update_notebooks")

    def run(self):
        self.running = True
        try:
            schedule.run_all()
            while self.running:
                time.sleep(self.interval)
                schedule.run_pending()
        except Exception as e:
            logger.error(f"TasksThread: {e}")
        finally:
            self.running = False

    def update_notebooks(self):
        updates = {
            "notebooks": self.api.get_notebooks(changes=True),
            "notes": []
        }

        if updates["notebooks"]:
            for notebook in updates["notebooks"]:
                updates["notes"] += self.api.get_notes(notebook, changes=True)

        if updates["notebooks"] or updates["notes"]:
            self.new_updates_signal.emit(updates)


class BaseTask(QtCore.QThread):
    failed = pyqtSignal()

    def __init__(self):
        super(BaseTask, self).__init__()
        self.running = False

    @abc.abstractmethod
    def task(self):
        ...

    def run(self):
        self.running = True
        try:
            self.task()
        except Exception as e:
            logger.error(f"{self.__class__.__name__} failed: {e}")
            self.failed.emit()
        finally:
            self.running = False


class SaveNotesTask(BaseTask):
    def __init__(self, api: EtesyncNotes, notes: List[Note]):
        super(SaveNotesTask, self).__init__()
        self.api = api
        self.notes = notes

    def task(self):
        self.api.save_notes(self.notes)


class CreateNotebookTask(BaseTask):
    created = pyqtSignal(Notebook)

    def __init__(self, api: EtesyncNotes, name: str, description: str, color: str):
        super(CreateNotebookTask, self).__init__()
        self.api = api
        self.name = name
        self.description = description
        self.color = color

    def task(self):
        notebook = self.api.create_notebook(self.name, self.description, self.color)
        self.created.emit(notebook)


class CreateNoteTask(BaseTask):
    created = pyqtSignal(Note)

    def __init__(self, api: EtesyncNotes, name: str, notebook: Notebook):
        super(CreateNoteTask, self).__init__()
        self.api = api
        self.name = name
        self.notebook = notebook

    def task(self):
        note = self.api.create_note(self.name, self.notebook)
        self.created.emit(note)


class DeleteNoteTask(BaseTask):
    deleted = pyqtSignal(Note)

    def __init__(self, api: EtesyncNotes, note: Note):
        super(DeleteNoteTask, self).__init__()
        self.api = api
        self.note = note

    def task(self):
        self.api.remove_note(self.note)
        self.deleted.emit(self.note)


class DeleteNotebookTask(BaseTask):
    deleted = pyqtSignal(Notebook)

    def __init__(self, api: EtesyncNotes, notebook: Notebook):
        super(DeleteNotebookTask, self).__init__()
        self.api = api
        self.notebook = notebook

    def task(self):
        self.api.remove_notebook(self.notebook)
        self.deleted.emit(self.notebook)


class ExportNotesTask(BaseTask):
    def __init__(self, notes: List[Note], savedir: str = ""):
        super(ExportNotesTask, self).__init__()
        self.notes = notes
        self.savedir = savedir

    def task(self):
        for note in self.notes:
            savename = get_clean_string(note.name) + ".txt"
            savepath = os.path.join(self.savedir, savename)
            with open(savepath, "wb") as f:
                f.write(note.content)


class ExportNoteTask(BaseTask):
    def __init__(self, note: Note, savename: str):
        super(ExportNoteTask, self).__init__()
        self.note = note
        self.savename = savename

    def task(self):
        with open(self.savename, "wb") as f:
            f.write(self.note.content)
