import getpass
import logging
import os
import sys
import tempfile
from typing import Dict, List, Union

from PyQt5 import QtCore, QtGui, QtWidgets

from ..__version__ import __title__
from ..etesync import EtesyncNotes, Note, Notebook
from ..settings import Settings
from ..tasks import CreateNotebookTask, CreateNoteTask, ExportNoteTask, ExportNotesTask, SaveNotesTask, TasksThread
from .themes import set_theme
from ..utils import get_clean_string
from .designs.mainwindow import Ui_MainWindow
from .AuthenticationDialog import AuthenticationDialog
from .ShortcutDialog import ShortcutsDialog
from .NewNotebookDialog import NewNotebookDialog
from .NewNoteDialog import NewNoteDialog
from .NotesTabWidget import NotesTabWidget
from .NotesTreeWidget import NotesTreeWidget
from .NoteTabEntryWidget import NoteTabEntryWidget

logger = logging.getLogger("logger")
settings = Settings(__title__)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow, QtCore.QCoreApplication):
    def __init__(self, app: QtWidgets.QApplication, api: EtesyncNotes):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.app = app
        self.api = api

    def init_ui(self):
        self.setWindowTitle(__title__)
        self.app.setWindowIcon(QtGui.QIcon("logo.ico"))
        self.statusbar.hide()
        self.pb_save.setDisabled(True)
        self.actionSave.setDisabled(True)
        self.set_size_button_sizes()

        # Themes
        self.actionGroupTheme = QtWidgets.QActionGroup(self.menuTheme)
        self.actionGroupTheme.setExclusive(True)
        current_theme: str = settings.value("style", type=str)
        set_theme(self.app, current_theme)
        for name in ["Default", "Dark Green", "Light Green"]:
            action = QtWidgets.QAction(name, self.menuTheme, checkable=True)
            if current_theme == name.lower().replace(" ", ""):
                action.setChecked(True)
            self.actionGroupTheme.addAction(action)
            self.menuTheme.addAction(action)

        # Task update_notebooks
        self.actionGroupFetchChanges = QtWidgets.QActionGroup(self.menuFetchChanges)
        self.actionGroupFetchChanges.setExclusive(True)
        current_interval = settings.value("tasks/update_notebooks/interval", type=int)
        for interval in [0, 1, 5, 10, 30, 60]:
            action = QtWidgets.QAction(str(interval) + " minutes" if interval > 0 else "Disabled", self.menuFetchChanges, checkable=True)
            action.interval = interval
            if interval == current_interval:
                action.setChecked(True)
            self.actionGroupFetchChanges.addAction(action)
            self.menuFetchChanges.addAction(action)

        self.notes_tree_widget = NotesTreeWidget(self)
        self.notes_tab_widget = NotesTabWidget(self)
        self.splitter_tree.insertWidget(0, self.notes_tree_widget)
        self.splitter_tree.insertWidget(1, self.notes_tab_widget)

        self.cache_load()
        
        self.tasks_thread = TasksThread(self.api)

        self.restore_window_state()
        self.init_shortcuts()
        self.update_shortcuts()
        self.link_callbacks()
        self.tasks_thread.start()

    def set_size_button_sizes(self):
        self.pb_save.setFixedHeight(30)
        self.pb_save_all.setFixedHeight(30)
        self.pb_new_note.setFixedHeight(30)
        self.pb_new_notebook.setFixedHeight(30)
        self.combo_view.setFixedHeight(30)

    def cache_load(self):
        notebooks, notes = self.api.cache_load()
        self.notes_tree_widget.restore(notebooks, notes)

    def cache_save(self):
        self.api.cache_save(self.notes_tree_widget.find_notebooks(), self.notes_tree_widget.find_notes())

    def open_note(self, title: str, note: Note):
        if (index := self.notes_tab_widget.note_is_opened(note)) < 0:
            index = self.notes_tab_widget.open_tab(title, note)
        self.notes_tab_widget.select_tab(index)

    def save_notes(self) -> bool:
        notes = []
        for note_widget in self.notes_tab_widget.opened_note_widgets():
            note = note_widget.note
            if not note.changed:
                continue
            note.content = note_widget.note_edit_widget.toPlainText().encode()
            notes.append(note)

        if not notes:
            return False

        self.save_all_notes_task = SaveNotesTask(api=self.api, notes=notes)
        self.save_all_notes_task.started.connect(self.save_started)
        self.save_all_notes_task.finished.connect(self.save_finished)
        self.save_all_notes_task.failed.connect(self.save_failed)
        self.save_all_notes_task.start()
        return True

    def save_note(self):
        # Save the currently displayed note
        note_widget: NoteTabEntryWidget = self.notes_tab_widget.currentWidget()
        if not note_widget:
            return
        if not note_widget.note.changed:
            return
        note = note_widget.note
        note.content = note_widget.note_edit_widget.toPlainText().encode()

        self.save_note_task = SaveNotesTask(api=self.api, notes=[note])
        self.save_note_task.started.connect(self.save_started)
        self.save_note_task.finished.connect(self.save_finished)
        self.save_note_task.failed.connect(self.save_failed)
        self.save_note_task.start()

    def save_started(self):
        self.pb_save.setDisabled(True)
        self.pb_save_all.setDisabled(True)
        self.actionSave.setDisabled(True)
        self.actionSave_All.setDisabled(True)
        self.statusbar.showMessage("Saving...")

    def save_finished(self):
        self.pb_save_all.setEnabled(True)
        self.actionSave_All.setEnabled(True)
        self.statusbar.showMessage("Saved.", 5000)

    def save_failed(self):
        self.pb_save_all.setEnabled(True)
        self.actionSave_All.setEnabled(True)
        self.statusbar.showMessage("Save failed.", 5000)

    def export_notes(self) -> bool:
        notes = self.notes_tree_widget.find_notes()
        if not notes:
            return False

        savedir = QtWidgets.QFileDialog.getExistingDirectory(self, "Export", settings.value("export/path", type=str))
        if savedir and os.path.exists(savedir):
            settings.setValue("export/path", savedir)
            self.export_all_notes_task = ExportNotesTask(notes, savedir)
            self.export_all_notes_task.started.connect(self.export_started)
            self.export_all_notes_task.finished.connect(self.export_finished)
            self.export_all_notes_task.failed.connect(self.export_failed)
            self.export_all_notes_task.start()
            return True
        else:
            return False

    def export_note(self):
        # Export the currently displayed note
        note_widget: NoteTabEntryWidget = self.notes_tab_widget.currentWidget()
        if not note_widget:
            return
        note = note_widget.note

        fname = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Export",
            os.path.join(settings.value("export/path", type=str), get_clean_string(note.name)),
            "*.txt"
        )[0]

        if fname and os.path.exists(os.path.dirname(fname)):
            settings.setValue("export/path", os.path.dirname(fname))
            self.export_note_task = ExportNoteTask(note, fname)
            self.export_note_task.started.connect(self.export_started)
            self.export_note_task.finished.connect(self.export_finished)
            self.export_note_task.failed.connect(self.export_failed)
            self.export_note_task.start()

    def export_started(self):
        self.actionExport_All.setDisabled(True)
        self.actionExport.setDisabled(True)
        self.statusbar.showMessage("Exporting...")

    def export_finished(self):
        self.actionExport_All.setEnabled(True)
        self.actionExport.setEnabled(True)
        self.statusbar.showMessage("Export finished.", 5000)

    def export_failed(self):
        self.actionExport_All.setEnabled(True)
        self.actionExport.setEnabled(True)
        self.statusbar.showMessage("Export failed.", 5000)

    def new_note_callback(self, selected_notebook: Notebook = None):
        dialog = NewNoteDialog(self, self.notes_tree_widget.find_notebooks(), selected_notebook)
        accepted = dialog.exec_()
        if accepted and dialog.line_name.text() and dialog.combo_notebooks.currentText():
            notebook = self.notes_tree_widget.find_notebook(dialog.combo_notebooks.currentText())
            self.create_note_task = CreateNoteTask(self.api, dialog.line_name.text(), notebook)
            self.create_note_task.created.connect(self.note_created_callback)
            self.create_note_task.start()

    def note_created_callback(self, note: Note):
        self.notes_tree_widget.add_note(note, note.notebook)
        index = self.notes_tab_widget.open_tab(note.name, note)
        self.notes_tab_widget.select_tab(index)

    def new_notebook_callback(self):
        dialog = NewNotebookDialog(self)
        accepted = dialog.exec_()
        if accepted and dialog.line_name.text():
            self.create_notebook_task = CreateNotebookTask(
                self.api,
                dialog.line_name.text(),
                dialog.line_description.text(),
                dialog.color_name
            )
            self.create_notebook_task.created.connect(lambda notebook: self.notes_tree_widget.add_notebook(notebook))
            self.create_notebook_task.start()

    def view_currentTextChanged_callback(self, text: str):
        current_note_widget: NoteTabEntryWidget = self.notes_tab_widget.currentWidget()
        if current_note_widget:
            current_note_widget.update_view(text)

    def change_edit_font_callback(self):
        font = settings.value("notewidget/font/edit", type=QtGui.QFont)
        font, accepted = QtWidgets.QFontDialog.getFont(font, self, "Select Note Editor font")

        if not accepted:
            return

        settings.setValue("notewidget/font/edit", font)
        for opened_note_widget in self.notes_tab_widget.opened_note_widgets():
            opened_note_widget.note_edit_widget.set_font(font)

    def change_preview_font_callback(self):
        font = settings.value("notewidget/font/preview", type=QtGui.QFont)
        font, accepted = QtWidgets.QFontDialog.getFont(font, self, "Select Note Preview font")

        if not accepted:
            return

        settings.setValue("notewidget/font/preview", font)
        for opened_note_widget in self.notes_tab_widget.opened_note_widgets():
            opened_note_widget.note_preview_widget.set_font(font)

    def theme_selected_callback(self, action: QtWidgets.QAction):
        theme = action.text().lower().replace(" ", "")
        set_theme(self.app, theme)
        settings.setValue("style", theme)

    def fetch_changes_selected_callback(self, action: QtWidgets.QAction):
        settings.setValue("tasks/update_notebooks/interval", action.interval)
        self.tasks_thread.set_schedule()

    def shortcuts_callback(self):
        dialog = ShortcutsDialog(self)
        dialog.exec_()
        self.update_shortcuts()

    def new_updates_signal_callback(self, updates: Dict[str, Union[List[Notebook], List[Note]]]):
        for notebook in updates['notebooks']:
            if list(filter(lambda nb: nb.uid == notebook.uid, self.notes_tree_widget.find_notebooks())):
                # update an existing notebook
                self.notes_tree_widget.update_notebooks([notebook])
                logger.debug(f"tasks_updated_notes_callback: Updated notebook \"{notebook.name}\".")
            else:
                # New notebook
                self.notes_tree_widget.add_notebook(notebook)
                logger.debug(f"tasks_updated_notes_callback: Added new notebook \"{notebook.name}\".")

        for note in updates['notes']:
            if list(filter(lambda n: n.uid == note.uid, self.notes_tree_widget.find_notes())):
                # update an existing note
                self.notes_tree_widget.update_notes([note])
                self.notes_tab_widget.update_notes([note])
                logger.debug(f"tasks_updated_notes_callback: Updated note \"{note.name}\" in notebook \"{note.notebook.name}\".")
            else:
                # New note
                self.notes_tree_widget.add_note(note, note.notebook)
                logger.debug(f"tasks_updated_notes_callback: Added new note \"{note.name}\" to notebook \"{note.notebook.name}\".")

    def logout(self):
        response = QtWidgets.QMessageBox.warning(
            self,
            "Are you sure?",
            "Log out?",
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
            defaultButton=QtWidgets.QMessageBox.Cancel
        )
        if response == QtWidgets.QMessageBox.Ok:
            self.api.logout()
            self.close()

    def init_shortcuts(self):
        self.shortcut_new_note = QtWidgets.QShortcut(self)
        self.shortcut_new_notebook = QtWidgets.QShortcut(self)
        self.shortcut_save = QtWidgets.QShortcut(self)
        self.shortcut_save_all = QtWidgets.QShortcut(self)
        self.shortcut_close = QtWidgets.QShortcut(self)
        self.shortcut_close_all = QtWidgets.QShortcut(self)
        self.shortcut_quit = QtWidgets.QShortcut(self)
        self.shortcut_view_preview = QtWidgets.QShortcut(self)
        self.shortcut_view_live_preview = QtWidgets.QShortcut(self)
        self.shortcut_view_edit = QtWidgets.QShortcut(self)
        self.shortcut_close_tab = QtWidgets.QShortcut(self)
        self.shortcut_next_tab = QtWidgets.QShortcut(self)
        self.shortcut_previous_tab = QtWidgets.QShortcut(self)
        self.shortcut_toggle_filter = QtWidgets.QShortcut(self)

    def update_shortcuts(self):
        self.shortcut_new_note.setKey(QtGui.QKeySequence.fromString(settings.value("shortcuts/new_note", type=str)))
        self.shortcut_new_notebook.setKey(QtGui.QKeySequence.fromString(settings.value("shortcuts/new_notebook", type=str)))
        self.shortcut_save.setKey(QtGui.QKeySequence.fromString(settings.value("shortcuts/save", type=str)))
        self.shortcut_save_all.setKey(QtGui.QKeySequence.fromString(settings.value("shortcuts/save_all", type=str)))
        self.shortcut_close.setKey(QtGui.QKeySequence.fromString(settings.value("shortcuts/close", type=str)))
        self.shortcut_close_all.setKey(QtGui.QKeySequence.fromString(settings.value("shortcuts/close_all", type=str)))
        self.shortcut_quit.setKey(QtGui.QKeySequence.fromString(settings.value("shortcuts/quit", type=str)))
        self.shortcut_view_preview.setKey(QtGui.QKeySequence.fromString(settings.value("shortcuts/preview", type=str)))
        self.shortcut_view_live_preview.setKey(QtGui.QKeySequence.fromString(settings.value("shortcuts/live_preview", type=str)))
        self.shortcut_view_edit.setKey(QtGui.QKeySequence.fromString(settings.value("shortcuts/edit", type=str)))
        self.shortcut_close_tab.setKey(QtGui.QKeySequence.fromString(settings.value("shortcuts/close_tab", type=str)))
        self.shortcut_next_tab.setKey(QtGui.QKeySequence.fromString(settings.value("shortcuts/next_tab", type=str)))
        self.shortcut_previous_tab.setKey(QtGui.QKeySequence.fromString(settings.value("shortcuts/previous_tab", type=str)))
        self.shortcut_toggle_filter.setKey(QtGui.QKeySequence.fromString(settings.value("shortcuts/toggle_filter", type=str)))

    def link_callbacks(self):
        self.pb_save.clicked.connect(self.save_note)
        self.pb_save_all.clicked.connect(self.save_notes)
        self.pb_new_note.clicked.connect(self.new_note_callback)
        self.pb_new_notebook.clicked.connect(self.new_notebook_callback)

        self.combo_view.currentTextChanged.connect(self.view_currentTextChanged_callback)

        self.actionNew_note.triggered.connect(self.new_note_callback)
        self.actionNew_notebook.triggered.connect(self.new_notebook_callback)
        self.actionSave.triggered.connect(self.save_note)
        self.actionSave_All.triggered.connect(self.save_notes)
        self.actionClose.triggered.connect(self.notes_tab_widget.close_current_tab)
        self.actionClose_All.triggered.connect(self.notes_tab_widget.close_all_tabs)
        self.actionExport.triggered.connect(self.export_note)
        self.actionExport_All.triggered.connect(self.export_notes)
        self.actionLogout.triggered.connect(self.logout)
        self.actionQuit.triggered.connect(self.close)
        self.actionChange_edit_font.triggered.connect(self.change_edit_font_callback)
        self.actionChange_preview_font.triggered.connect(self.change_preview_font_callback)
        self.actionShortcuts.triggered.connect(self.shortcuts_callback)
        self.actionGroupTheme.triggered.connect(self.theme_selected_callback)
        self.actionGroupFetchChanges.triggered.connect(self.fetch_changes_selected_callback)

        self.tasks_thread.new_updates_signal[dict].connect(self.new_updates_signal_callback)

        self.shortcut_new_note.activated.connect(self.new_note_callback)
        self.shortcut_new_notebook.activated.connect(self.new_notebook_callback)
        self.shortcut_save.activated.connect(self.save_note)
        self.shortcut_save_all.activated.connect(self.save_notes)
        self.shortcut_quit.activated.connect(self.close)
        self.shortcut_view_preview.activated.connect(lambda: self.combo_view.setCurrentText("Preview"))
        self.shortcut_view_live_preview.activated.connect(lambda: self.combo_view.setCurrentText("Live Preview"))
        self.shortcut_view_edit.activated.connect(lambda: self.combo_view.setCurrentText("Edit"))
        self.shortcut_close_tab.activated.connect(self.notes_tab_widget.close_current_tab)
        self.shortcut_next_tab.activated.connect(self.notes_tab_widget.next_tab)
        self.shortcut_previous_tab.activated.connect(self.notes_tab_widget.previous_tab)
        self.shortcut_toggle_filter.activated.connect(self.notes_tree_widget.toggle_filter)

        self.notes_tab_widget.tab_closed.connect(self.notes_tree_widget.close_note)

    def acquire_lock(self) -> bool:
        temp_dir = tempfile.gettempdir()
        lock_filename = os.path.join(temp_dir, __title__ + "-" + getpass.getuser() + ".lock")
        self.lock_file = QtCore.QLockFile(lock_filename)
        self.lock_file.setStaleLockTime(0)
        return self.lock_file.tryLock()

    def restore_window_state(self):
        window_geometry = settings.value("mainwindow/geometry", type=QtCore.QByteArray)
        window_state = settings.value("mainwindow/state", type=QtCore.QByteArray)
        splitter_tree = settings.value("mainwindow/splitter_tree", type=QtCore.QByteArray)

        if window_geometry:
            self.restoreGeometry(window_geometry)
        if window_state:
            self.restoreState(window_state)
        if splitter_tree:
            self.splitter_tree.restoreState(splitter_tree)

    def save_window_state(self):
        settings.setValue("mainwindow/geometry", self.saveGeometry())
        settings.setValue("mainwindow/state", self.saveState())
        settings.setValue("mainwindow/splitter_tree", self.splitter_tree.saveState())

    def handle_close(self):
        save_started = self.save_notes()
        self.cache_save()
        self.save_window_state()
        self.lock_file.unlock()
        if save_started:
            self.save_all_notes_task.wait()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.handle_close()
        event.accept()
        self.quit()


def authenticate(api: EtesyncNotes) -> bool:
    # Check for a stored session
    encryption_key = settings.value("session/key", type=bytes)
    stored_session = settings.value("session/sessiondata", type=str)
    server_url = settings.value("session/url", type=str)
    if encryption_key and stored_session and server_url:
        api.restore_session(encryption_key, stored_session, server_url)
        logger.debug("Restored previous session.")
        return True

    # No stored session available
    username = None
    password = None
    stay_logged_in = True

    while not api.authenticated:
        dialog = AuthenticationDialog(username, password, server_url, stay_logged_in)
        accepted = dialog.exec_()
        if not accepted:
            logger.debug("Authentication: cancelled.")
            break

        username = dialog.line_username.text()
        password = dialog.line_password.text()
        server_url = dialog.line_url.text()
        stay_logged_in = dialog.cb_stay_logged_in.isChecked()

        if not username or not password:
            logger.debug("Authentication: missing user inputs.")
            continue

        api.authenticate(username, password, server_url, stay_logged_in)

    return api.authenticated


def start_gui():
    api = EtesyncNotes()
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    window = MainWindow(app, api)

    logdir = QtCore.QStandardPaths.standardLocations(QtCore.QStandardPaths.DataLocation)[0]
    if not os.path.exists(logdir):
        os.mkdir(logdir)

    logging.basicConfig(filename=os.path.join(logdir, "pyetenotes.log"), format='%(levelname)s > %(name)s > %(asctime)s > %(message)s', level=logging.ERROR)

    # prevent multiple instances
    if not window.acquire_lock() and "--no-lock" not in sys.argv:
        return

    if authenticate(api):
        # Initialize and show the main window
        window.init_ui()
        window.show()
        sys.exit(app.exec_())
