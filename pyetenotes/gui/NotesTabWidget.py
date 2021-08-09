import logging
from typing import Dict, List, Union

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal

from ..__version__ import __title__
from ..etesync import Note
from ..settings import Settings
from .NoteTabEntryWidget import NoteTabEntryWidget

logger = logging.getLogger("logger")
settings = Settings(__title__)


class NotesTabWidget(QtWidgets.QTabWidget):
    tab_closed = pyqtSignal(Note)

    def __init__(self, mainwindow: QtWidgets.QMainWindow):
        super(NotesTabWidget, self).__init__(mainwindow)
        self.setup_ui()
        self.mainwindow = mainwindow

    def setup_ui(self):
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(1)
        self.setSizePolicy(size_policy)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.link_callbacks()

    def open_tab(self, title: str, note: Note) -> int:
        if settings.value("notestabwidget/showcolors", type=bool) and note.notebook.color:
            pixmap = QtGui.QPixmap(20, 20)
            color = QtGui.QColor(note.notebook.color)
            pixmap.fill(QtGui.QColor(color.red(), color.green(), color.blue(), settings.value("notestreewidget/color/alpha", type=int)))
            return self.addTab(NoteTabEntryWidget(note, self.mainwindow), QtGui.QIcon(pixmap), title)
        else:
            return self.addTab(NoteTabEntryWidget(note, self.mainwindow), title)

    def select_tab(self, index: int):
        self.setCurrentIndex(index)

    def next_tab(self):
        if self.count():
            self.select_tab((self.currentIndex() + 1) % self.count())

    def previous_tab(self):
        if self.count():
            self.select_tab((self.currentIndex() - 1) % self.count())

    def opened_notes(self) -> List[Note]:
        return [self.widget(index).note for index in range(self.count())]

    def opened_note_widgets(self) -> List[NoteTabEntryWidget]:
        return [self.widget(index) for index in range(self.count())]

    def note_is_opened(self, note: Note) -> int:
        note_widget_opened = list(filter(lambda nw: nw.note.uid == note.uid, self.opened_note_widgets()))
        return self.indexOf(note_widget_opened[0]) if note_widget_opened else -1

    def close_tab(self, index):
        self.mainwindow.save_note()
        widget: NoteTabEntryWidget = self.widget(index)
        if widget is not None:
            self.tab_closed.emit(widget.note)
            widget.deleteLater()
        self.removeTab(index)

    def close_current_tab(self):
        self.close_tab(self.currentIndex())

    def close_all_tabs(self):
        while self.count():
            self.close_tab(0)

    def update_notes(self, notes: List[Note]):
        for note in notes:
            if (index := self.note_is_opened(note)) >= 0:
                widget: NoteTabEntryWidget = self.widget(index)

                if note.content == widget.note.content and note.name == widget.note.name:
                    continue
                elif not widget.note.changed:
                    widget.note_edit_widget.setText(note.content.decode())
                    logger.debug(f"NotesTabWidget.update_notes: note {widget.note.name} - {widget.note.uid} updated.")
                else:
                    note.changed = True

                widget.note = note
                self.setTabText(index, note.name)

    def tab_changed_callback(self, index):
        if index < 0:
            return
        current_note_widget: NoteTabEntryWidget = self.currentWidget()
        self.mainwindow.pb_save.setEnabled(current_note_widget.note.changed)
        self.mainwindow.actionSave.setEnabled(current_note_widget.note.changed)
        self.mainwindow.combo_view.setCurrentText(current_note_widget.view)

    def link_callbacks(self):
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self.tab_changed_callback)
