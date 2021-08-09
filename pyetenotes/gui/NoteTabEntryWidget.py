import logging

from PyQt5 import QtCore, QtGui, QtWidgets

from ..__version__ import __title__
from ..etesync import Note
from ..settings import Settings
from .designs.widget_note import Ui_Form as Ui_Form_NoteWidget
from .NoteEditWidget import NoteEditWidget
from .NotePreviewWidget import NotePreviewWidget


logger = logging.getLogger("logger")
settings = Settings(__title__)


class NoteTabEntryWidget(QtWidgets.QWidget, Ui_Form_NoteWidget):
    def __init__(self, note: Note, mainwindow: QtWidgets.QMainWindow):
        super(NoteTabEntryWidget, self).__init__()
        self.setupUi(self)
        self.mainwindow = mainwindow
        self.note = note
        self.note_edit_widget = NoteEditWidget(self.splitter)
        self.note_preview_widget = NotePreviewWidget(self.splitter)

        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        self.update_preview = True

        self.link_callbacks()

        self.note_edit_widget.setPlainText(self.note.content.decode())
        self.note.changed = False
        self.update_view(settings.value(f"noteentrywidget/{self.note.notebook.uid}/{self.note.uid}/view", "Live Preview", type=str))

        if splitter_state := settings.value(f"noteentrywidget/{self.note.notebook.uid}/{self.note.uid}/splitter", type=QtCore.QByteArray):
            self.splitter.restoreState(splitter_state)

    def update_view(self, view: str):
        self.view = view
        if view == "Live Preview":
            self.note_preview_widget.setMarkdown(self.note_edit_widget.toPlainText())
            self.update_preview = True
            self.note_edit_widget.setFocus()
            self.note_edit_widget.setVisible(True)
            self.note_preview_widget.setVisible(True)
        elif view == "Preview":
            self.note_preview_widget.setMarkdown(self.note_edit_widget.toPlainText())
            self.note_preview_widget.setFocus()
            self.note_edit_widget.setHidden(True)
            self.note_preview_widget.setVisible(True)
        elif view == "Edit":
            self.update_preview = False
            self.note_edit_widget.setFocus()
            self.note_edit_widget.setVisible(True)
            self.note_preview_widget.setHidden(True)
        settings.setValue(f"noteentrywidget/{self.note.notebook.uid}/{self.note.uid}/view", view)

    def note_edit_changed_callback(self):
        if self.update_preview:
            self.note_preview_widget.setMarkdown(self.note_edit_widget.toPlainText())
        self.note.changed = True
        self.mainwindow.pb_save.setEnabled(True)
        self.mainwindow.actionSave.setEnabled(True)

    def link_callbacks(self):
        self.note_edit_widget.textChanged.connect(self.note_edit_changed_callback)
        self.splitter.splitterMoved.connect(lambda _: settings.setValue(f"noteentrywidget/{self.note.notebook.uid}/{self.note.uid}/splitter", self.splitter.saveState()))
