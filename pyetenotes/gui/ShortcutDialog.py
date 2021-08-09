from PyQt5 import QtCore, QtGui, QtWidgets
from typing import Dict
from functools import reduce

from ..__version__ import __title__
from ..settings import Settings
from ..utils import center_widget
from pyetenotes.settings.default_settings import DEFAULT_SETTINGS


settings = Settings(__title__)


class MyQKeySequenceEditWidget(QtWidgets.QKeySequenceEdit):
    def __init__(self, key: str, sequence: QtGui.QKeySequence, used_shortcuts: Dict):
        super(MyQKeySequenceEditWidget, self).__init__(sequence)
        self.key = key
        self.used_shortcuts = used_shortcuts

    def editingFinished_callback(self):
        # Update the setting, if the key sequence isn't already being used
        new_sequence = self.keySequence().toString()
        sequence_is_used = reduce(
            lambda x, y: x or (y != self and y.keySequence().toString() == new_sequence),
            self.used_shortcuts,
            False
        )

        if not sequence_is_used:
            # Store the new sequence
            settings.setValue(self.key, new_sequence)
            self.used_shortcuts[self] = new_sequence
        else:
            # Restore the previous key sequence
            self.setKeySequence(settings.value(self.key, type=str))


class ShortcutsWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QMainWindow):
        super(ShortcutsWidget, self).__init__()

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.formLayout_shortcuts = QtWidgets.QFormLayout(self)
        self.formLayout_edit_shortcuts = QtWidgets.QFormLayout()

        self.frame1 = QtWidgets.QFrame()
        self.frame2 = QtWidgets.QFrame()
        self.frame1.setLayout(self.formLayout_shortcuts)
        self.frame2.setLayout(self.formLayout_edit_shortcuts)

        self.add_shortcut_widgets()

        vline = QtWidgets.QFrame()
        vline.setFrameShape(QtWidgets.QFrame.VLine)
        vline.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.gridLayout.addWidget(self.frame1, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.frame2, 0, 2, 1, 1)
        self.gridLayout.addWidget(vline, 0, 1, 1, 1)

        center_widget(parent, self)

    def add_shortcut_widgets(self):
        shortcuts = filter(lambda x: "shortcuts/" in x, DEFAULT_SETTINGS.keys())
        self.used_shortcuts = {}
        count = 0
        for i, s in enumerate(shortcuts):
            text = s.split("/")[1].replace("_", " ").title()
            label = QtWidgets.QLabel(f"{text:30s}")
            self.formLayout_shortcuts.setWidget(i, QtWidgets.QFormLayout.LabelRole, label)

            key_str = settings.value(s, type=str)
            key = QtGui.QKeySequence.fromString(key_str)

            keySequenceEdit = MyQKeySequenceEditWidget(s, key, self.used_shortcuts)
            keySequenceEdit.setMinimumWidth(100)
            keySequenceEdit.editingFinished.connect(keySequenceEdit.editingFinished_callback)

            self.used_shortcuts[keySequenceEdit] = key_str

            self.formLayout_shortcuts.setWidget(i, QtWidgets.QFormLayout.FieldRole, keySequenceEdit)
            count += 1

        # Add edit shortcuts (which are not to be modified)
        edit_shortcuts = [
            ("Bold", "Ctrl+B"),
            ("Italics", "Ctrl+I"),
            ("Underline", "Ctrl+U"),
            ("Strikethrough", "Ctrl+K"),
            ("Newline below", "Ctrl+Return"),
            ("Newline above", "Ctrl+Shift+Return"),
            ("Move line up", "Alt+Up"),
            ("Move line down", "Alt+Down"),
            ("Indent", "Tab"),
            ("Dedent", "Shift+Tab"),
            ("Toggle checkbox", "Ctrl+/"),
            ("Duplicate", "Ctrl+D"),
        ]
        for i, s in enumerate(edit_shortcuts):
            label = QtWidgets.QLabel(f"{s[0]:30s}")
            self.formLayout_edit_shortcuts.setWidget(count+i, QtWidgets.QFormLayout.LabelRole, label)
            keySequenceEdit = QtWidgets.QKeySequenceEdit(QtGui.QKeySequence.fromString(s[1]))
            keySequenceEdit.setMinimumWidth(100)
            keySequenceEdit.setDisabled(True)
            self.used_shortcuts[keySequenceEdit] = s[1]

            self.formLayout_edit_shortcuts.setWidget(count+i, QtWidgets.QFormLayout.FieldRole, keySequenceEdit)

    def restore_defaults(self):
        response = QtWidgets.QMessageBox.warning(
            self,
            "Are you sure?",
            "Reset all shortcuts to their default values?",
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
            defaultButton=QtWidgets.QMessageBox.Cancel
        )
        if response != QtWidgets.QMessageBox.Ok:
            return

        for row in range(self.formLayout_shortcuts.rowCount()):
            label: QtWidgets.QLabel = self.formLayout_shortcuts.itemAt(row, QtWidgets.QFormLayout.LabelRole).widget()
            keyseq_edit: MyQKeySequenceEditWidget = self.formLayout_shortcuts.itemAt(row, QtWidgets.QFormLayout.FieldRole).widget()

            key = "shortcuts/" + label.text().strip().lower().replace(" ", "_")
            if keySequence := DEFAULT_SETTINGS.get(key):
                keyseq_edit.setKeySequence(keySequence)
                settings.setValue(key, keySequence)


class ShortcutsDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QMainWindow):
        super(ShortcutsDialog, self).__init__()

        self.shortcuts_widget = ShortcutsWidget(self)

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.addWidget(self.shortcuts_widget)
        self.pb_restore_defaults = QtWidgets.QPushButton("Restore defaults")
        self.gridLayout.addWidget(self.pb_restore_defaults)

        self.setWindowTitle("Keyboard Shortcuts")
        center_widget(parent, self)
        self.pb_restore_defaults.setFocus()

        self.link_callbacks()

    def link_callbacks(self):
        self.pb_restore_defaults.clicked.connect(self.shortcuts_widget.restore_defaults)
