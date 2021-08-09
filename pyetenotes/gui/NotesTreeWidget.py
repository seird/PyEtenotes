import logging
import os
from enum import Enum
from typing import Iterator, List, Optional, Union
from PyQt5 import QtCore, QtGui, QtWidgets

from ..__version__ import __title__
from ..etesync import EtesyncNotes, Note, Notebook
from ..settings import Settings
from ..tasks import DeleteNotebookTask, DeleteNoteTask, ExportNoteTask, ExportNotesTask
from ..utils import get_clean_string
from .FilterNotesWidget import FilterNotesWidget


logger = logging.getLogger("logger")
settings = Settings(__title__)


class NoteContextAction(Enum):
    Nop = 0
    Delete = 1
    Export = 2


class NoteTreeWidgetItemContextMenu(QtWidgets.QMenu):
    def __init__(self):
        super(NoteTreeWidgetItemContextMenu, self).__init__()
        self.action_edit = self.addAction("Edit note")
        self.action_edit.setDisabled(True)
        self.action_export = self.addAction("Export note")
        self.action_delete = self.addAction("Delete note")


class NotebookTreeWidgetItemContextMenu(QtWidgets.QMenu):
    def __init__(self):
        super(NotebookTreeWidgetItemContextMenu, self).__init__()
        self.action_create_note = self.addAction("Create note")
        self.action_edit = self.addAction("Edit notebook")
        self.action_edit.setDisabled(True)
        self.action_export = self.addAction("Export notes")
        self.action_delete = self.addAction("Delete notebook")


class NotebookTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, notebook: Notebook, mainwindow: QtWidgets.QMainWindow):
        super(NotebookTreeWidgetItem, self).__init__([notebook.name])
        self.notebook = notebook
        self.mainwindow = mainwindow
        self.set_color(notebook.color)
        self.setSizeHint(0, QtCore.QSize(0, 25))
        self.setToolTip(0, notebook.collection.meta.get("description"))

    def set_color(self, color: str):
        if settings.value("notestreewidget/showcolors", type=bool) and color:
            color = QtGui.QColor(color)
            self.setBackground(0, QtGui.QColor(color.red(), color.green(), color.blue(), alpha=settings.value("notestreewidget/color/alpha", type=int)))

    def context_callback(self, pos: QtCore.QPoint) -> NoteContextAction:
        context_menu = NotebookTreeWidgetItemContextMenu()
        action = context_menu.exec_(pos)
        if action == context_menu.action_delete:
            response = QtWidgets.QMessageBox.warning(
                self.mainwindow,
                "Are you sure?",
                f"Delete notebook \"{self.notebook.name}\"?",
                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                defaultButton=QtWidgets.QMessageBox.Cancel
            )
            if response == QtWidgets.QMessageBox.Ok:
                return NoteContextAction.Delete
        elif action == context_menu.action_create_note:
            self.mainwindow.new_note_callback(self.notebook)
            return NoteContextAction.Nop
        elif action == context_menu.action_export:
            return NoteContextAction.Export
        else:
            return NoteContextAction.Nop


class NoteTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, note: Note, parent: NotebookTreeWidgetItem, mainwindow: QtWidgets.QMainWindow):
        super(NoteTreeWidgetItem, self).__init__([note.name])
        self.note = note
        self.parent = parent
        self.mainwindow = mainwindow
        self.setSizeHint(0, QtCore.QSize(0, 22))

    def context_callback(self, pos: QtCore.QPoint) -> NoteContextAction:
        context_menu = NoteTreeWidgetItemContextMenu()
        action = context_menu.exec_(pos)
        if action == context_menu.action_delete:
            response = QtWidgets.QMessageBox.warning(
                self.mainwindow,
                "Are you sure?",
                f"Delete note \"{self.note.name}\"?",
                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                defaultButton=QtWidgets.QMessageBox.Cancel
            )
            if response == QtWidgets.QMessageBox.Ok:
                return NoteContextAction.Delete
        elif action == context_menu.action_export:
            return NoteContextAction.Export

        return NoteContextAction.Nop


class NotesTreeWidget(QtWidgets.QWidget):
    def __init__(self, mainwindow: QtWidgets.QMainWindow):
        super(NotesTreeWidget, self).__init__(mainwindow)
        self.mainwindow = mainwindow
        self.api: EtesyncNotes = mainwindow.api
        self.notes_tree_widget = QtWidgets.QTreeWidget()
        self.filter_notes_widget = FilterNotesWidget()
        self.init_ui()

    def init_ui(self):
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.verticalLayout = QtWidgets.QVBoxLayout()

        self.verticalLayout.addWidget(self.filter_notes_widget)
        self.verticalLayout.addWidget(self.notes_tree_widget)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.gridLayout.setContentsMargins(1, 1, 1, 1)

        self.notes_tree_widget.setIndentation(10)
        self.notes_tree_widget.setColumnCount(1)
        self.notes_tree_widget.setHeaderHidden(True)
        self.notes_tree_widget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.notes_tree_widget.setAlternatingRowColors(False)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        self.notes_tree_widget.setSizePolicy(size_policy)
        self.notes_tree_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        # self.build_tree()

        self.link_callbacks()

    def toggle_filter(self):
        self.filter_notes_widget.toggle()

    def build_tree(self):
        for notebook in self.api.get_notebooks():
            self.notes_tree_widget.add_notebook(notebook)

    def restore(self, notebooks: List[Notebook], notes: List[Note]):
        for notebook in notebooks:
            twi_notebook = NotebookTreeWidgetItem(notebook, self.mainwindow)
            self.notes_tree_widget.addTopLevelItem(twi_notebook)
            twi_notebook.setExpanded(settings.value(f"notetreewidget/{notebook.uid}/expanded", True, type=bool))

        for note in notes:
            self.add_note(note, note.notebook)

    def add_notebook(self, notebook: Notebook):
        twi_notebook = NotebookTreeWidgetItem(notebook, self.mainwindow)
        for note in self.api.get_notes(notebook):
            twi_notebook.addChild(NoteTreeWidgetItem(note, twi_notebook, self.mainwindow))
        self.notes_tree_widget.addTopLevelItem(twi_notebook)
        twi_notebook.setExpanded(settings.value(f"notetreewidget/{notebook.uid}/expanded", True, type=bool))
        twi_notebook.sortChildren(0, QtCore.Qt.AscendingOrder)
        self.notes_tree_widget.sortItems(0, QtCore.Qt.AscendingOrder)

    def add_note(self, note: Note, notebook: Notebook):
        items: List[NotebookTreeWidgetItem] = self.notes_tree_widget.findItems(notebook.name, QtCore.Qt.MatchExactly, 0)
        if items:
            twi_notebook = items[0]
            twi_notebook.addChild(NoteTreeWidgetItem(note, twi_notebook, self.mainwindow))
            twi_notebook.sortChildren(0, QtCore.Qt.AscendingOrder)
        else:
            logger.error(f"NotesTreeWidget:add_note {notebook.name} not found when adding {note.name}.")

    def update_notebooks(self, notebooks: List[Notebook]):
        for notebook in notebooks:
            if notebook_tree_item := self.find_notebook_tree_item(notebook):
                notebook_tree_item.notebook = notebook
                notebook_tree_item.setText(0, notebook.name)
                notebook_tree_item.set_color(notebook.color)
                notebook_tree_item.setToolTip(0, notebook.collection.meta.get("description"))
                logger.debug(f"NotesTreeWidget.update_notebooks: updated {notebook.name} - {notebook.uid}")

    def update_notes(self, notes: List[Note]):
        for note in notes:
            if note_tree_item := self.find_note_tree_item(note):
                note_tree_item.note = note
                note_tree_item.setText(0, note.name)
                logger.debug(f"NotesTreeWidget.update_notes: updated {note.name} - {note.uid}")

    def find_notebooks(self) -> List[Notebook]:
        return [self.notes_tree_widget.topLevelItem(index).notebook for index in range(self.notes_tree_widget.topLevelItemCount())]

    def find_notebook(self, name: str) -> Notebook:
        items: List[NotebookTreeWidgetItem] = self.notes_tree_widget.findItems(name, QtCore.Qt.MatchExactly, 0)
        return items[0].notebook if items and isinstance(items[0], NotebookTreeWidgetItem) else None

    def find_notes(self) -> List[Note]:
        return [item.note for item in self.notes_tree_widget.findItems("*", QtCore.Qt.MatchWildcard | QtCore.Qt.MatchRecursive) if isinstance(item, NoteTreeWidgetItem)]

    def find_note_widget_items(self) -> Iterator[NoteTreeWidgetItem]:
        return filter(lambda item: isinstance(item, NoteTreeWidgetItem), self.notes_tree_widget.findItems("*", QtCore.Qt.MatchWildcard | QtCore.Qt.MatchRecursive))

    def find_notes_in_notebook(self, notebook: Notebook) -> List[Note]:
        return list(filter(lambda note: note.notebook.uid == notebook.uid, self.find_notes()))

    def find_notebook_tree_item(self, notebook: Notebook) -> Optional[NotebookTreeWidgetItem]:
        for index in range(self.notes_tree_widget.topLevelItemCount()):
            item: NotebookTreeWidgetItem = self.notes_tree_widget.topLevelItem(index)
            if item.notebook.uid == notebook.uid:
                return item
        return None

    def find_note_tree_item(self, note: Note) -> Optional[NoteTreeWidgetItem]:
        for item in self.notes_tree_widget.findItems("*", QtCore.Qt.MatchWildcard | QtCore.Qt.MatchRecursive):
            if isinstance(item, NoteTreeWidgetItem) and item.note.uid == note.uid:
                return item
        return None

    def item_clicked_callback(self, item: NoteTreeWidgetItem, column: int):
        if not isinstance(item, NoteTreeWidgetItem):
            return

        # Add an indicator when the note is opened in a tab
        pixmap = QtGui.QPixmap(7, 7)
        color = QtGui.QColor("lightblue")
        pixmap.fill(color)
        item.setIcon(0, QtGui.QIcon(pixmap))

        self.mainwindow.open_note(item.note.name, item.note)

    def close_note(self, note: Note):
        # Remove the "open" icon indicator
        for note_widget in self.find_note_widget_items():
            if note_widget.note.uid == note.uid:
                note_widget.setIcon(0, QtGui.QIcon())
                return

    def context_callback(self, pos: QtCore.QPoint):
        item: Union[NotebookTreeWidgetItem, NoteTreeWidgetItem, QtWidgets.QTreeWidgetItem] = self.notes_tree_widget.itemAt(pos)
        if item is None:
            return
        pos_mapped = self.notes_tree_widget.mapToGlobal(pos)
        action = item.context_callback(pos_mapped)

        if action == NoteContextAction.Nop:
            return
        elif action == NoteContextAction.Delete:
            if isinstance(item, NoteTreeWidgetItem):
                # Remove via the api
                self.delete_note_task = DeleteNoteTask(self.api, item.note)
                self.delete_note_task.start()

                # Remove settings
                settings.remove(f"notewidget/{item.note.notebook.uid}/{item.note.uid}/")

                # Check if the note is opened in a tab
                if (index := self.mainwindow.notes_tab_widget.note_is_opened(item.note)) is not None:
                    self.mainwindow.notes_tab_widget.close_tab(index)

                # Remove from the tree
                twi_notebook: NotebookTreeWidgetItem = item.parent
                twi_notebook.takeChild(twi_notebook.indexOfChild(item))

            elif isinstance(item, NotebookTreeWidgetItem):
                # Remove via the api
                self.delete_notebook_task = DeleteNotebookTask(self.api, item.notebook)
                self.delete_notebook_task.start()

                # Remove settings
                settings.remove(f"notewidget/{item.notebook.uid}/")

                # Check if its notes are opened in a tab
                ...

                # Remove from the tree
                if (index := self.notes_tree_widget.indexOfTopLevelItem(item)) is not None:
                    self.notes_tree_widget.takeTopLevelItem(index)
        elif action == NoteContextAction.Export:
            if isinstance(item, NoteTreeWidgetItem):
                fname = QtWidgets.QFileDialog.getSaveFileName(
                    self.mainwindow,
                    "Export",
                    os.path.join(settings.value("export/path", type=str), get_clean_string(item.note.name)),
                    "*.txt"
                )[0]

                if fname and os.path.exists(os.path.dirname(fname)):
                    settings.setValue("export/path", os.path.dirname(fname))
                    self.export_note_task = ExportNoteTask(item.note, fname)
                    self.export_note_task.started.connect(self.mainwindow.export_started)
                    self.export_note_task.finished.connect(self.mainwindow.export_finished)
                    self.export_note_task.failed.connect(self.mainwindow.export_failed)
                    self.export_note_task.start()
            elif isinstance(item, NotebookTreeWidgetItem):
                savedir = QtWidgets.QFileDialog.getExistingDirectory(self, "Export", settings.value("export/path", type=str))
                if savedir and os.path.exists(savedir):
                    notes = self.find_notes_in_notebook(item.notebook)
                    if not notes:
                        return
                    settings.setValue("export/path", savedir)
                    self.export_all_notes_task = ExportNotesTask(notes, savedir)
                    self.export_all_notes_task.started.connect(self.mainwindow.export_started)
                    self.export_all_notes_task.finished.connect(self.mainwindow.export_finished)
                    self.export_all_notes_task.failed.connect(self.mainwindow.export_failed)
                    self.export_all_notes_task.start()

    def filter_changed(self, text: str):
        # Hide note widget items for which text does not appear in the name
        for item in self.find_note_widget_items():
            item.setHidden(text.lower().strip() not in item.note.name.lower())

    def filter_hidden(self):
        # Make all note widget items visible again when the filter widget is hidden
        for item in self.find_note_widget_items():
            item.setHidden(False)

    def link_callbacks(self):
        self.notes_tree_widget.itemClicked.connect(self.item_clicked_callback)
        self.notes_tree_widget.customContextMenuRequested.connect(self.context_callback)
        self.notes_tree_widget.itemCollapsed.connect(lambda x: settings.setValue(f"notetreewidget/{x.notebook.uid}/expanded", 0))
        self.notes_tree_widget.itemExpanded.connect(lambda x: settings.setValue(f"notetreewidget/{x.notebook.uid}/expanded", 1))
        self.filter_notes_widget.textChanged.connect(self.filter_changed)
        self.filter_notes_widget.hidden.connect(self.filter_hidden)
